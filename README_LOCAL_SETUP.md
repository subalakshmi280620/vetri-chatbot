# Local setup and verification (Windows PowerShell)

## Backend
Open PowerShell in the project folder:

```powershell
cd .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test chatbot
python manage.py runserver 8000
```

Keep the backend terminal open. The health endpoint is `http://127.0.0.1:8000/health/`.

## Frontend
Open a second PowerShell window:

```powershell
cd .\frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run build
npm.cmd run dev
```

Open the exact URL Vite prints. The current Vite config uses port 5000. The Vite proxy forwards `/api`, `/admin`, `/health/`, and `/static` to Django on port 8000.

## Manual checks
1. In a new private/incognito window, confirm the login/register screen appears before website content.
2. Register a test account with a unique username, log out, then log in again.
3. Confirm `/products`, `/services`, `/about`, `/portfolio`, `/contact`, and `/enquiry` show distinct page content after navigation and when refreshed directly.
4. Ask Coach AI about a product, service, contact information, and a price not present in verified data. It should not invent a price.
5. Confirm course details and public enrolment remain unavailable.
6. Click WhatsApp and call icons; check that the WhatsApp link opens `wa.me/918438154827` and the call link uses `tel:+918438154827`.
7. In Django Admin, open Coach AI Analytics and confirm page visits, unique visitors, and top pages change after navigating the site.
8. With production-style auth enabled (`REQUIRE_LOGIN_FOR_PUBLIC_SITE=True`), request `/api/chatbot/public-content/` and `/api/chatbot/chat/` without the `X-Visitor-Auth` header; they should return HTTP 401. Repeat with a logged-in frontend session; requests should work.

## Production configuration
- Keep `DEBUG=False`.
- Set `REQUIRE_LOGIN_FOR_PUBLIC_SITE=True`.
- Keep the existing secure `DJANGO_SECRET_KEY`, database URL, and allowed origins configured.
- Apply migrations only through the normal reviewed deployment migration command. Never reset the database; existing enquiry leads must be preserved.

## Current verification caveat
The packaging environment did not have Django/Vite installed and could not access the package registry, so run the checks above in your local Windows environment before deploying.
