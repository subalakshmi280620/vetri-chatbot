import json
import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from .eligibility import handle_eligibility
from .knowledge import COURSES, PRODUCTS, SERVICES, get_structured_reply
from .throttles import ChatRateThrottle
from .views import generate_reply

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
        self.assertIn("General Eligibility", reply)
        self.assertNotIn("Java Fullstack", reply)

    def test_general_eligibility_questions(self):
        for message in (
            "What are the eligibility requirements?",
            "Who can apply?",
            "What qualification is required?",
        ):
            reply = handle_eligibility(message)
            self.assertIn("General Eligibility", reply)
            self.assertNotIn("Java Fullstack", reply)

    def test_am_i_eligible_returns_general_information(self):
        reply = handle_eligibility("Am I eligible?", self.JAVA_HISTORY)
        self.assertIn("General Eligibility", reply)
        self.assertNotIn("Java Fullstack", reply)

    def test_course_specific_eligibility_when_course_named(self):
        reply = handle_eligibility("What is the eligibility for Python Fullstack?")
        self.assertIn("Eligibility Requirements — Python Fullstack", reply)
        self.assertNotIn("General Eligibility", reply)

    def test_eligibility_assessment_flow_still_works(self):
        first = handle_eligibility("Am I eligible?")
        second = handle_eligibility(
            "B.Tech",
            [
                {"role": "user", "text": "Am I eligible?"},
                {"role": "bot", "text": first},
            ],
        )
        self.assertIn("Please select the course", second)

        third = handle_eligibility(
            "Java Fullstack",
            [
                {"role": "user", "text": "Am I eligible?"},
                {"role": "bot", "text": first},
                {"role": "user", "text": "B.Tech"},
                {"role": "bot", "text": second},
            ],
        )
        self.assertIn("Outcome: ELIGIBLE", third)
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

    def test_fees_after_eligibility_outcome_uses_kb_not_eligibility(self):
        history = self._eligibility_conversation_history()
        self.assertIsNone(handle_eligibility("what are the fees?", history))
        reply, source = generate_reply("what are the fees?", history)
        self.assertIn("Pricing & Quotation", reply)
        self.assertNotIn("Outcome: ELIGIBLE", reply)
        self.assertEqual(source, "verified_kb")

    def test_apply_after_eligibility_outcome_uses_kb_not_eligibility(self):
        history = self._eligibility_conversation_history()
        self.assertIsNone(handle_eligibility("How do I apply for a course?", history))
        reply, source = generate_reply("How do I apply for a course?", history)
        self.assertIn("How to Apply", reply)
        self.assertNotIn("Outcome: ELIGIBLE", reply)
        self.assertEqual(source, "verified_kb")

    def test_qualification_not_parsed_from_bot_general_eligibility_text(self):
        first = handle_eligibility("What are the eligibility requirements?")
        second = handle_eligibility(
            "i am B.E graduate and i am interested in pythonfull stack",
            [
                {"role": "user", "text": "What are the eligibility requirements?"},
                {"role": "bot", "text": first},
            ],
        )
        self.assertIn("Outcome: ELIGIBLE", second)
        self.assertNotIn("General Eligibility", second.split("Qualification provided:", 1)[-1])


class KnowledgeReplyTests(TestCase):
    def test_courses_list_includes_all_programmes(self):
        reply = get_structured_reply("Which courses are available?")
        for course in COURSES:
            self.assertIn(course, reply)

    def test_fee_reply_points_to_quotation_contact(self):
        reply = get_structured_reply("What are the fees?")
        self.assertIn("Pricing & Quotation", reply)
        self.assertIn("support@vetri-it.com", reply)
        self.assertNotIn("register for free", reply.lower())

    def test_generate_reply_general_eligibility_via_api_path(self):
        history = [
            {"role": "user", "text": "Tell me about Java Fullstack"},
            {"role": "bot", "text": "Course Overview — Java Fullstack"},
        ]
        reply, source = generate_reply("What is the eligibility?", history)
        self.assertIn("General Eligibility", reply)
        self.assertNotIn("Java Fullstack", reply)
        self.assertEqual(source, "eligibility")

    def test_products_reply_lists_all_vis_products(self):
        reply = get_structured_reply("What products does VIS offer?")
        for product in PRODUCTS:
            self.assertIn(product, reply)

    def test_services_reply_lists_all_vis_services(self):
        reply = get_structured_reply("What services does VIS provide?")
        for service in SERVICES:
            self.assertIn(service, reply)

    def test_portfolio_reply_points_to_contact(self):
        reply = get_structured_reply("Show me your portfolio")
        self.assertIn("Portfolio", reply)
        self.assertIn("support@vetri-it.com", reply)

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

    def test_digital_marketing_course_still_returns_course_when_in_course_context(self):
        reply = get_structured_reply("Tell me about Digital Marketing course")
        self.assertIn("Course Overview", reply)
        self.assertIn("Digital Marketing", reply)


class ChatAdvancedFeatureTests(ChatApiTestCase):
    def test_chat_returns_source_and_suggestions(self):
        response = self._post_chat("What courses are available?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["source"], "verified_kb")
        self.assertIn("message_id", data)
        self.assertGreaterEqual(len(data["suggestions"]), 1)

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
