# Vetri AI Coach — focused fixes in this package

## Changes made
- Fixed the Tamil-script language detector test to use valid Tamil Unicode code points rather than mojibake text.
- Fixed the Tamil prompt test assertion and AI mock fixture to use valid Tamil Unicode.
- Updated the public course-question test to assert the intended safe behaviour: a Tamil unavailable response without exposing course duration or internship facts.
- Fixed website-price enquiry routing: recognised ecommerce/retail website price questions now suggest `quotation`, not `enroll`.
- Changed the Tanglish website-price test to assert the verified ₹9,999 + GST price, a quotation path, and no enrolment/sign-in CTA.
- Corrected mojibake rupee and en-dash strings in test expectations to their real Unicode characters.

## Safety scope
- No migrations were created or run.
- No course model or historical course record was deleted.
- No production database, Render service, or GitHub repository was touched.
- Public course details and public course enrolment remain disabled.

## Verification status — read carefully
- `python -m py_compile` passed for `chatbot/tests.py` and `chatbot/knowledge.py`.
- Django test suite was **not run** in this packaging environment: Django is not installed, and package installation could not reach the package index (network unavailable).
- This is a focused corrected candidate, not a certified production release. Run the full Django test suite in the project's Windows virtual environment before deploying. Do not deploy this ZIP without that test run and a local smoke test.
