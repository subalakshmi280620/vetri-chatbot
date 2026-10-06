"""Coach AI analytics — aggregates existing Conversation, Message, and Enquiry data."""

from __future__ import annotations

import re
from collections import Counter
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncWeek
from django.utils import timezone

from .models import Conversation, Enquiry, Message

TOPIC_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Courses & training", (
        "course", "python", "java", "internship", "eligibility", "degree",
        "training", "padippu", "padikalam", "fullstack", "ui/ux",
    )),
    ("Products", (
        "vetri bills", "coach ai", "crm", "vetri files", "product", "billing",
        "gst", "hr management", "project management",
    )),
    ("Website & pricing", (
        "website", "quotation", "quote", "price", "cost", "evlo", "9999",
        "3000", "ecommerce", "retail shop",
    )),
    ("Contact & support", (
        "contact", "phone", "email", "call", "address", "support",
    )),
    ("Demos & enrolment", (
        "demo", "consultation", "enroll", "enquiry", "join",
    )),
    ("Company info", (
        "what is vis", "about vetri", "who are you", "portfolio", "mission",
        "vision", "why choose",
    )),
)

_SKIP_QUESTION_PREFIXES = (
    "submitted enquiry:",
    "shared attachment",
    "[attached:",
)


def _normalize_question(text: str) -> str:
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    if any(lowered.startswith(prefix) for prefix in _SKIP_QUESTION_PREFIXES):
        return ""
    if len(cleaned) < 8:
        return ""
    return cleaned[:160]


def classify_topic(text: str) -> str | None:
    lowered = text.lower()
    for label, keywords in TOPIC_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return None


def get_dashboard_stats() -> dict:
    return {
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


def get_enquiry_breakdown() -> list[dict]:
    labels = dict(Enquiry.TYPE_CHOICES)
    rows = (
        Enquiry.objects.values("enquiry_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    return [
        {
            "enquiry_type": row["enquiry_type"],
            "label": labels.get(row["enquiry_type"], row["enquiry_type"]),
            "total": row["total"],
        }
        for row in rows
    ]


def get_topic_summary(limit: int = 8) -> list[dict]:
    """Most common classified topics from user messages."""
    counts: Counter[str] = Counter()
    for text in Message.objects.filter(role=Message.ROLE_USER).values_list("text", flat=True):
        normalized = _normalize_question(text)
        if not normalized:
            continue
        topic = classify_topic(normalized)
        if topic:
            counts[topic] += 1

    return [
        {"topic": topic, "total": total}
        for topic, total in counts.most_common(limit)
    ]


def get_top_user_questions(limit: int = 8) -> list[dict]:
    """Most repeated user questions (normalized wording)."""
    counts: Counter[str] = Counter()
    for text in Message.objects.filter(role=Message.ROLE_USER).values_list("text", flat=True):
        normalized = _normalize_question(text)
        if not normalized:
            continue
        key = normalized.lower()
        key = re.sub(r"[?!.]+$", "", key).strip()
        counts[key] += 1

    return [
        {"question": question, "total": total}
        for question, total in counts.most_common(limit)
    ]


def _fill_daily_series(rows: list[dict], days: int) -> list[dict]:
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    by_date = {row["date"]: row["total"] for row in rows}
    series = []
    max_total = 0
    for offset in range(days):
        day = start + timedelta(days=offset)
        total = by_date.get(day, 0)
        max_total = max(max_total, total)
        series.append({
            "label": day.strftime("%d %b"),
            "date": day,
            "total": total,
        })
    for item in series:
        item["percent"] = int((item["total"] / max_total) * 100) if max_total else 0
    return series


def get_daily_message_counts(days: int = 7) -> list[dict]:
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    rows = (
        Message.objects.filter(created_at__date__gte=start)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(total=Count("id"))
        .order_by("date")
    )
    normalized = [{"date": row["date"], "total": row["total"]} for row in rows]
    return _fill_daily_series(normalized, days)


def get_weekly_message_counts(weeks: int = 4) -> list[dict]:
    now = timezone.now()
    start = now - timedelta(weeks=weeks)
    rows = (
        Message.objects.filter(created_at__gte=start)
        .annotate(week=TruncWeek("created_at"))
        .values("week")
        .annotate(total=Count("id"))
        .order_by("week")
    )
    series = []
    max_total = 0
    for row in rows:
        week_start = row["week"]
        if hasattr(week_start, "date"):
            week_start = week_start.date()
        total = row["total"]
        max_total = max(max_total, total)
        series.append({
            "label": week_start.strftime("%d %b"),
            "week_start": week_start,
            "total": total,
        })
    for item in series:
        item["percent"] = int((item["total"] / max_total) * 100) if max_total else 0
    return series


def build_analytics_context() -> dict:
    return {
        "stats": get_dashboard_stats(),
        "enquiry_breakdown": get_enquiry_breakdown(),
        "top_topics": get_topic_summary(),
        "top_questions": get_top_user_questions(),
        "daily_usage": get_daily_message_counts(),
        "weekly_usage": get_weekly_message_counts(),
        "recent_enquiries": Enquiry.objects.order_by("-created_at")[:8],
        "recent_feedback": (
            Message.objects.filter(role=Message.ROLE_BOT, feedback__in=["up", "down"])
            .select_related("conversation")
            .order_by("-created_at")[:8]
        ),
    }
