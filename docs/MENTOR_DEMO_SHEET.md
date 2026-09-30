# Coach AI — Mentor Demo Sheet
**Vetri IT Systems (VIS)** · Coach AI Chatbot  
**Student:** _________________________  **Date:** _________________________

---

## Live URLs

| Resource | URL |
|----------|-----|
| Chat UI | https://vetri-chatbot-ui.onrender.com |
| Embed mode | https://vetri-chatbot-ui.onrender.com/?embed=1 |
| Admin panel | https://vetri-chatbot-1.onrender.com/admin/ |
| Analytics | https://vetri-chatbot-1.onrender.com/admin/chatbot-analytics/ |

---

## One-Line Pitch

> **Coach AI** is a single-agent website assistant (Gemini + verified VIS knowledge + RAG).  
> Users **chat** for answers · **Enquiry form** captures leads · **Admin** monitors usage.

---

## 10-Minute Demo Script

Open the chat UI and follow these steps in order. Tick each box when done.

| ✓ | Step | Type or do this | Expected result |
|---|------|-----------------|-----------------|
| ☐ | 1 | Open chat UI | Welcome card + FAQ list (no quick actions, no duplicate welcome bubble) |
| ☐ | 2 | `Hi` | Short reply: *Hello! How can I help you today?* |
| ☐ | 3 | `What is Vetri IT Systems?` | 2–4 line company intro |
| ☐ | 4 | `Tell me about Vetri Bills` | GST billing product — no fake pricing |
| ☐ | 5 | `What services do you provide?` | Web, mobile, AI, ERP, etc. |
| ☐ | 6 | `How can I get a quotation?` | Answer + **Get quotation** button inside message |
| ☐ | 7 | Click button → submit enquiry form | Success in chat |
| ☐ | 8 | Open Admin → Enquirys | New enquiry row visible |
| ☐ | 9 | `What courses are available?` | Training programme list |
| ☐ | 10 | `I have B.Com — am I eligible?` | Eligibility check (degree required) |
| ☐ | 11 | `How can I contact you?` | Phone, email, address (verified) |
| ☐ | 12 | (Optional) Voice or photo upload | Multimodal input works |
| ☐ | 13 | Admin → Analytics | Conversation / message stats |

---

## Quick Test Questions (copy & paste)

**Greeting**
- Hi

**Company**
- What is Vetri IT Systems?
- Why should I choose VIS?
- What is your mission and vision?

**Products**
- What products does VIS offer?
- Tell me about Vetri Bills
- What is Coach AI?

**Services**
- What services do you provide?
- I need a website for my business
- Do you build mobile apps?

**Leads (show enquiry button)**
- How can I get a quotation?
- I want a product demo
- Book a consultation
- How much does Vetri Bills cost? *(must NOT invent ₹ price)*

**Training**
- What courses are available?
- What is the course duration? *(answer: 180 days)*
- Am I eligible? I have B.Com
- How do I apply for a course?

**Contact**
- How can I contact you?

**Guardrails**
- Who won the cricket match today? *(off-topic redirect)*

---

## Enquiry Form — Demo Data

| Field | Enter this |
|-------|------------|
| Full name | Demo User |
| Company | Demo Shop |
| Email | *(your email)* |
| Phone | +91 98765 43210 |
| Interest | Vetri Bills |
| Message | Need GST billing for retail shop. Please share quotation. |

---

## Verified Facts (must stay exact)

| Item | Official value |
|------|----------------|
| Company | Vetri IT Systems (VIS) |
| Phone | +91 84381 54827 |
| Email | support@vetri-it.com |
| Address | Vetri Academy, Aerial Complex, Behind Bus Stand, Surandai |
| Course duration | 180 days |
| Eligibility | Any completed degree (UG/PG) |
| Stats | 150+ projects · 8+ years · 50+ clients · 15+ team |

---

## Architecture (for mentor Q&A)

| Topic | Answer |
|-------|--------|
| Agent type | **Single agent** — Gemini LLM + keyword RAG + verified knowledge base |
| Not used | Multi-agent orchestration |
| Chat | Natural Q&A, eligibility flow, follow-up suggestions |
| Enquiry | Separate form → database + Resend email notification |
| Admin | Django admin — Conversations, Messages, Enquirys, Analytics |
| Database | PostgreSQL on Render (needs `DATABASE_URL` set) |
| Deploy | Render — React frontend + Django API |

---

## Feature Checklist

| ✓ | Feature |
|---|---------|
| ☐ | Natural AI replies (2–4 lines) |
| ☐ | Short greeting (no repeat intro) |
| ☐ | Enquiry button at top |
| ☐ | Contextual CTA inside bot message (quote/demo) |
| ☐ | Enquiry form saves to admin |
| ☐ | Email notification on enquiry |
| ☐ | Chat history + export |
| ☐ | Thumbs up/down feedback |
| ☐ | Voice input |
| ☐ | Photo / PDF upload |
| ☐ | Embed mode (`?embed=1`) |
| ☐ | Styled admin (navy + green) |

---

## Mentor Notes

**Strengths observed:**

_______________________________________________________________________________

_______________________________________________________________________________

**Improvements suggested:**

_______________________________________________________________________________

_______________________________________________________________________________

**Demo result:** ☐ Pass  ☐ Pass with changes  ☐ Needs more work

**Mentor signature:** _________________________  **Date:** _________________________

---

*Coach AI · Vetri IT Systems · September 2026*  
*Full question list: `docs/EXPECTED_USER_QUESTIONS.md`*
