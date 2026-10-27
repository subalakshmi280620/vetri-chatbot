# Test report — candidate v5

- Python syntax compilation: PASS (`python -m compileall` on backend source).
- Django `check`: NOT RUN in packaging environment (Django package unavailable).
- Django unit tests: NOT RUN against these changes. Prior v3/v4 tests reported by the user are not evidence that the new login/analytics changes pass.
- Frontend lint: NOT RUN in packaging environment (ESLint dependency unavailable).
- Frontend production build: NOT RUN in packaging environment (Vite dependency unavailable).
- Browser smoke test: NOT RUN.

Required before deployment: run `python manage.py migrate`, `python manage.py check`, `python manage.py test chatbot`, `npm.cmd ci`, `npm.cmd run lint`, `npm.cmd run build`, then perform the manual checks in `README_LOCAL_SETUP.md`.
