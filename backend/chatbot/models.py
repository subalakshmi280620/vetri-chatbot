import uuid

from django.conf import settings
from django.db import models


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_token = models.UUIDField(default=uuid.uuid4, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    ROLE_USER = "user"
    ROLE_BOT = "bot"
    ROLE_CHOICES = (
        (ROLE_USER, "User"),
        (ROLE_BOT, "Bot"),
    )

    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    source = models.CharField(max_length=20, blank=True, default="")
    feedback = models.CharField(max_length=10, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.text[:40]}"


class Enquiry(models.Model):
    TYPE_QUOTATION = "quotation"
    TYPE_CONSULTATION = "consultation"
    TYPE_DEMO = "demo"
    TYPE_SALES = "sales"
    TYPE_GENERAL = "general"
    TYPE_ENROLL = "enroll"
    TYPE_CHOICES = (
        (TYPE_QUOTATION, "Request a quotation"),
        (TYPE_CONSULTATION, "Book a consultation"),
        (TYPE_DEMO, "Request a product demo"),
        (TYPE_SALES, "Contact sales team"),
        (TYPE_ENROLL, "Enroll / connect with team"),
        (TYPE_GENERAL, "General enquiry"),
    )

    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_CLOSED, "Closed"),
    )

    enquiry_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_GENERAL)
    full_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True, default="")
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default="")
    interest = models.CharField(max_length=120, blank=True, default="")
    message = models.TextField()
    client_token = models.UUIDField(db_index=True)
    conversation = models.ForeignKey(
        Conversation,
        related_name="enquiries",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_enquiries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_enquiry_type_display()} — {self.full_name}"


class EnquiryNote(models.Model):
    enquiry = models.ForeignKey(
        Enquiry,
        related_name="notes",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="enquiry_notes",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.enquiry_id} by {self.author_id}"


class KnowledgeChunk(models.Model):
    """Indexed knowledge excerpt with Gemini embedding for vector RAG."""

    source = models.CharField(max_length=120)
    section = models.CharField(max_length=200, blank=True, default="")
    text = models.TextField()
    chunk_index = models.PositiveIntegerField(default=0)
    content_hash = models.CharField(max_length=64, db_index=True)
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["source", "chunk_index"]
        indexes = [
            models.Index(fields=["source", "chunk_index"]),
        ]

    def __str__(self):
        return f"{self.source}#{self.chunk_index}"


class KnowledgeIndexState(models.Model):
    """Tracks content hash so index_knowledge re-embeds only when sources change."""

    content_hash = models.CharField(max_length=64, unique=True)
    chunk_count = models.PositiveIntegerField(default=0)
    indexed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.chunk_count} chunks @ {self.indexed_at:%Y-%m-%d}"
