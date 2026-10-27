# Chatbot natural-language pricing update

This update expands website-pricing intent matching so common paraphrases such as “Do you have any low-cost website?”, “I need an affordable website”, “website on a low budget”, and “what is your cheapest website package?” can receive the general budget-options response. Specific ecommerce and small-retail-shop questions continue to receive their corresponding configured price.

The general response lists the two currently configured website prices and directs visitors to Enquiry → Quotation for other requirements. It does not create new prices or promise that an arbitrary custom website fits a stated budget.

Admin product/service/FAQ grounding remains part of the existing code path. New active records can be matched when the visitor asks about their names or details; unrelated paraphrases that do not identify an item may still need a matching FAQ or more descriptive query. Verify this with actual Admin data before production deployment.

## Verification

Run in Windows PowerShell from the extracted project:

```powershell
cd .\backend
python manage.py check
python manage.py test chatbot
cd ..\frontend
npm.cmd run lint
npm.cmd run build
```

Test these phrases in the chatbot:
- Do you have any low-cost website?
- I need a website on a low budget.
- What is your most affordable website package?
- How much for an online shop?
- What is the price of a small retail shop website?
- I need a custom website with booking and payment. (Should request a quotation rather than invent a price.)
