import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
d=json.loads((p/"artifacts/NATIVE_SOURCE.json").read_text())
assert d["counts"]=={"ZL3b":33,"IT2a":32,"RF1b":32}
assert len(d["rows"])==97
assert all(r["locus"] in {f"f83r.{i}" for i in range(25,31)} for r in d["rows"])
print("SOURCE_SCOPE_ONLY_PASS;AUTHOR_NOT_REVIEWED")
