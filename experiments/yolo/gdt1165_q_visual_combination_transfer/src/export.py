"""Export every frozen observed event prediction; no fitting or selection."""
from pathlib import Path
import csv, gzip, json
E = Path(__file__).resolve().parents[1]
x = json.loads((E / "src/INPUT.json").read_text())
folds = json.loads(gzip.decompress((E / "artifacts/OBSERVED_FOLDS.json.gz").read_bytes()))
rows = []
for fold in folds:
    for j, index in enumerate(fold["test_event_indices"]):
        event = x["q_events"][index]
        row = {key: event[key] for key in ["sourceid", "page", "leaf", "locus", "index", "raw", "base", "q"]}
        row.update({f"p_q_{arm}": fold["predictions"][arm][j] for arm in ["C", "ID", "INV"]})
        row.update(gamma=fold["gamma"], C_converged=fold["C_fit"]["converged"], FULL_converged=fold["FULL_fit"]["converged"])
        rows.append(row)
rows.sort(key=lambda row: row["sourceid"])
assert len(rows) == len(x["q_events"]) == len({row["sourceid"] for row in rows})
with (E / "artifacts/EVENT_PREDICTIONS.tsv").open("w") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
