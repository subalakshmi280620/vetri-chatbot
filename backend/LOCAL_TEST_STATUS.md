# Local candidate test status

## Changes in this revision
- Website package pricing is handled before the generic Tamil/Tanglish fallback, so ecommerce/retail price questions direct users to Enquiry → Quotation.
- Updated stale tests to match the current policy: public course catalogue details and public enrolment stay disabled.
- Updated the leads-dashboard test to expect only accepted enquiry types; rejected public enrolment must not create a lead.
- Corrected the prompt test to check the wording actually used by the prompt (`1–2 tight sentences`).

## Checks run here
- Python syntax compilation passed for `backend/chatbot/knowledge.py` and `backend/chatbot/tests.py`.
- ZIP integrity check passed after packaging.

## Not verified here
- Django test suite was not run in this environment because Django is not installed here. Do not treat this candidate as fully test-passing until `python manage.py test chatbot --verbosity 2` passes in the project's Windows virtual environment.
- No production database, leads, GitHub repository, or Render service was changed.
