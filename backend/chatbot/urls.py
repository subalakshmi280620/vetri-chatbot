from django.urls import path

from .views import chat, conversation_detail, conversation_list, message_feedback, submit_enquiry

urlpatterns = [
    path("chat/", chat, name="chat"),
    path("enquiries/", submit_enquiry, name="submit-enquiry"),
    path("messages/feedback/", message_feedback, name="message-feedback"),
    path("conversations/", conversation_list, name="conversation-list"),
    path(
        "conversations/<str:conversation_id>/",
        conversation_detail,
        name="conversation-detail",
    ),
]
