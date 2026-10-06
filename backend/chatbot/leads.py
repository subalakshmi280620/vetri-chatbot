"""Leads dashboard — filters, counts, and status updates for existing Enquiry records."""

from __future__ import annotations

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q

from .models import Enquiry, EnquiryNote
VALID_LEAD_STATUSES = {
    Enquiry.STATUS_NEW,
    Enquiry.STATUS_CONTACTED,
    Enquiry.STATUS_CLOSED,
}


def parse_date_param(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_filter_params(request) -> dict:
    """Read lead filter values from a GET or POST request."""
    source = request.GET if request.method == "GET" else request.POST
    return {
        "search": (source.get("q") or "").strip(),
        "enquiry_type": (source.get("enquiry_type") or "").strip(),
        "status": (source.get("status") or "").strip(),
        "date_from": parse_date_param((source.get("date_from") or "").strip()),
        "date_to": parse_date_param((source.get("date_to") or "").strip()),
    }


def filter_leads(
    search: str = "",
    enquiry_type: str = "",
    status: str = "",
    date_from=None,
    date_to=None,
):
    queryset = Enquiry.objects.select_related("conversation", "assigned_to").prefetch_related(
        Prefetch(
            "notes",
            queryset=EnquiryNote.objects.select_related("author").order_by("-created_at"),
        )
    )

    if search:
        queryset = queryset.filter(
            Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )

    allowed_types = {choice[0] for choice in Enquiry.TYPE_CHOICES}
    if enquiry_type and enquiry_type in allowed_types:
        queryset = queryset.filter(enquiry_type=enquiry_type)

    if status and status in VALID_LEAD_STATUSES:
        queryset = queryset.filter(status=status)

    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)

    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)

    return queryset.order_by("-created_at")


def get_lead_counts(queryset=None) -> dict:
    base = queryset if queryset is not None else Enquiry.objects.all()
    grouped = {
        row["status"]: row["total"]
        for row in base.values("status").annotate(total=Count("id"))
    }
    return {
        "total": base.count(),
        "new": grouped.get(Enquiry.STATUS_NEW, 0),
        "contacted": grouped.get(Enquiry.STATUS_CONTACTED, 0),
        "closed": grouped.get(Enquiry.STATUS_CLOSED, 0),
    }


def get_assignable_staff_users():
    User = get_user_model()
    return User.objects.filter(is_staff=True, is_active=True).order_by("username")


def add_lead_note(enquiry_id, text: str, author) -> EnquiryNote:
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Note text is required")
    enquiry = Enquiry.objects.get(pk=enquiry_id)
    return EnquiryNote.objects.create(enquiry=enquiry, author=author, text=cleaned)


def update_lead_assignment(enquiry_id, assigned_to_id) -> Enquiry:
    User = get_user_model()
    enquiry = Enquiry.objects.get(pk=enquiry_id)
    if assigned_to_id in (None, "", "none"):
        enquiry.assigned_to = None
    else:
        try:
            user_id = int(assigned_to_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid staff user")
        user = User.objects.get(pk=user_id)
        if not user.is_staff or not user.is_active:
            raise ValueError("Can only assign to active staff users")
        enquiry.assigned_to = user
    enquiry.save(update_fields=["assigned_to"])
    return enquiry


def update_lead_status(enquiry_id, status: str) -> Enquiry:
    if status not in VALID_LEAD_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    enquiry = Enquiry.objects.get(pk=enquiry_id)
    enquiry.status = status
    enquiry.save(update_fields=["status"])
    return enquiry


def build_leads_query_string(filters: dict) -> str:
    from urllib.parse import urlencode

    params = {}
    if filters.get("search"):
        params["q"] = filters["search"]
    if filters.get("enquiry_type"):
        params["enquiry_type"] = filters["enquiry_type"]
    if filters.get("status"):
        params["status"] = filters["status"]
    if filters.get("date_from"):
        params["date_from"] = filters["date_from"].isoformat()
    if filters.get("date_to"):
        params["date_to"] = filters["date_to"].isoformat()
    return urlencode(params)


def build_leads_context(request) -> dict:
    filters = get_filter_params(request)
    leads = filter_leads(**filters)
    return {
        "filters": filters,
        "leads": leads,
        "counts": get_lead_counts(),
        "enquiry_type_choices": Enquiry.TYPE_CHOICES,
        "status_choices": Enquiry.STATUS_CHOICES,
        "staff_users": get_assignable_staff_users(),
        "query_string": build_leads_query_string(filters),
    }
