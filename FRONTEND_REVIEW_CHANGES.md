# Frontend review changes

Changes in this candidate:
- Removed the redundant Enquiry link from the main navigation; the Get a quotation CTA remains connected to the enquiry flow.
- Moved Logout to the upper-right area below the sticky navigation and aligned its navy/green styling with the website.
- Improved visitor login card styling, spacing, focus states, and responsive presentation without changing authentication logic.
- Corrected confirmed mojibake symbols in App.jsx, including arrows, the rupee symbol, and the enquiry confirmation checkmark.
- Updated the homepage metrics to match figures currently displayed on the official Vetri IT Systems website: 50+ digital solutions delivered, 99.4% on-time delivery, 30+ senior engineers/designers, and 5+ countries served. These figures should be reconfirmed with the company before final publication because public website content can change.
- Connected company description, mission, vision, phone, email, website, and address display to the existing Admin-backed public-content API, with safe fallback text. Updated fallback mission/vision and contact values to match the current official website checked during this review. Admin values take precedence.
- Added an FAQ section that renders active FAQ records returned by the Admin-backed public-content API.
- Product and service cards continue to use active records returned by the existing Admin-backed public-content API.

Important limits:
- The backend endpoint already exposes company, products, services, and FAQs. The frontend now consumes those fields, but this does not prove the deployed database has the expected records; verify the live Admin data and API response after deployment.
- The page routes are separate (Home, About Us, Services, Products, Portfolio, Contact), and the main content sections have dedicated layouts. Company identity/contact, products, services and FAQs are the important Admin-managed content. Portfolio entries and general marketing copy remain frontend-defined because this project does not expose an Admin-managed portfolio/content model through the public-content endpoint. This is intentional for this scope; full Admin editing of every page would require additional backend model/API work.
- Automated `npm run build` could not be completed in the packaging environment because Vite dependencies were unavailable and package installation timed out. Run `npm.cmd ci`, `npm.cmd run lint`, and `npm.cmd run build` on Windows before deployment.
- No backend, database, credentials, or authentication logic was intentionally changed.


## Chatbot pricing and official-site coverage (v4)
- Added deterministic grounding for the configured e-commerce website price (₹9,999 + GST) and small retail shop website price (₹3,000 + GST).
- Other custom project pricing is described as scope-dependent; the chatbot is instructed not to invent fixed prices.
- This does not assert that the official company website publishes those two configured package prices; confirm package rates and inclusions with the company before public launch.
- Official website FAQs, policies, service descriptions, and product details should be added to Admin FAQ/Product/Service records for live Admin-first answers. Existing chat knowledge still contains some static details and should be reviewed against the live company website.
