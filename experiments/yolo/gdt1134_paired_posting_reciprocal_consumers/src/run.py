"""Read-only replay of the frozen GDT1134 whole accounts."""
from pathlib import Path
import hashlib
import importlib.util
import json

BASE = Path(__file__).resolve().parents[1]


def main():
    receipt = json.loads((BASE / "artifacts/FINAL_FREEZE_RECEIPT.json").read_text())
    for relative, expected in receipt["files"].items():
        assert hashlib.sha256((BASE / relative).read_bytes()).hexdigest() == expected, relative
    assert hashlib.sha256((BASE / "src/SOURCE.json").read_bytes()).hexdigest() == receipt["source_sha256"]
    spec = importlib.util.spec_from_file_location("frozen_1134_author", BASE / "src/author_helper.py")
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    source = json.loads((BASE / "src/SOURCE.json").read_text())
    extension = json.loads((BASE / "src/EXTENSIONS.json").read_text())
    frozen = json.loads((BASE / "artifacts/AUTHOR_ACCOUNT.json").read_text())
    fixed = {sid: chunk["fixed_units"] for line in source["lines"]
             for chunk in line["chunks"] for sid in chunk["source_ids"]}
    dictionary = {item["raw_form"]: item for item in extension["dictionary"]}
    results = {}
    for edition, expected in frozen["accounts"].items():
        native = [row for row in source["native_rows"] if row["edition"] == edition]
        replay = author.evaluate(native, fixed, dictionary, author.world())
        assert replay == expected, edition
        results[edition] = {"exact_replay": True, "author_status": replay["status"],
                            "first_barrier": replay["first_barrier"], "native_rows": len(native)}
    print(json.dumps({"status": "EXACT_FROZEN_ACCOUNT_REPLAY", "readers": results,
                      "author_files_changed": False, "semantic_validation": False}, indent=2))


if __name__ == "__main__":
    main()
