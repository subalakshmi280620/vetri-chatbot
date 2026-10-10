# Vetri AI Coach â€” Project Review Presentation

**Student:** [Your Name]
**Project:** Vetri AI Coach (AI Chatbot for Vetri IT Systems)
**Status:** Deployed on Render â€” ready for vetriitsystems.com embed

---

## One-page speaking script (read or memorize key points)

### Opening (30 sec)

Good morning/afternoon. I built **Vetri AI Coach** â€” an AI-powered chatbot for **Vetri IT Systems**. It helps website visitors ask about **courses, products, and services**, submit **enquiries**, and lets staff **manage leads** from an admin panel. The system is **live on Render** and ready to embed on the main website.

### Problem (30 sec)

Visitors often ask the same questions â€” course eligibility, fees, products like Vetri Bills. They had to call, email, or search the site. Staff had no single dashboard to track enquiries. Coach AI answers questions **24/7** and captures leads automatically.

### Solution overview (30 sec)

A full-stack web application: **React chat UI**, **Django API**, **PostgreSQL database**, **Gemini AI** with **Grok/DeepSeek fallbacks**, **vector RAG** for verified company knowledge, **Tamil and English** support, **enquiry forms**, **email alerts**, and **admin dashboards** for analytics and leads.

### Live links (have these open)

| Item | URL |
|------|-----|
| Chat UI | https://vetri-chatbot-ui.onrender.com |
| Embed preview | https://vetri-chatbot-ui.onrender.com/embed.html |
| Admin | https://vetri-chatbot-1.onrender.com/admin/ |
| Leads | https://vetri-chatbot-1.onrender.com/admin/chatbot-leads/ |
| Analytics | https://vetri-chatbot-1.onrender.com/admin/chatbot-analytics/ |

### Demo flow (5â€“7 min)

1. **Chat** â€” Ask: *What courses do you offer?* / *Tell me about Vetri Bills.*
2. **Follow-up** â€” Say: *tell me more* or *yes* (shows conversation memory).
3. **Tamil** (optional) â€” Ask in Tamil/Tanglish.
4. **Enquiry** â€” Submit Enroll or Quotation form.
5. **Leads dashboard** â€” Show new lead, change status, add note, assign staff.
6. **Analytics** â€” Show message counts and top questions.
7. **Embed** â€” Show floating Coach AI icon on embed preview page.

### Closing (20 sec)

Vetri AI Coach is production-ready with verified answers, multilingual support, lead capture, and staff tools. **147 automated tests** pass. The only remaining step for the main website is adding one embed script tag to vetriitsystems.com. Thank you â€” Iâ€™m happy to answer questions.

---

## PowerPoint slide outline (10 slides)

### Slide 1 â€” Title

- **Vetri AI Coach**
- AI Chatbot for Vetri IT Systems
- [Your Name] | [Date]
- Live demo: vetri-chatbot-ui.onrender.com

### Slide 2 â€” Problem statement

- Visitors repeat the same questions (courses, fees, products)
- No 24/7 instant answers on the website
- Enquiries scattered â€” hard for staff to track and follow up
- Risk of wrong information if AI is not controlled

### Slide 3 â€” Solution overview

- AI chatbot with **verified company knowledge (RAG)**
- Enquiry capture + email notifications
- Admin: **Analytics** + **Leads dashboard**
- Embeddable widget for vetriitsystems.com
- Deployed on **Render** (PostgreSQL)

### Slide 4 â€” How the chatbot works

- User asks in natural language (English / Tamil)
- **Gemini AI** â†’ primary (natural replies)
- **Grok** â†’ fallback if Gemini fails
- **DeepSeek** â†’ third fallback
- **Verified KB / RAG** â†’ when AI unavailable; blocks invented prices
- Short answers by default; detailed when user asks for more

### Slide 5 â€” Vector RAG & verified facts

- Knowledge indexed from official VIS content
- Semantic search finds relevant chunks
- AI must use verified facts only
- Prevents fake fees, fake course details
- Important for business trust

### Slide 6 â€” Enquiry & lead capture

- In-chat forms: **Enroll, Quotation, Consultation, Demo, Sales**
- Data saved to PostgreSQL
- **Email notification** to team on new enquiry
- No public login required for visitors

### Slide 7 â€” Leads dashboard (staff)

- Staff-only admin page
- List all enquiries with search and filters
- Status: **New â†’ Contacted â†’ Closed**
- **Assign staff** to each lead
- **Private notes** with date and author
- Mini CRM for follow-up

### Slide 8 â€” Analytics dashboard (staff)

- Conversation and message statistics
- Enquiry breakdown by type
- Top questions and topics
- Daily / weekly trends
- Helps improve content and training

### Slide 9 â€” Technology stack

| Layer | Tech |
|-------|------|
| Frontend | React, Vite |
| Backend | Django 6, Python |
| Database | PostgreSQL |
| AI | Gemini, Grok (xAI), DeepSeek |
| Knowledge | Vector RAG, embeddings |
| Hosting | Render |
| Quality | 147 automated tests |

### Slide 10 â€” Status, next steps & Q&A

- **Completed:** Full MVP deployed and tested
- **Live website:** Add embed script to vetriitsystems.com footer
- **Optional Phase 2:** Monitoring, rate limits, WhatsApp lead alerts
- **Questions?**

---

## Feature cheat sheet (quick answers)

| Feature | One-line explanation |
|---------|----------------------|
| AI chat | Natural Q&A powered by Gemini with safe fallbacks |
| RAG | Searches official VIS knowledge before answering |
| Tamil/English | Detects language; replies appropriately |
| Follow-ups | Understands â€œyesâ€ / â€œtell me moreâ€ from context |
| Enquiry forms | Capture leads without leaving the chat |
| Email alerts | Team notified when someone submits an enquiry |
| Analytics | Usage stats and popular questions for staff |
| Leads dashboard | Track, assign, and note on every enquiry |
| Embed widget | Floating Coach AI icon on main website |
| Security | Staff-only admin; API keys in env vars; CSRF on forms |

---

## Mentor Q&A â€” short answers

**Is the project complete?**
Yes for MVP. Deployed with chat, enquiries, admin, analytics, leads, and embed.

**What if Gemini is down?**
Grok, then DeepSeek, then verified knowledge base.

**How do you prevent wrong prices?**
Verified facts enforcement; only official prices allowed.

**How does staff follow up?**
Leads dashboard + email; status, notes, assignment.

**Tests?**
147 automated tests, all passing.

**Whatâ€™s left for main website?**
Website team adds one script tag before `</body>` on vetriitsystems.com.

---

## Embed script (for website team)

```html
<script
  src="https://vetri-chatbot-ui.onrender.com/coach-ai-widget.js"
  data-chat-url="https://vetri-chatbot-ui.onrender.com"
  data-title="Coach AI"
  defer
></script>
```
