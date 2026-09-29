# Expected User Questions — Coach AI (Vetri IT Systems)

This document lists the types of questions real website visitors are likely to ask Coach AI, how the chatbot should respond, and a test checklist for demos and mentor review.

---

## 1. Purpose

Coach AI is the official assistant for **Vetri IT Systems (VIS)**. Users open the chatbot when they want quick answers about the company, products, services, training programmes, pricing enquiries, or contact details — without searching the full website.

The chatbot is designed to:

- Answer **naturally** (conversational, short replies)
- Stay **accurate** (verified VIS website content only)
- **Not invent** pricing, clients, or features
- **Route serious leads** to the enquiry form (quotation, consultation, product demo)

---

## 2. User Mindset Map

```
Visitor arrives on website
        │
        ├── Curious      → Who is VIS? What do you do?
        ├── Shopping     → Products, services, comparisons
        ├── Price        → How much? Request quotation
        ├── Ready to buy → Demo, consultation, enquiry form
        ├── Student      → Courses, eligibility, how to apply
        └── In a hurry   → Phone, email, address
```

---

## 3. Question Categories and Examples

### 3.1 Company and trust (first-time visitors)

| Example questions | Expected behaviour |
|-------------------|-------------------|
| What is Vetri IT Systems? | Short intro, tagline, what VIS does |
| Who are you? / What is VIS? | Same as above |
| Where are you located? | Surandai address |
| How can I contact you? | +91 84381 54827, support@vetri-it.com |
| What is your mission and vision? | Verified mission/vision from website |

### 3.2 Products (enterprise software)

| Example questions | Expected behaviour |
|-------------------|-------------------|
| What products does VIS offer? | List main products in natural language |
| Tell me about Vetri Bills | GST billing and invoicing features |
| What is Vetri CRM? | Sales pipelines, leads, quotations |
| What is Coach AI? | AI learning platform + training programmes |
| Difference between Coach AI and Vetri AI Assistant? | Learning vs private company assistant |

**Products covered:** Vetri Bills, Vetri Files, Vetri Project Management, Coach AI, Vetri AI Assistant, Vetri CRM, Vetri Training Management System.

### 3.3 Services (custom work)

| Example questions | Expected behaviour |
|-------------------|-------------------|
| What services do you provide? | Web, mobile, UI/UX, AI, ERP, SEO, cloud, etc. |
| I need a website for my business | Match to Website Development, offer consultation |
| Do you build mobile apps? | Yes — Mobile App Development |
| We want AI solutions | Explain AI services, offer consultation |
| Do you do digital marketing / SEO? | Confirm service, brief description |

### 3.4 Pricing and business enquiries

| Example questions | Expected behaviour |
|-------------------|-------------------|
| How much does it cost? | No fixed ₹ price — tailored quotation |
| What are the fees? | Same — contact or enquiry form |
| I want a quotation | Direct to quotation enquiry or explain process |
| I want a product demo | Demo enquiry flow |
| Book a consultation | Consultation enquiry flow |
| Contact sales | Sales / general enquiry |

**Important:** Coach AI must **never invent exact prices**. Users should use the **Enquiry** form or contact support@vetri-it.com.

### 3.5 Training courses (Coach AI programmes)

| Example questions | Expected behaviour |
|-------------------|-------------------|
| What courses are available? | List programmes (Python, Java, Data Science, etc.) |
| Tell me about Python Fullstack | Course overview, 180-day programme |
| How long is the course? | **180 days** |
| Who can apply? / Am I eligible? | **Any degree completion** (UG/PG) |
| I have B.Tech / B.Com — can I join? | Eligibility check based on qualification |
| How do I apply? | Steps + contact VIS team |

**Courses covered:** Python Fullstack, Java Fullstack, Prompt Engineering, UI/UX, Software Testing, Data Analytics, Mobile App Development, AWS & DevOps, Data Science, Digital Marketing.

### 3.6 Quick contact (impatient users)

| Example questions | Expected behaviour |
|-------------------|-------------------|
| Phone number? | +91 84381 54827 (clickable) |
| Email? | support@vetri-it.com (clickable) |
| Address? | Vetri Academy, Aerial Complex, Behind Bus Stand, Surandai |

### 3.7 Credibility

| Example questions | Expected behaviour |
|-------------------|-------------------|
| Why should I choose VIS? | Why VIS points from verified content |
| Show your portfolio | Direct to contact for case studies if not in KB |
| How many projects have you done? | Verified stats (50+ projects, 10+ products, etc.) |

### 3.8 Multimodal input (voice, photos, documents)

| Input type | Example use |
|------------|-------------|
| Voice | User speaks: "What products do you offer?" |
| Photo | Screenshot of product page: "What is this?" |
| PDF / TXT | Brochure upload: "Summarise this" |

Requires Gemini API and supported browser (voice: Chrome/Edge recommended).

### 3.9 Off-topic questions

| Example questions | Expected behaviour |
|-------------------|-------------------|
| Weather, sports, homework, other companies | Politely decline; offer VIS topics or contact |

---

## 4. Top 15 Test Questions (Demo Checklist)

Use these before mentor review or go-live:

| # | Question | Pass criteria |
|---|----------|---------------|
| 1 | Hi | Friendly natural greeting |
| 2 | What is Vetri IT Systems? | Company intro, not a FAQ template wall |
| 3 | What products does VIS offer? | Products named correctly |
| 4 | Tell me about Vetri Bills | GST billing, relevant features |
| 5 | What services do you provide? | Services listed naturally |
| 6 | I need a website — can you help? | Website development + next step |
| 7 | How can I contact you? | Correct phone, email, address |
| 8 | How can I get a quotation? | Quotation process or enquiry form |
| 9 | I want a product demo | Demo enquiry guidance |
| 10 | What courses are available? | Course list |
| 11 | Am I eligible? I have B.Com | Eligibility conversation |
| 12 | What is the course duration? | 180 days |
| 13 | Why choose VIS? | Why VIS summary |
| 14 | What is your mission? | Mission/vision |
| 15 | How much does Python course cost? | **No invented price** → quote/contact |

---

## 5. Chat vs Enquiry Form

| Feature | Purpose |
|---------|---------|
| **Chat** | Questions, explanations, eligibility, general guidance |
| **Enquiry form** | Structured lead: name, email, phone, requirement → admin + email |
| **Export** | User downloads chat transcript (.txt) for their own records |

---

## 6. Verified Facts (Must Stay Exact)

| Item | Official value |
|------|----------------|
| Company | Vetri IT Systems (VIS) |
| Phone | +91 84381 54827 |
| Email | support@vetri-it.com |
| Address | Vetri Academy, Aerial Complex, Behind Bus Stand, Surandai |
| Course duration | 180 days |
| Course eligibility | Any degree completion (UG/PG) |

---

## 7. Architecture Note (Single Agent)

Coach AI uses a **single AI agent** (Gemini) with verified knowledge base and RAG — not multi-agent. This is appropriate for a company website chatbot: natural conversation with accurate, grounded answers.

---

## 8. Live URLs (Production)

| Resource | URL |
|----------|-----|
| Chat UI | https://vetri-chatbot-ui.onrender.com |
| Embed mode | https://vetri-chatbot-ui.onrender.com/?embed=1 |
| Embed kit | https://vetri-chatbot-ui.onrender.com/embed.html |
| API | https://vetri-chatbot-1.onrender.com |
| Admin | https://vetri-chatbot-1.onrender.com/admin/ |
| Analytics | https://vetri-chatbot-1.onrender.com/admin/chatbot-analytics/ |

---

*Document version: September 2026 — Coach AI for Vetri IT Systems*
