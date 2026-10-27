from pathlib import Path
import py_compile

root = Path(__file__).resolve().parent
target = root / "backend" / "chatbot" / "knowledge.py"
backup = root / "backend" / "chatbot" / "knowledge.py.before_followup_fix.bak"

if not target.is_file() or not backup.is_file():
    raise SystemExit("STOP: Source or backup file is missing.")

source = target.read_text(encoding="utf-8")
original = backup.read_text(encoding="utf-8")

if source != original:
    raise SystemExit("STOP: Source differs from backup. No changes made.")

old = '''    product_id = match_product_id(text)

    if product_id:
        summary = SHORT_PRODUCT_SUMMARIES.get(product_id)
        if summary:
            return f"{summary} Want more detail on any feature?"'''

new = '''    product_id = match_product_id(text)

    if product_id:
        if detailed:
            detail = get_grounding_facts(message)
            if detail and GENERIC_FALLBACK_MARKER not in detail:
                return detail

        summary = SHORT_PRODUCT_SUMMARIES.get(product_id)
        if summary:
            return f"{summary} Want more detail on any feature?"'''

if source.count(old) != 1:
    raise SystemExit(
        "STOP: Expected product block was not found exactly once. "
        "No changes made."
    )

updated = source.replace(old, new, 1)

check_file = root / "knowledge_followup_syntax_check.py"
try:
    check_file.write_text(updated, encoding="utf-8")
    py_compile.compile(str(check_file), doraise=True)
finally:
    check_file.unlink(missing_ok=True)
    check_file.with_suffix(".pyc").unlink(missing_ok=True)

target.write_text(updated, encoding="utf-8")
print("PATCH APPLIED. Python syntax validated.")