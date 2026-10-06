"""Leads dashboard — filters, counts, and status updates for existing Enquiry records."""

from __future__ import annotations

from datetime import datetime

from django.db.models import Count, Q

from .models import Enquiry

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
    queryset = Enquiry.objects.select_related("conversation").all()

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
        "query_string": build_leads_query_string(filters),
    }
