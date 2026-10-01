import base64
import json
import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from .eligibility import handle_eligibility
from .knowledge import (
    COURSES,
    PRODUCTS,
    SERVICES,
    SHORT_GREETING_REPLY,
    get_conversational_fallback,
    get_grounding_facts,
    get_structured_reply,
)
from .models import Enquiry
from .throttles import ChatRateThrottle
from .attachments import build_user_message_with_attachments, parse_attachments
from .verified_facts import enforce_verified_facts, get_verified_facts_prompt
from .gemini import GeminiAPIError, ask_gemini
from .views import (
    SOURCE_ELIGIBILITY,
    SOURCE_UNVERIFIED,
    SOURCE_VERIFIED_KB,
    build_prompt,
    generate_reply,
)

CLIENT_A = str(uuid.uuid4())
CLIENT_B = str(uuid.uuid4())


class ChatApiTestCase(TestCase):
    def _post_chat(self, message: str, client_token: str = CLIENT_A, conversation_id=None):
        payload = {"message": message, "client_token": client_token}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        return self.client.post(
            "/api/chatbot/chat/",
            data=json.dumps(payload),
            content_type="application/json",
        )


class AttachmentTests(TestCase):
    def test_parse_text_document_attachment(self):
        content = base64.b64encode(b"Python Fullstack course details").decode("ascii")
        processed = parse_attachments(
            [{
                "name": "course.txt",
                "mime_type": "text/plain",
                "type": "document",
                "data": content,
            }],
            max_count=3,
            max_bytes=1024 * 1024,
            max_document_chars=5000,
        )
        self.assertIn("Python Fullstack", processed.document_text)
        self.assertEqual(processed.display_labels, ["course.txt"])

    def test_build_user_message_includes_document_text(self):
        processed = parse_attachments(
            [{
                "name": "notes.txt",
                "mime_type": "text/plain",
                "type": "document",
                "data": base64.b64encode(b"Vetri Bills GST billing").decode("ascii"),
            }],
            max_count=3,
            max_bytes=1024 * 1024,
            max_document_chars=5000,
        )
        message = build_user_message_with_attachments(
            "What product is mentioned here?",
            processed,
        )
        self.assertIn("Vetri Bills", message)
        self.assertIn("What product is mentioned here?", message)

    @override_settings(GEMINI_API_KEY="test-key", DEEPSEEK_API_KEY="")
    @patch("chatbot.views.ask_gemini", return_value="I can see Vetri Bills in the image.")
    def test_chat_accepts_image_attachment(self, mock_gemini):
        image_bytes = base64.b64encode(b"fake-image-bytes").decode("ascii")
        response = self.client.post(
            "/api/chatbot/chat/",
            data=json.dumps({
                "message": "What is in this image?",
                "client_token": CLIENT_A,
                "attachments": [{
                    "name": "screenshot.png",
                    "mime_type": "image/png",
                    "type": "image",
                    "data": image_bytes,
                }],
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Vetri Bills", response.json()["reply"])
        self.assertTrue(mock_gemini.called)
        self.assertTrue(mock_gemini.call_args.kwargs.get("images"))


class VerifiedFactsTests(TestCase):
    def test_verified_facts_prompt_lists_contact_and_never_invent_rules(self):
        prompt = get_verified_facts_prompt()
        self.assertIn("84381 54827", prompt)
        self.assertIn("support@vetri-it.com", prompt)
        self.assertIn("Never invent", prompt)
        self.assertIn("180 days", prompt)

    def test_polish_ai_reply_fixes_truncated_stats(self):
        from .verified_facts import polish_ai_reply

        polished = polish_ai_reply(
            "You can trust VIS — over 8 years delivering 15"
        )
        self.assertIn("150+ projects", polished)
        self.assertTrue(polished.endswith("."))

    def test_enforce_verified_facts_strips_invented_pricing(self):
        reply = enforce_verified_facts(
            "The Python course costs ₹25,000 per month and includes placement."
        )
        self.assertNotIn("₹25,000", reply)
        self.assertIn("support@vetri-it.com", reply)

    def test_enforce_verified_facts_leaves_clean_reply_unchanged(self):
        reply = "Vetri Bills handles GST billing. Want a demo?"
        self.assertEqual(enforce_verified_facts(reply), reply)

    def test_build_prompt_includes_verified_facts_block(self):
        prompt = build_prompt("What products does VIS offer?")
        self.assertIn("VERIFIED FACTS ONLY", prompt)
        self.assertIn("Vetri Bills", prompt)


class ChatMessageLengthTests(ChatApiTestCase):
    def test_message_under_limit_succeeds(self):
        response = self._post_chat("What courses are available?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reply", data)
        self.assertIn("conversation_id", data)

    def test_message_at_limit_succeeds(self):
        response = self._post_chat("a" * 2000)
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.json())

    def test_message_over_limit_rejected(self):
        response = self._post_chat("a" * 2001)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("2000", data["error"])


class ChatRateLimitTests(ChatApiTestCase):
    def setUp(self):
        cache.clear()

    def _post_chat(self, message: str = "hello", ip: str = "10.0.0.1", client_token: str = CLIENT_A):
        payload = {"message": message, "client_token": client_token}
        return self.client.post(
            "/api/chatbot/chat/",
            data=json.dumps(payload),
            content_type="application/json",
            REMOTE_ADDR=ip,
        )

    @patch.object(ChatRateThrottle, "get_rate", return_value="2/minute")
    def test_requests_under_limit_succeed(self, _mock_rate):
        for index in range(2):
            response = self._post_chat(f"hello {index}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("reply", response.json())

    @patch.object(ChatRateThrottle, "get_rate", return_value="2/minute")
    def test_requests_over_limit_rejected(self, _mock_rate):
        for index in range(2):
            self._post_chat(f"hello {index}")

        response = self._post_chat("one more")
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("Too many chat requests", data["error"])


class ConversationPrivacyTests(ChatApiTestCase):
    def test_chat_requires_client_token(self):
        response = self.client.post(
            "/api/chatbot/chat/",
            data=json.dumps({"message": "hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("client_token", response.json()["error"])

    def test_client_cannot_access_other_clients_conversation_detail(self):
        create_response = self._post_chat("hello from client A", CLIENT_A)
        conversation_id = create_response.json()["conversation_id"]

        response = self.client.get(
            f"/api/chatbot/conversations/{conversation_id}/?client_token={CLIENT_B}"
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response.json())

    def test_client_cannot_send_to_other_clients_conversation(self):
        create_response = self._post_chat("hello from client A", CLIENT_A)
        conversation_id = create_response.json()["conversation_id"]

        response = self._post_chat(
            "intruder message",
            CLIENT_B,
            conversation_id=conversation_id,
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response.json())

    def test_conversation_list_only_shows_own_conversations(self):
        self._post_chat("message from A", CLIENT_A)
        self._post_chat("message from B", CLIENT_B)

        list_a = self.client.get(f"/api/chatbot/conversations/?client_token={CLIENT_A}")
        list_b = self.client.get(f"/api/chatbot/conversations/?client_token={CLIENT_B}")

        self.assertEqual(list_a.status_code, 200)
        self.assertEqual(list_b.status_code, 200)

        ids_a = {item["id"] for item in list_a.json()["conversations"]}
        ids_b = {item["id"] for item in list_b.json()["conversations"]}

        self.assertEqual(len(ids_a), 1)
        self.assertEqual(len(ids_b), 1)
        self.assertNotEqual(ids_a, ids_b)

    def test_conversation_list_title_uses_latest_user_message(self):
        first = self._post_chat("What are the eligibility requirements?", CLIENT_A)
        conversation_id = first.json()["conversation_id"]
        self._post_chat("What are the fees?", CLIENT_A, conversation_id=conversation_id)

        response = self.client.get(f"/api/chatbot/conversations/?client_token={CLIENT_A}")
        self.assertEqual(response.status_code, 200)
        item = response.json()["conversations"][0]
        self.assertIn("fees", item["title"].lower())
        self.assertIn("eligibility", item["first_question"].lower())
        self.assertGreaterEqual(item["question_count"], 2)

    def test_multiple_chats_appear_in_history(self):
        first = self._post_chat("First chat question", CLIENT_A)
        second = self._post_chat("Second chat question", CLIENT_A)
        self.assertNotEqual(
            first.json()["conversation_id"],
            second.json()["conversation_id"],
        )

        response = self.client.get(f"/api/chatbot/conversations/?client_token={CLIENT_A}")
        titles = [item["title"] for item in response.json()["conversations"]]
        self.assertEqual(len(titles), 2)

    def test_client_can_delete_own_conversation(self):
        create_response = self._post_chat("Delete me", CLIENT_A)
        conversation_id = create_response.json()["conversation_id"]

        delete_response = self.client.delete(
            f"/api/chatbot/conversations/{conversation_id}/?client_token={CLIENT_A}"
        )
        self.assertEqual(delete_response.status_code, 204)

        detail_response = self.client.get(
            f"/api/chatbot/conversations/{conversation_id}/?client_token={CLIENT_A}"
        )
        self.assertEqual(detail_response.status_code, 404)


class EligibilityReplyTests(TestCase):
    JAVA_HISTORY = [
        {"role": "user", "text": "Tell me about Java Fullstack"},
        {"role": "bot", "text": "Course Overview — Java Fullstack"},
    ]

    def test_general_eligibility_ignores_prior_course_in_history(self):
        reply = handle_eligibility("What is the eligibility?", self.JAVA_HISTORY)
        self.assertIn("degree", reply.lower())
        self.assertNotIn("Java Fullstack", reply)

    def test_general_eligibility_questions(self):
        for message in (
            "What are the eligibility requirements?",
            "Who can apply?",
            "What qualification is required?",
        ):
            reply = handle_eligibility(message)
            self.assertIn("degree", reply.lower())
            self.assertNotIn("Java Fullstack", reply)

    def test_am_i_eligible_returns_general_information(self):
        reply = handle_eligibility("Am I eligible?", self.JAVA_HISTORY)
        self.assertIn("qualification", reply.lower())
        self.assertNotIn("Java Fullstack", reply)

    def test_course_specific_eligibility_when_course_named(self):
        reply = handle_eligibility("What is the eligibility for Python Fullstack?")
        self.assertIn("Python Fullstack", reply)
        self.assertIn("degree", reply.lower())

    def test_eligibility_assessment_flow_still_works(self):
        first = handle_eligibility("Am I eligible?")
        second = handle_eligibility(
            "B.Tech",
            [
                {"role": "user", "text": "Am I eligible?"},
                {"role": "bot", "text": first},
            ],
        )
        self.assertIn("which course", second.lower())

        third = handle_eligibility(
            "Java Fullstack",
            [
                {"role": "user", "text": "Am I eligible?"},
                {"role": "bot", "text": first},
                {"role": "user", "text": "B.Tech"},
                {"role": "bot", "text": second},
            ],
        )
        self.assertIn("you meet the requirement", third.lower())
        self.assertIn("Java Fullstack", third)

    def _eligibility_conversation_history(self):
        first = handle_eligibility("What are the eligibility requirements?")
        second = handle_eligibility(
            "i am B.E graduate and i am interested in pythonfull stack",
            [
                {"role": "user", "text": "What are the eligibility requirements?"},
                {"role": "bot", "text": first},
            ],
        )
        return [
            {"role": "user", "text": "What are the eligibility requirements?"},
            {"role": "bot", "text": first},
            {"role": "user", "text": "i am B.E graduate and i am interested in pythonfull stack"},
            {"role": "bot", "text": second},
        ]

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_fees_after_eligibility_outcome_uses_kb_not_eligibility(self):
        history = self._eligibility_conversation_history()
        self.assertIsNone(handle_eligibility("what are the fees?", history))
        reply, source = generate_reply("what are the fees?", history)
        self.assertIn("fee", reply.lower())
        self.assertNotIn("Outcome: ELIGIBLE", reply)
        self.assertEqual(source, SOURCE_VERIFIED_KB)

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_apply_after_eligibility_outcome_uses_kb_not_eligibility(self):
        history = self._eligibility_conversation_history()
        self.assertIsNone(handle_eligibility("How do I apply for a course?", history))
        reply, source = generate_reply("How do I apply for a course?", history)
        self.assertIn("apply", reply.lower())
        self.assertNotIn("Outcome: ELIGIBLE", reply)
        self.assertEqual(source, SOURCE_VERIFIED_KB)

    def test_qualification_not_parsed_from_bot_general_eligibility_text(self):
        first = handle_eligibility("What are the eligibility requirements?")
        second = handle_eligibility(
            "i am B.E graduate and i am interested in pythonfull stack",
            [
                {"role": "user", "text": "What are the eligibility requirements?"},
                {"role": "bot", "text": first},
            ],
        )
        self.assertIn("you meet the requirement", second.lower())
        self.assertIn("Python", second)


class KnowledgeReplyTests(TestCase):
    def test_courses_list_includes_all_programmes(self):
        reply = get_structured_reply("Which courses are available?")
        for course in COURSES:
            self.assertIn(course, reply)

    def test_fee_reply_points_to_quotation_contact(self):
        reply = get_structured_reply("What are the fees?")
        self.assertIn("Pricing & Quotation", reply)
        self.assertIn("Enquiry", reply)
        self.assertNotIn("register for free", reply.lower())

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_greeting_reply_is_short(self):
        for message in ("hi", "hii", "hello", "good morning"):
            reply, source = generate_reply(message)
            self.assertEqual(reply, SHORT_GREETING_REPLY)
            self.assertEqual(source, "ai")
            self.assertNotIn("Vetri Bills", reply)
            self.assertNotIn("products", reply.lower())

    @override_settings(GEMINI_API_KEY="test-key", DEEPSEEK_API_KEY="")
    @patch("chatbot.views.ask_gemini", return_value="Long AI greeting with products and services.")
    def test_greeting_skips_ai(self, mock_gemini):
        reply, source = generate_reply("hii")
        self.assertEqual(reply, SHORT_GREETING_REPLY)
        mock_gemini.assert_not_called()

    def test_structured_greeting_is_short(self):
        reply = get_structured_reply("hello")
        self.assertEqual(reply, SHORT_GREETING_REPLY)

    def test_conversational_greeting_is_short(self):
        reply = get_conversational_fallback("hey")
        self.assertEqual(reply, SHORT_GREETING_REPLY)

    def test_about_and_why_vis_grounding_facts_differ(self):
        about = get_grounding_facts("What is VIS?")
        why = get_grounding_facts("Why should I choose VIS?")
        self.assertIn("Vetri IT Systems", about)
        self.assertIn("track record", why.lower())
        self.assertNotEqual(about, why)

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_about_and_why_vis_fallback_replies_differ(self):
        about = get_conversational_fallback("What is Vetri IT Systems?")
        why = get_conversational_fallback("Why should I choose VIS?")
        self.assertIn("Tamil Nadu", about)
        self.assertIn("choose VIS", why)
        self.assertNotEqual(about.lower(), why.lower())

    def test_structured_about_and_why_vis_replies_differ(self):
        about = get_structured_reply("What is VIS?")
        why = get_structured_reply("Why choose VIS?")
        self.assertIn("About", about)
        self.assertIn("Why VIS", why)
        self.assertNotEqual(about, why)

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_generate_reply_general_eligibility_via_api_path(self):
        history = [
            {"role": "user", "text": "Tell me about Java Fullstack"},
            {"role": "bot", "text": "Course Overview — Java Fullstack"},
        ]
        reply, source = generate_reply("What is the eligibility?", history)
        self.assertIn("degree", reply.lower())
        self.assertNotIn("Java Fullstack", reply)
        self.assertEqual(source, SOURCE_ELIGIBILITY)

    @override_settings(GEMINI_API_KEY="test-key", DEEPSEEK_API_KEY="")
    @patch("chatbot.views.ask_gemini", return_value="Vetri Bills is our GST billing product.")
    def test_generate_reply_prefers_ai_for_natural_answers(self, mock_gemini):
        reply, source = generate_reply("Tell me about Vetri Bills")
        self.assertEqual(source, "ai")
        self.assertIn("Vetri Bills", reply)
        mock_gemini.assert_called_once()

    def test_products_reply_lists_all_vis_products(self):
        reply = get_structured_reply("What products does VIS offer?")
        for product in PRODUCTS:
            self.assertIn(product, reply)

    def test_services_reply_lists_all_vis_services(self):
        reply = get_structured_reply("What services does VIS provide?")
        for service in SERVICES:
            self.assertIn(service, reply)

    def test_portfolio_reply_lists_featured_projects(self):
        reply = get_structured_reply("Show me your portfolio")
        self.assertIn("Featured Projects", reply)
        self.assertIn("Retail POS System", reply)
        self.assertIn("Healthcare Portal", reply)
        self.assertIn("150+", reply)

    def test_vetri_bills_product_detail(self):
        reply = get_structured_reply("Tell me about Vetri Bills")
        self.assertIn("Vetri Bills", reply)
        self.assertIn("GST", reply)

    def test_mission_vision_reply(self):
        reply = get_structured_reply("What is your mission and vision?")
        self.assertIn("Mission & Vision", reply)
        self.assertIn("AI-Powered Business For Everyone", reply)

    def test_contact_has_new_details(self):
        reply = get_structured_reply("How can I contact you?")
        self.assertIn("84381 54827", reply)
        self.assertIn("support@vetri-it.com", reply)
        self.assertIn("Surandai", reply)

    def test_quotation_and_consultation_have_distinct_replies(self):
        quote = get_structured_reply("How can I get a quotation?")
        consult = get_structured_reply("I want to book a consultation")
        self.assertIn("Get Quotation", quote)
        self.assertIn("tailored proposal", quote.lower())
        self.assertIn("Book a Consultation", consult)
        self.assertIn("solution consultant", consult.lower())
        self.assertNotEqual(quote, consult)

    def test_product_demo_has_distinct_reply(self):
        reply = get_structured_reply("I want to request a product demo")
        self.assertIn("Request a Product Demo", reply)
        self.assertIn("live workflow", reply.lower())

    def test_digital_marketing_course_still_returns_course_when_in_course_context(self):
        reply = get_structured_reply("Tell me about Digital Marketing course")
        self.assertIn("Course Overview", reply)
        self.assertIn("Digital Marketing", reply)

    def test_conversational_fallback_products_is_short(self):
        reply = get_conversational_fallback("What products does VIS offer?")
        self.assertIn("Vetri Bills", reply)
        self.assertNotIn("Our Products —", reply)
        self.assertLess(len(reply), 400)

    def test_conversational_fallback_answers_not_only_contact(self):
        reply = get_conversational_fallback("Tell me about Vetri Bills")
        self.assertIn("GST", reply)
        self.assertNotIn("reach our team", reply.lower())

    def test_grounding_facts_returns_product_knowledge(self):
        from .knowledge import get_grounding_facts

        facts = get_grounding_facts("Tell me about Vetri CRM")
        self.assertIn("CRM", facts)
        self.assertNotIn("contact our team", facts.lower())

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_generate_reply_uses_conversational_fallback_when_ai_unavailable(self):
        reply, source = generate_reply("What products does VIS offer?")
        self.assertEqual(source, SOURCE_VERIFIED_KB)
        self.assertIn("Vetri Bills", reply)
        self.assertNotIn("Our Products —", reply)


class EnquiryApiTests(ChatApiTestCase):
    def _post_enquiry(self, payload, client_token: str = CLIENT_A):
        return self.client.post(
            "/api/chatbot/enquiries/",
            data=json.dumps({**payload, "client_token": client_token}),
            content_type="application/json",
        )

    def test_submit_quotation_enquiry(self):
        response = self._post_enquiry({
            "enquiry_type": "quotation",
            "full_name": "Test User",
            "email": "test@example.com",
            "message": "Need pricing for Vetri Bills",
            "interest": "Vetri Bills",
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["enquiry_type"], "quotation")
        self.assertIn("Enquiry Submitted", data["confirmation"])
        self.assertEqual(Enquiry.objects.count(), 1)

    def test_submit_consultation_enquiry_has_distinct_confirmation(self):
        quote = self._post_enquiry({
            "enquiry_type": "quotation",
            "full_name": "Quote User",
            "email": "quote@example.com",
            "interest": "Vetri Bills",
            "message": "Need a quote",
        }).json()["confirmation"]
        consult = self._post_enquiry({
            "enquiry_type": "consultation",
            "full_name": "Consult User",
            "email": "consult@example.com",
            "message": "Need a consultation",
        }).json()["confirmation"]
        self.assertIn("Get Quotation", quote)
        self.assertIn("Book a Consultation", consult)
        self.assertNotEqual(quote, consult)

    def test_enquiry_requires_email_and_message(self):
        response = self._post_enquiry({
            "enquiry_type": "demo",
            "full_name": "Test User",
            "message": "",
        })
        self.assertEqual(response.status_code, 400)

    def test_demo_enquiry_requires_product_selection(self):
        response = self._post_enquiry({
            "enquiry_type": "demo",
            "full_name": "Demo User",
            "email": "demo@example.com",
            "message": "Show me workflows",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("product", response.json()["error"].lower())

    def test_quotation_enquiry_requires_interest(self):
        response = self._post_enquiry({
            "enquiry_type": "quotation",
            "full_name": "Quote User",
            "email": "quote@example.com",
            "message": "Need pricing",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("quotation", response.json()["error"].lower())

    @override_settings(
        RESEND_API_KEY="",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        ENQUIRY_NOTIFY_EMAIL="notify@vetri-it.com",
        DEFAULT_FROM_EMAIL="Coach AI <noreply@vetri-it.com>",
    )
    def test_enquiry_sends_notification_email(self):
        from django.core import mail

        response = self._post_enquiry({
            "enquiry_type": "quotation",
            "full_name": "Email Test",
            "email": "customer@example.com",
            "phone": "+91 84381 54827",
            "interest": "Vetri Bills",
            "message": "Please send pricing",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["email_queued"])
        import time
        time.sleep(0.2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Coach AI enquiry", mail.outbox[0].subject)
        self.assertIn("Email Test", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["notify@vetri-it.com"])

    @override_settings(
        RESEND_API_KEY="re_test_key",
        RESEND_FROM_EMAIL="Coach AI <onboarding@resend.dev>",
        ENQUIRY_NOTIFY_EMAIL="notify@vetri-it.com",
    )
    def test_enquiry_sends_notification_via_resend(self):
        from unittest.mock import patch

        with patch("resend.Emails.send", return_value={"id": "email_123"}) as mock_send:
            response = self._post_enquiry({
                "enquiry_type": "quotation",
                "full_name": "Resend Test",
                "email": "customer@example.com",
                "interest": "Vetri Bills",
                "message": "Please send pricing",
            })
            self.assertEqual(response.status_code, 200)
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            self.assertEqual(payload["to"], ["notify@vetri-it.com"])
            self.assertIn("Resend Test", payload["text"])
            self.assertEqual(payload["from"], "Coach AI <onboarding@resend.dev>")


class ChatAdvancedFeatureTests(ChatApiTestCase):
    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_chat_returns_source_and_suggestions(self):
        response = self._post_chat("What courses are available?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["source"], SOURCE_VERIFIED_KB)
        self.assertNotIn("Which Courses Are Available", data["reply"])
        self.assertNotIn("Course Overview —", data["reply"])
        self.assertIn("message_id", data)
        self.assertGreaterEqual(len(data["suggestions"]), 1)

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_chat_never_returns_long_faq_template(self):
        response = self._post_chat("What products does VIS offer?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["source"], SOURCE_VERIFIED_KB)
        self.assertNotIn("Our Products —", data["reply"])

    @override_settings(GEMINI_API_KEY="test-key", DEEPSEEK_API_KEY="")
    @patch("chatbot.views.ask_gemini", return_value="We offer Python, Java, UI/UX, and more.")
    def test_chat_uses_ai_when_configured(self, _mock_gemini):
        response = self._post_chat("What courses do you have?")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "ai")

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_chat_suggests_enquiry_for_quotation_intent(self):
        response = self._post_chat("How can I get a quotation?")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggest_enquiry"], "quotation")
        self.assertIn("Enquiry", response.json()["reply"])

    def test_chat_suggests_enquiry_for_demo_intent(self):
        response = self._post_chat("I want to request a product demo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggest_enquiry"], "demo")

    def test_client_can_rate_bot_message(self):
        chat_response = self._post_chat("What courses are available?", CLIENT_A)
        message_id = chat_response.json()["message_id"]

        feedback_response = self.client.post(
            "/api/chatbot/messages/feedback/",
            data=json.dumps({
                "message_id": message_id,
                "rating": "up",
                "client_token": CLIENT_A,
            }),
            content_type="application/json",
        )
        self.assertEqual(feedback_response.status_code, 200)
        self.assertEqual(feedback_response.json()["feedback"], "up")


def _reply_similarity(left: str, right: str) -> float:
    left_words = set(left.lower().split())
    right_words = set(right.lower().split())
    if not left_words or not right_words:
        return 1.0 if left.strip() == right.strip() else 0.0
    return len(left_words & right_words) / len(left_words | right_words)


class DemoQuestionCoverageTests(TestCase):
    """Ensure demo questions route to distinct, non-repeating answers."""

    DEMO_QUESTIONS = [
        ("Hi", ("how can i help",)),
        ("What is Vetri IT Systems?", ("tamil nadu", "vetri")),
        ("Why should I choose VIS?", ("choose vis", "trust")),
        ("What is your mission and vision?", ("vision", "mission")),
        ("Show your portfolio", ("retail", "project")),
        ("What products does VIS offer?", ("vetri bills",)),
        ("What services do you provide?", ("website", "mobile")),
        ("Tell me about Vetri Bills", ("gst", "billing")),
        ("What is Coach AI?", ("learning", "coach")),
        ("How can I get a quotation?", ("quotation", "enquiry")),
        ("I want a product demo", ("demo",)),
        ("Book a consultation", ("consultation",)),
        ("What courses are available?", ("python", "java")),
        ("What is the course duration?", ("180",)),
        (
            "I have B.Com and want Python Fullstack — am I eligible?",
            ("meet the requirement", "degree"),
        ),
        ("How can I contact you?", ("84381", "support@vetri-it.com")),
        ("How much does Vetri Bills cost?", ("quotation", "scope")),
    ]

    DISTINCT_PAIRS = [
        ("What is Vetri IT Systems?", "Why should I choose VIS?"),
        ("What is Vetri IT Systems?", "What is your mission and vision?"),
        ("Why should I choose VIS?", "Show your portfolio"),
        ("What products does VIS offer?", "What services do you provide?"),
        ("How can I get a quotation?", "I want a product demo"),
        ("How can I get a quotation?", "Book a consultation"),
        ("I want a product demo", "Book a consultation"),
        ("What is Vetri IT Systems?", "How can I contact you?"),
        ("Tell me about Vetri Bills", "What products does VIS offer?"),
    ]

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_demo_questions_return_expected_topics(self):
        for question, markers in self.DEMO_QUESTIONS:
            reply, source = generate_reply(question)
            lowered = reply.lower()
            self.assertTrue(
                any(marker in lowered for marker in markers),
                msg=f"{question!r} -> {reply!r}",
            )
            if question.strip().lower() == "hi":
                self.assertEqual(source, "ai")
            elif "eligible" in question.lower():
                self.assertEqual(source, SOURCE_ELIGIBILITY)
            else:
                self.assertEqual(source, SOURCE_VERIFIED_KB)

    def test_demo_fallback_replies_are_not_identical_pairs(self):
        replies = {
            question: get_conversational_fallback(question)
            for question, _ in self.DEMO_QUESTIONS
        }
        for left_q, right_q in self.DISTINCT_PAIRS:
            left = replies[left_q]
            right = replies[right_q]
            self.assertNotEqual(left, right, msg=f"{left_q} == {right_q}")
            self.assertLess(
                _reply_similarity(left, right),
                0.72,
                msg=f"Too similar:\n{left_q}: {left}\n{right_q}: {right}",
            )

    def test_grounding_facts_for_distinct_topics_differ(self):
        pairs = [
            ("What is Vetri IT Systems?", "Why should I choose VIS?"),
            ("What is your mission and vision?", "What is Vetri IT Systems?"),
            ("Show your portfolio", "Why should I choose VIS?"),
            ("What products does VIS offer?", "What services do you provide?"),
            ("How can I get a quotation?", "I want a product demo"),
            ("How can I contact you?", "What is Vetri IT Systems?"),
        ]
        for left_q, right_q in pairs:
            left = get_grounding_facts(left_q)
            right = get_grounding_facts(right_q)
            self.assertNotEqual(left, right, msg=f"{left_q} == {right_q}")
            self.assertLess(
                _reply_similarity(left, right),
                0.72,
                msg=f"Grounding too similar:\n{left_q}: {left}\n{right_q}: {right}",
            )

    @override_settings(GEMINI_API_KEY="", DEEPSEEK_API_KEY="")
    def test_greeting_stays_short_in_full_reply_flow(self):
        reply, _source = generate_reply("hii")
        self.assertEqual(reply, SHORT_GREETING_REPLY)
        self.assertNotIn("Vetri Bills", reply)

    def test_pricing_questions_do_not_invent_rupees(self):
        for question in (
            "How much does Vetri Bills cost?",
            "What is the price of Python course?",
            "How much does it cost?",
        ):
            reply = get_conversational_fallback(question)
            self.assertNotRegex(reply, r"₹\s*\d")
            self.assertNotRegex(reply.lower(), r"rs\.?\s*\d")


class GeminiRetryTests(TestCase):
    _GEMINI_SETTINGS = {
        "GEMINI_API_KEY": "test-key",
        "GEMINI_MODEL": "gemini-3.8-flash",
        "GEMINI_FALLBACK_MODELS": ["gemini-3.6-flash"],
        "DEEPSEEK_API_KEY": "",
    }

    @override_settings(**_GEMINI_SETTINGS)
    @patch("chatbot.gemini.time.sleep")
    @patch("chatbot.gemini._call_gemini_model")
    def test_503_retries_then_succeeds_on_same_model(self, mock_call, mock_sleep):
        mock_call.side_effect = [
            GeminiAPIError("Gemini HTTP 503: high demand", code=503, model="gemini-3.8-flash"),
            "Natural AI reply about Vetri Bills.",
        ]

        reply = ask_gemini("Tell me about Vetri Bills", "system prompt")

        self.assertEqual(reply, "Natural AI reply about Vetri Bills.")
        self.assertEqual(mock_call.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    @override_settings(**_GEMINI_SETTINGS)
    @patch("chatbot.gemini.time.sleep")
    @patch("chatbot.gemini._call_gemini_model")
    def test_503_exhausted_retries_use_fallback_model(self, mock_call, mock_sleep):
        unavailable = GeminiAPIError(
            "Gemini HTTP 503: high demand",
            code=503,
            model="gemini-3.8-flash",
        )
        mock_call.side_effect = [
            unavailable,
            unavailable,
            "Fallback model reply.",
        ]

        reply = ask_gemini("Why choose VIS?", "system prompt")

        self.assertEqual(reply, "Fallback model reply.")
        self.assertEqual(mock_call.call_count, 3)
        models_tried = [call.args[0] for call in mock_call.call_args_list]
        self.assertEqual(models_tried[:2], ["gemini-3.8-flash"] * 2)
        self.assertEqual(models_tried[2], "gemini-3.6-flash")

    @override_settings(**_GEMINI_SETTINGS)
    @patch("chatbot.gemini.time.sleep")
    @patch("chatbot.gemini._call_gemini_model")
    def test_429_does_not_retry_quota_exhausted_model(self, mock_call, mock_sleep):
        mock_call.side_effect = [
            GeminiAPIError("Gemini HTTP 429: quota exceeded", code=429, model="gemini-3.8-flash"),
            "Fallback model reply.",
        ]

        reply = ask_gemini("What is VIS?", "system prompt")

        self.assertEqual(reply, "Fallback model reply.")
        self.assertEqual(mock_call.call_count, 2)
        mock_sleep.assert_not_called()

    @override_settings(**_GEMINI_SETTINGS)
    @patch("chatbot.gemini.time.sleep")
    @patch("chatbot.gemini._call_gemini_model")
    def test_all_models_fail_after_retries_raises(self, mock_call, mock_sleep):
        unavailable = GeminiAPIError(
            "Gemini HTTP 503: high demand",
            code=503,
            model="gemini-3.8-flash",
        )
        mock_call.side_effect = [unavailable] * 4

        with self.assertRaises(GeminiAPIError) as ctx:
            ask_gemini("Hello", "system prompt")

        self.assertEqual(ctx.exception.code, 503)
        self.assertEqual(mock_call.call_count, 4)

    @override_settings(**{**_GEMINI_SETTINGS, "GEMINI_MAX_RETRIES": 3})
    @patch("chatbot.gemini.time.sleep")
    @patch("chatbot.gemini._call_gemini_model")
    def test_max_retries_configurable_via_settings(self, mock_call, mock_sleep):
        mock_call.side_effect = [
            GeminiAPIError("Gemini HTTP 503: high demand", code=503, model="gemini-3.8-flash"),
            GeminiAPIError("Gemini HTTP 503: high demand", code=503, model="gemini-3.8-flash"),
            "Reply after third attempt.",
        ]

        reply = ask_gemini("Hello", "system prompt")

        self.assertEqual(reply, "Reply after third attempt.")
        self.assertEqual(mock_call.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @override_settings(**_GEMINI_SETTINGS)
    @patch("chatbot.views.ask_gemini")
    def test_generate_reply_labels_verified_kb_when_ai_busy(self, mock_gemini):
        mock_gemini.side_effect = GeminiAPIError(
            "Gemini HTTP 503: high demand",
            code=503,
            model="gemini-3.8-flash",
        )

        reply, source = generate_reply("What products does VIS offer?")

        self.assertEqual(source, SOURCE_VERIFIED_KB)
        self.assertIn("temporarily unavailable", reply)
        self.assertIn("Vetri Bills", reply)
        self.assertNotIn("Our Products —", reply)

    @override_settings(**_GEMINI_SETTINGS)
    @patch("chatbot.views.ask_gemini")
    def test_generate_reply_friendly_message_when_ai_and_kb_miss(self, mock_gemini):
        mock_gemini.side_effect = GeminiAPIError(
            "Gemini HTTP 503: high demand",
            code=503,
            model="gemini-3.8-flash",
        )

        reply, source = generate_reply("xyzzy plugh totally unrelated question")

        self.assertEqual(source, SOURCE_UNVERIFIED)
        self.assertIn("trouble reaching our AI", reply)
        self.assertIn("84381", reply)
