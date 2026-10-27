# Vetri AI Coach — merged candidate handoff

This package combines the supplied `Vetri-AI-Coach-updated.zip` source, which includes Admin-backed public content and chatbot product-price grounding, with the previously added course-section removal and WhatsApp/call floating actions already present in the supplied project. It is a **candidate for local testing**, not a verified production release.

## Before doing anything
1. Keep your current project and production Render service unchanged as a backup.
2. Extract this ZIP into a new folder, not over your existing folder.
3. Do not upload `.env` or API keys into this ZIP or share them in chat.
4. Do not run production migrations, seed commands, or deploy until local checks and staging smoke tests pass.

## Included
- React/Vite frontend and Django REST backend source.
- Read-only `/api/chatbot/public-content/` endpoint returning active Admin-managed company, product, service and FAQ data.
- Product/service public UI fetch with a static fallback if the API is unavailable.
- Chatbot product grounding for Admin product prices/price notes.
- WhatsApp/call floating buttons and public course-section removal from the supplied project.
- Existing enquiry/lead functionality and course models/migrations are retained to avoid destructive database changes.

## Not yet complete / not verified
- Full separate URL-routed pages for Home, Products, Services, Pricing, About and Contact.
- Dedicated Admin-managed package/pricing model and public API/UI.
- Full Admin control of every public text field, including hero/about/mission/contact.
- Complete removal of course-related backend chatbot knowledge and legacy enrolment behavior (the database model is retained intentionally).
- Secure registration/login and protected pages, if required for the final scope.
- Frontend lint/build and backend tests: these were not successfully completed in the packaging environment. Do not treat this ZIP as release-tested.
- Production/Render deployment and live smoke tests have not been performed.

## Next safe validation
Use a new local folder and the project's normal Python/Node environments. Run backend tests and frontend `npm run lint` / `npm run build`. Verify the API content endpoint and chatbot/enquiry flows against a development database. Only then consider staging deployment with explicit approval. Never run seed/migration commands against production just to fix empty Admin sections without first backing up and diagnosing the database.
