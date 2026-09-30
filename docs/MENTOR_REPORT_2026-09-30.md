# Coach AI — Daily Progress Report
**Project:** Vetri IT Systems (VIS) Chatbot  
**Student:** _________________________  
**Date:** 30 September 2026  
**Report for:** Mentor review

---

## 1. Project Summary

**Coach AI** is the official AI assistant for Vetri IT Systems. It answers visitor questions about products, services, training courses, and company information using verified website content. It also captures business leads through an enquiry form and provides an admin panel for monitoring.

**Architecture:** Single-agent system — Gemini LLM + keyword RAG + verified knowledge base (not multi-agent).

| Layer | Technology |
|-------|------------|
| Frontend | React 19 + Vite |
| Backend | Django 6 + Django REST Framework |
| AI | Google Gemini |
| Database | PostgreSQL (Render) / SQLite (local) |
| Email | Resend API |
| Hosting | Render (free tier) |

---

## 2. Live URLs

| Resource | URL |
|----------|-----|
| Chat UI | https://vetri-chatbot-ui.onrender.com |
| Embed mode | https://vetri-chatbot-ui.onrender.com/?embed=1 |
| API | https://vetri-chatbot-1.onrender.com |
| Admin | https://vetri-chatbot-1.onrender.com/admin/ |
| Analytics | https://vetri-chatbot-1.onrender.com/admin/chatbot-analytics/ |
| Health check | https://vetri-chatbot-1.onrender.com/health/ |
| GitHub | https://github.com/subalakshmi280620/vetri-chatbot |

---

## 3. Work Completed Today (30 Sep 2026)

### A. Knowledge & AI replies
- Updated all chatbot knowledge from the **new VIS Figma website design** (stats, services, products, portfolio, courses).
- Tuned replies to **natural English** — complete answers in 2–4 short lines (not rigid FAQ templates).
- **Short greeting** for "Hi" — only *"Hello! How can I help you today?"* (no repeated product list).
- **Distinct answers** for different question types so replies do not repeat:
  - What is VIS? → company intro
  - Why choose VIS? → differentiators and track record
  - Mission & vision → vision/mission only
  - Portfolio → project examples
  - Products vs services → separate answers
  - Quotation / demo / consultation → each has its own flow
- Added **67 automated tests** including demo question coverage (all passing).

### B. Chat UI improvements
- Removed **duplicate welcome bot message** and **quick action chips** (redundant with top Enquiry button).
- Kept one **welcome card** + FAQ suggestions at bottom.
- Moved **enquiry CTA button inside the bot message bubble** (compact, not full-width).
- Shorter CTA labels: *Get quotation*, *Book consultation*, *Request demo*.
- Added **official Vetri IT logo** to chat UI, favicon, and admin header.

### C. Enquiry system
- Enquiry form saves to database and sends **email via Resend API**.
- AI routes quotation / consultation / demo questions to the **Enquiry button**.
- Admin panel: **Chatbot → Enquirys** to view all submissions.

### D. Admin panel
- **VIS-themed styling** — navy header, green buttons, clean tables.
- **Analytics dashboard** — conversations, messages, enquiries, feedback counts.
- Analytics link added to **admin home**, **header**, and **left sidebar**.
- Health endpoint shows database type (`postgresql` vs `sqlite`) for deploy verification.

### E. Documentation
- `docs/EXPECTED_USER_QUESTIONS.md` — full test question list.
- `docs/MENTOR_DEMO_SHEET.md` — printable 10-minute demo script with checkboxes.

---

## 4. Issues Found & Resolved Today

| Issue | Cause | Fix |
|-------|-------|-----|
| Enquiries show 0 in admin | `DATABASE_URL` not set on Render → SQLite wiped on restart | Guide to add PostgreSQL + `DATABASE_URL` on Render |
| Analytics hard to find | Not in admin sidebar | Added to home, header, and sidebar |
| UI still showed quick actions | Changes not pushed to Render | Pushed and redeployed frontend |
| "What is VIS" = "Why choose VIS" same answer | Shared grounding facts for AI | Separate routing and facts per question type |
| "Hi" gave long intro again | AI repeated welcome content | Short greeting bypasses AI |
| Enquiry CTA too wide | Full-width button outside bubble | Compact button inside message |

