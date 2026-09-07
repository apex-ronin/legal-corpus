"""
Corpus schema validation — run before any commit touching corpus/.

Checks every corpus/*.json file:
  - parses as a JSON array of objects
  - every clause has non-empty id, title, vector, clause_text (strings)
  - no unknown fields
  - ids are unique across the entire corpus

Exit 0 on pass, 1 on any violation.
"""

import json
import sys
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus"
REQUIRED_FIELDS = {"id", "title", "vector", "clause_text"}


def main() -> int:
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    total = 0

    files = sorted(CORPUS_DIR.glob("*.json"))
    if not files:
        print(f"FAIL: no corpus files found in {CORPUS_DIR}")
        return 1

    for path in files:
        try:
            clauses = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}: invalid JSON — {e}")
            continue
        if not isinstance(clauses, list):
            errors.append(f"{path.name}: top level must be a JSON array")
            continue

        for i, c in enumerate(clauses):
            where = f"{path.name}[{i}]"
            if not isinstance(c, dict):
                errors.append(f"{where}: clause must be an object")
                continue
            missing = REQUIRED_FIELDS - set(c)
            unknown = set(c) - REQUIRED_FIELDS
            if missing:
                errors.append(f"{where}: missing fields {sorted(missing)}")
            if unknown:
                errors.append(f"{where}: unknown fields {sorted(unknown)}")
            for field in REQUIRED_FIELDS & set(c):
                if not isinstance(c[field], str) or not c[field].strip():
                    errors.append(f"{where}: field '{field}' must be a non-empty string")
            cid = c.get("id")
            if isinstance(cid, str):
                if cid in seen_ids:
                    errors.append(f"{where}: duplicate id '{cid}' (first in {seen_ids[cid]})")
                else:
                    seen_ids[cid] = path.name
            total += 1

    print(f"Checked {total} clauses across {len(files)} files.")
    if errors:
        print(f"FAIL — {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS — corpus schema valid, all ids unique.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
