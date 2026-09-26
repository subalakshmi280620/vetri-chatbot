from django.contrib import admin
from django.db.models import Count
from django.shortcuts import render
from django.urls import path

from .models import Conversation, Enquiry, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "text", "source", "feedback", "created_at")
    fields = ("role", "text", "source", "feedback", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "client_token", "message_count", "created_at")
    readonly_fields = ("id", "client_token", "created_at")
    inlines = (MessageInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_message_count=Count("messages"))

    @admin.display(description="Messages")
    def message_count(self, obj):
        return obj._message_count


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "source", "feedback", "preview", "created_at")
    list_filter = ("role", "source", "feedback")
    search_fields = ("text",)
    readonly_fields = ("conversation", "role", "text", "source", "feedback", "created_at")

    @admin.display(description="Text")
    def preview(self, obj):
        return obj.text[:80]


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "enquiry_type",
        "full_name",
        "email",
        "phone",
        "interest",
        "status",
        "created_at",
    )
    list_filter = ("enquiry_type", "status", "created_at")
    search_fields = ("full_name", "company", "email", "phone", "interest", "message")
    readonly_fields = ("client_token", "conversation", "created_at")
    list_editable = ("status",)
    ordering = ("-created_at",)


def analytics_view(request):
    recent_enquiries = Enquiry.objects.order_by("-created_at")[:8]
    recent_feedback = (
        Message.objects.filter(role=Message.ROLE_BOT, feedback__in=["up", "down"])
        .select_related("conversation")
        .order_by("-created_at")[:8]
    )
    stats = {
        "conversations": Conversation.objects.count(),
        "messages": Message.objects.count(),
        "user_messages": Message.objects.filter(role=Message.ROLE_USER).count(),
        "enquiries": Enquiry.objects.count(),
        "enquiries_new": Enquiry.objects.filter(status=Enquiry.STATUS_NEW).count(),
        "feedback_up": Message.objects.filter(feedback="up").count(),
        "feedback_down": Message.objects.filter(feedback="down").count(),
        "ai_replies": Message.objects.filter(role=Message.ROLE_BOT, source="ai").count(),
        "verified_replies": Message.objects.filter(
            role=Message.ROLE_BOT,
            source="verified_kb",
        ).count(),
    }
    enquiry_breakdown = (
        Enquiry.objects.values("enquiry_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    context = {
        **admin.site.each_context(request),
        "title": "Coach AI Analytics",
        "stats": stats,
        "enquiry_breakdown": enquiry_breakdown,
        "recent_enquiries": recent_enquiries,
        "recent_feedback": recent_feedback,
    }
    return render(request, "admin/chatbot/analytics.html", context)


_original_get_urls = admin.site.get_urls


def _extended_admin_urls():
    custom_urls = [
        path(
            "chatbot-analytics/",
            admin.site.admin_view(analytics_view),
            name="chatbot-analytics",
        ),
    ]
    return custom_urls + _original_get_urls()


admin.site.get_urls = _extended_admin_urls