---

## 5. Features Delivered (MVP)

| Feature | Status |
|---------|--------|
| Natural AI chat (Gemini + RAG + verified KB) | Done |
| Products, services, courses, company Q&A | Done |
| Verified contact details (no invented pricing) | Done |
| Enquiry form (quotation / consultation / demo) | Done |
| Email notification on enquiry (Resend) | Done |
| Admin: Conversations, Messages, Enquirys | Done |
| Analytics dashboard | Done |
| Chat history + export | Done |
| Thumbs up/down feedback | Done |
| Voice input | Done |
| Photo / PDF upload | Done |
| Embed mode for website (`?embed=1`) | Done |
| Styled admin (navy + green) | Done |

---

## 6. Verified Facts (always exact)

| Item | Value |
|------|-------|
| Company | Vetri IT Systems (VIS) |
| Phone | +91 84381 54827 |
| Email | support@vetri-it.com |
| Address | Vetri Academy, Aerial Complex, Behind Bus Stand, Surandai |
| Course duration | 180 days |
| Eligibility | Any completed degree (UG/PG) |
| Stats | 150+ projects · 8+ years · 50+ clients · 15+ team |

---

## 7. Demo Script for Mentor (5 min)

1. Open https://vetri-chatbot-ui.onrender.com  
2. Type **Hi** → short greeting only  
3. Ask **What is Vetri IT Systems?** → company intro  
4. Ask **Why should I choose VIS?** → different answer (benefits)  
5. Ask **Tell me about Vetri Bills** → GST billing product  
6. Ask **How can I get a quotation?** → answer + **Get quotation** button in message  
7. Submit **Enquiry form** → show in admin Enquirys  
8. Open **Admin → Analytics**  

---

## 8. Pending / Action Required

| Item | Owner | Notes |
|------|-------|-------|
| Set `DATABASE_URL` on Render | Student | PostgreSQL must be linked or enquiries will not persist |
| Confirm `GEMINI_API_KEY` on Render | Student | Required for AI replies |
| Verify Resend email domain | Student | Test sender may land in spam; verify `vetri-it.com` for production |
| Embed on vetriitsystems.com | Student | Use `?embed=1` or embed.html |

---

## 9. Test Results

- **67 automated backend tests** — all passing  
- Demo question coverage — 17 questions tested for distinct, non-repeating answers  
- Pricing guardrails — no invented ₹ amounts  

---

## 10. Git Commits Today

| Commit | Description |
|--------|-------------|
| ced339c | Update knowledge with new VIS Figma website content |
| 4758b3a | Add clean Django admin and analytics styling |
| 38db484 | Add official Vetri IT logo |
| 9dcf470 | Tune replies for natural English (2–4 lines) |
| 24ee055 | Analytics link on admin home |
| 42cdf15 | Analytics in admin left sidebar |
| cf8f5cb | Health check shows database type |
| 3e001e5 | Simplify UI — remove quick actions and duplicate welcome |
| 0078d51 | Distinct answers for VIS vs why choose VIS |
| f8139ab | Distinct routing for all demo questions + 67 tests |

---

## 11. One-Line Summary for Mentor

> Coach AI is deployed on Render with natural Gemini-powered replies, verified VIS knowledge, enquiry lead capture with email, and a styled admin panel — ready for demo after PostgreSQL `DATABASE_URL` is confirmed on Render.

---

**Prepared by:** _________________________  
**Signature:** _________________________  

*Attachments: `docs/MENTOR_DEMO_SHEET.md` · `docs/EXPECTED_USER_QUESTIONS.md`*
