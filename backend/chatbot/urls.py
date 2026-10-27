from django.urls import path

from .views import chat, conversation_detail, conversation_list, message_feedback, public_content, submit_enquiry, track_visit, auth_status, auth_register, auth_login, auth_logout

urlpatterns = [
    path("auth/status/", auth_status, name="auth-status"),
    path("auth/register/", auth_register, name="auth-register"),
    path("auth/login/", auth_login, name="auth-login"),
    path("auth/logout/", auth_logout, name="auth-logout"),
    path("analytics/visit/", track_visit, name="track-visit"),
    path("public-content/", public_content, name="public-content"),
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
