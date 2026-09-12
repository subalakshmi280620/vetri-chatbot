import json
import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from .throttles import ChatRateThrottle

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
