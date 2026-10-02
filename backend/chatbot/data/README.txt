Add .txt or .md files here for RAG (course notes, FAQs, question banks).
The chatbot retrieves the most relevant chunks and sends them to Gemini.

Vector RAG (PostgreSQL / Render):
  - knowledge.py facts are exported automatically at index time.
  - vis_website.md is indexed.
  - vetrifresh.md is EXCLUDED until verified (conflicts with knowledge.py).
  - Re-index only when content changes:
      python manage.py index_knowledge
  - Force re-index:
      python manage.py index_knowledge --force

Local SQLite uses lexical (keyword) RAG fallback — no index command needed.

PDF support is not enabled yet; paste text from PDFs into a .md file.

VERIFIED FACTS CHECKLIST (Coach AI must match exactly)
============================================================
Update vis_website.md and knowledge.py when the VIS website changes.

Must be exact:
  - Company: Vetri IT Systems (VIS)
  - Phone: +91 84381 54827
  - Email: support@vetri-it.com
  - Address: Vetri Academy, Aerial Complex, Behind Bus Stand, Surandai
  - Course duration: 180 days
  - Course eligibility: Any degree completion (UG/PG)
  - Product list: Vetri Bills, Vetri Files, Vetri Project Management,
    Coach AI, Vetri AI Assistant, Vetri CRM, Vetri Training Management System

Never invent in chat replies:
  - Exact prices (₹ / Rs amounts)
  - Client names or case studies not in these files
  - Features or services not on the official VIS website
  - Job placement or salary guarantees

For pricing questions: direct users to quotation form or support@vetri-it.com
