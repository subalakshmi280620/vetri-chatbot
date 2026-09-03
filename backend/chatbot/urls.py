from django.urls import path

from .views import chat, conversation_detail, conversation_list

urlpatterns = [
    path("chat/", chat, name="chat"),
    path("conversations/", conversation_list, name="conversation-list"),
    path(
        "conversations/<str:conversation_id>/",
        conversation_detail,
        name="conversation-detail",
    ),
]
