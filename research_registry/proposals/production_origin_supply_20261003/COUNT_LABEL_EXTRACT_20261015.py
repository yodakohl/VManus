"""Project three fixed label loci from existing admitted GDT915 JSON caches."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOSSIER = Path(__file__).resolve().parent
LOCI = ("f66r.82", "f82v.3", "f89v1.24")
READERS = ("IT2a", "ZL3b", "RF1b")


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def extract():
    plan = DOSSIER / "COUNT_GROUP_BINDING_PLAN_20261015.json"
    assert set(json.loads(plan.read_bytes())["source_selection"]["label_loci"]) == set(LOCI)
    sources, readers = [], {}
    for edition in READERS:
        records = {locus: [] for locus in LOCI}
        for phase in ("DISCOVERY", "EVALUATION"):
            relative = Path("experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts") / f"SOURCE_{phase}_{edition}.json"
            blob = (ROOT / relative).read_bytes()
            source = json.loads(blob)
            sources.append({"path": relative.as_posix(), "sha256": sha(blob)})
            for line in source["lines"]:
                metadata = line["metadata"]
                locus = metadata["locus"]
                if locus not in records:
                    continue
                assert metadata["page"] == locus.split(".")[0]
                assert metadata["edition"] == edition
                assert metadata["kind"] == "L"
                assert int(metadata["source_group_count"]) == len(line["groups"])
                records[locus].append({"source": relative.as_posix(), "group_columns": source["group_columns"], "line": line})
        for entries in records.values():
            assert len(entries) <= 1, "Duplicate exact locus in source caches"
        readers[edition] = {
            "loci": {locus: {"status": "PRESENT" if entries else "MISSING_FROM_SIX_CACHES", "records": entries} for locus, entries in records.items()},
            "present_loci": sum(bool(entries) for entries in records.values()),
            "raw_groups": sum(len(entry["line"]["groups"]) for entries in records.values() for entry in entries),
        }
    return {
        "schema": "count-label-source-v1",
        "status": "EXACT_EXISTING_LABEL_PROJECTION_NO_OWNER_OR_COUNT_BINDING",
        "selection_plan": {"path": plan.relative_to(ROOT).as_posix(), "sha256": sha(plan.read_bytes())},
        "extractor": {"path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__).read_bytes())},
        "selected_loci": list(LOCI),
        "sources": sources,
        "readers": readers,
        "limits": ["All nested line metadata, groups and group columns preserved unchanged.", "Only the three fixed kind-L loci selected; no circular line or adjacent payload included.", "Reader-specific flags and separators retained; no normalization or reader pooling.", "Prior exposed source, not independent confirmation. No caption owner, word meaning, group membership or number inferred."],
    }


if __name__ == "__main__":
    packet = extract()
    output = DOSSIER / "COUNT_LABEL_SOURCE_20261015.json"
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    assert json.loads(output.read_bytes()) == packet
    print(json.dumps({"output": output.relative_to(ROOT).as_posix(), "sha256": sha(output.read_bytes()), "readers": {edition: {key: value for key, value in record.items() if key != "loci"} for edition, record in packet["readers"].items()}}, indent=2))
