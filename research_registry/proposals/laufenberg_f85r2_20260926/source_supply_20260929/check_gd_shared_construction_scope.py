"""Enumerate exact EY/EDY pairs in frozen ES dictionaries; no target access."""
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "ES_JOINT_FAMILY_AUTHOR.json"
FOCAL = {("cheey", "cheedy"), ("qokeey", "qokeedy")}

def run():
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    rows = []
    sizes = {}
    for model, parent in sorted(source["parent32_models_unchanged"].items()):
        words = {}
        for layer in (parent["dictionary"], source["prospective_EQ14_unchanged"],
                      source["new_exact_whole_values"]):
            for form, value in layer.items():
                if form in words and words[form] != value:
                    raise ValueError("Conflicting frozen value: " + form)
                words[form] = value
        sizes[model] = len(words)
        for form in sorted(words):
            if not form.endswith("ey"):
                continue
            partner = form[:-1] + "dy"
            if partner not in words:
                continue
            rows.append(dict(model=model, base=form, base_value=words[form],
                             partner=partner, partner_value=words[partner],
                             proposed_scope="focal" if (form, partner) in FOCAL else "outside"))
    result = dict(source=SOURCE.name, source_sha256=hashlib.sha256(raw).hexdigest(),
                  rule="Exact terminal ey -> edy; no normalization or inferred missing forms",
                  dictionary_sizes=sizes, rows=rows,
                  scope="Frozen hypothetical lexicon only; no semantic or manuscript validation")
    (BASE / "GD_SHARED_CONSTRUCTION_SCOPE_20261002.json").write_text(
        json.dumps(result, indent=2) + "\n")
    with (BASE / "GD_SHARED_CONSTRUCTION_SCOPE_20261002.tsv").open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(dict(models=len(sizes), paired_rows=len(rows),
                          unique_pairs=len({(r["base"], r["partner"]) for r in rows}),
                          manuscript_data_read=False)))

if __name__ == "__main__":
    run()
