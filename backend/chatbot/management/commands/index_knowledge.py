from django.core.management.base import BaseCommand

from chatbot.vector_rag import index_knowledge, is_postgresql


class Command(BaseCommand):
    help = (
        "Index VIS knowledge for vector RAG (PostgreSQL only). "
        "Re-embeds only when content hash changes unless --force is passed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-index even when content hash is unchanged",
        )

    def handle(self, *args, **options):
        if not is_postgresql():
            self.stdout.write(
                self.style.WARNING(
                    "Skipped: vector indexing requires PostgreSQL. "
                    "Local SQLite uses lexical RAG fallback."
                )
            )
            return

        result = index_knowledge(force=options["force"])
        status = result.get("status")
        if status == "indexed":
            self.stdout.write(
                self.style.SUCCESS(
                    f"Indexed {result['chunk_count']} chunks "
                    f"(hash {result['content_hash'][:12]}…)"
                )
            )
        elif status == "unchanged":
            self.stdout.write(
                self.style.SUCCESS(
                    f"Knowledge unchanged — {result['chunk_count']} chunks "
                    f"(hash {result['content_hash'][:12]}…). No re-index needed."
                )
            )
        elif status == "skipped":
            self.stdout.write(self.style.WARNING(f"Skipped: {result.get('reason')}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed: {result.get('reason')}"))
