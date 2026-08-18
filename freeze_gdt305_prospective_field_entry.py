#!/usr/bin/env python3
"""Freeze score-blind low-support pairs for GDT305."""
import csv, hashlib, itertools, json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
EXPOSED = R / "gdt303_pair_deltas.tsv"
METHOD = R / "GDT305_PROSPECTIVE_FIELD_ENTRY_LOW_SUPPORT_METHOD.md"
PAIRS = R / "gdt305_frozen_pairs.tsv"
CAPACITY = R / "gdt305_capacity.tsv"
DESIGN = R / "gdt305_design.json"
MANIFEST = R / "gdt305_freeze_manifest.tsv"
FIELDS = ("wrapper", "local_frame", "inner_d", "right_family", "dy_closure", "b3")
OPERATIONS = (("wrapper", "NONE", "q"), ("wrapper", "ch", "s"), ("wrapper", "d", "s"))
ALLOWED = {
    "control_id", "page", "locus", "physical_folio", "group_count",
    "page_host", "source_surface_sha256", *FIELDS,
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()

def write_tsv(path, rows, fields):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    exposed_forms = set()
    with EXPOSED.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            exposed_forms.add(row["source_surface_sha256"])
            exposed_forms.add(row["target_surface_sha256"])

    forms = defaultdict(lambda: defaultdict(lambda: {
        "events": 0, "folios": set(), "renderer": None,
    }))
    with SOURCE.open(encoding="utf8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        assert ALLOWED <= set(reader.fieldnames)
        for original in reader:
            # Copy only score-blind columns before any downstream operation.
            row = {key: original[key] for key in ALLOWED}
            if row["control_id"] != "VOYNICH_REFERENCE" or int(row["group_count"]) < 2:
                continue
            assert not row["page"].startswith("f84") and not row["locus"].startswith("f84")
            item = forms[row["page_host"]][row["source_surface_sha256"]]
            item["events"] += 1
            item["folios"].add(row["physical_folio"])
            renderer = tuple(row[key] for key in FIELDS)
            if item["renderer"] is None:
                item["renderer"] = renderer
            assert item["renderer"] == renderer

    frozen = []
    capacity_all = defaultdict(lambda: {"pairs": 0, "hosts": set(), "events": 0})
    capacity_support = defaultdict(lambda: {"pairs": 0, "hosts": set(), "events": 0})
    for host, form_map in forms.items():
        for (sha_a, a), (sha_b, b) in itertools.combinations(sorted(form_map.items()), 2):
            differences = [i for i, (x, y) in enumerate(zip(a["renderer"], b["renderer"])) if x != y]
            if len(differences) != 1:
                continue
            index = differences[0]
            field = FIELDS[index]
            oriented = None
            for source_sha, source, target_sha, target in (
                (sha_a, a, sha_b, b), (sha_b, b, sha_a, a),
            ):
                operation = (field, source["renderer"][index], target["renderer"][index])
                if operation in OPERATIONS:
                    oriented = (operation, source_sha, source, target_sha, target)
                    break
            if oriented is None:
                continue
            operation, source_sha, source, target_sha, target = oriented
            op_name = f"{operation[0]}:{operation[1]}>{operation[2]}"
            all_item = capacity_all[op_name]
            all_item["pairs"] += 1
            all_item["hosts"].add(host)
            all_item["events"] += source["events"] + target["events"]
            eligible = (
                min(source["events"], target["events"]) >= 2
                and min(len(source["folios"]), len(target["folios"])) >= 2
                and source_sha not in exposed_forms
                and target_sha not in exposed_forms
            )
            if not eligible:
                continue
            kept = capacity_support[op_name]
            kept["pairs"] += 1
            kept["hosts"].add(host)
            kept["events"] += source["events"] + target["events"]
            frozen.append({
                "pair_id": "G305P" + hashlib.sha256(
                    f"{op_name}|{host}|{source_sha}|{target_sha}".encode()).hexdigest()[:12].upper(),
                "operation": op_name,
                "page_host": host,
                "source_surface_sha256": source_sha,
                "target_surface_sha256": target_sha,
                "source_events": source["events"],
                "target_events": target["events"],
                "source_folios": len(source["folios"]),
                "target_folios": len(target["folios"]),
                "gdt303_surface_exposure": "BOTH_UNEXPOSED",
            })

    frozen.sort(key=lambda row: (row["operation"], row["page_host"], row["pair_id"]))
    fields = list(frozen[0])
    write_tsv(PAIRS, frozen, fields)
    capacity_rows = []
    for operation in ("wrapper:NONE>q", "wrapper:ch>s", "wrapper:d>s"):
        a, b = capacity_all[operation], capacity_support[operation]
        capacity_rows.append({
            "operation": operation,
            "all_identity_matched_pairs": a["pairs"],
            "all_identity_matched_hosts": len(a["hosts"]),
            "frozen_pairs": b["pairs"],
            "frozen_hosts": len(b["hosts"]),
            "frozen_events": b["events"],
            "capacity": "DESCRIPTIVE_ONLY" if len(b["hosts"]) < 4 else "PROSPECTIVE_DIRECTION_TEST",
        })
    write_tsv(CAPACITY, capacity_rows, list(capacity_rows[0]))

    design = {
        "schema": "GDT305_PROSPECTIVE_FIELD_ENTRY_LOW_SUPPORT_DESIGN_V1",
        "status": "FROZEN_BEFORE_GDT305_POSITION_SCORING",
        "score_blind_columns": sorted(ALLOWED),
        "renderer_fields": list(FIELDS),
        "operations": [f"{a}:{b}>{c}" for a, b, c in OPERATIONS],
        "minimum_events_per_form": 2,
        "minimum_folios_per_form": 2,
        "require_both_surfaces_absent_from_gdt303_pairs": True,
        "predictions": {
            "P1": "NONE_TO_Q_FIELD_FIRST_POSITIVE_AND_FIELD_LAST_NEGATIVE",
            "P2": "CH_TO_S_FIELD_FIRST_POSITIVE",
            "P3": "D_TO_S_FIELD_FIRST_POSITIVE",
            "P4": "ALL_OPERATION_RECORD1_ABSOLUTE_MEAN_DELTAS_BELOW_0_10",
        },
        "diagnostic_null": "EXACT_HOST_VECTOR_SIGN_FLIP",
        "claim_ceiling": "Formal probabilistic field-entry renderer transfer only; no grammatical semantic phonetic language plaintext or translation claim.",
        "f84": {"authorized": False, "opened": False, "parsed": False,
                 "retained": False, "joined": False, "scored": False},
        "inputs": {SOURCE.name: sha(SOURCE), EXPOSED.name: sha(EXPOSED), METHOD.name: sha(METHOD)},
        "outputs": {PAIRS.name: sha(PAIRS), CAPACITY.name: sha(CAPACITY)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    manifest = [{
        "artifact": path.name, "sha256": sha(path), "status": "FROZEN_BEFORE_POSITION_SCORING",
    } for path in (METHOD, PAIRS, CAPACITY, DESIGN, SOURCE, EXPOSED, Path(__file__))]
    write_tsv(MANIFEST, manifest, list(manifest[0]))
    print(json.dumps({
        "status": design["status"], "pairs": len(frozen),
        "capacity": capacity_rows, "design_sha256": sha(DESIGN),
    }, sort_keys=True))

if __name__ == "__main__":
    main()
