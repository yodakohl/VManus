#!/usr/bin/env python3
"""Score frozen GDT154 os visual predictions against direct observations."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
PRED = R / "gdt154_prediction.json"; PRED_TSV = R / "gdt154_os_visual_predictions.tsv"
OBS = R / "gdt154_visual_observations.tsv"; METHOD = R / "GDT154_OS_VISUAL_TRANSFER_METHOD.md"
REPORT = R / "GDT154_OS_VISUAL_TRANSFER_REPORT.md"; SCORED = R / "gdt154_scored_predictions.tsv"
COUNTER = R / "gdt154_counterexamples.tsv"; RESULT = R / "gdt154_result.json"


def read(path):
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def main():
    prediction = json.loads(PRED.read_text(encoding="utf8")); pred = read(PRED_TSV); obs = read(OBS)
    assert prediction["status"] == "FROZEN_BEFORE_TARGET_IMAGE_ACCESS"
    assert [r["target_id"] for r in pred] == [r["target_id"] for r in obs] == ["OSVT01", "OSVT02"]
    assert not any(r["page"].startswith("f84") for r in pred + obs)
    scored = []
    for p, o in zip(pred, obs):
        assert (p["target_id"], p["page"], p["physical_folio"]) == (o["target_id"], o["page"], o["physical_folio"])
        joint_match = int(o["joint_call"] == "POSITIVE")
        scored.append({
            "target_id": p["target_id"], "page": p["page"], "locus": p["locus"], "page_host": p["page_host"],
            "predicted_dark_leaf": p["predicted_dark_leaf"], "observed_dark_leaf": o["dark_leaf_call"],
            "predicted_light_root": p["predicted_light_root"], "observed_light_root": o["light_root_call"],
            "predicted_joint_state": p["predicted_joint_state"], "observed_joint_call": o["joint_call"],
            "joint_prediction_match": joint_match, "observation_provenance": o["observation_provenance"],
            "image_sha256": o["full_image_sha256"], "ownership_scope": p["occurrence_scope"],
        })
    write(SCORED, scored)
    hits = sum(int(r["joint_prediction_match"]) for r in scored)
    if hits == 2: status = "OS_DARK_LEAF_LIGHT_ROOT_GLOSS_PROVISIONAL_LEAD"
    elif hits == 1: status = "OS_DARK_LEAF_LIGHT_ROOT_GLOSS_UNSTABLE_LOCAL_ONLY"
    else: status = "OS_DARK_LEAF_LIGHT_ROOT_GLOSS_REJECTED"
    counter = [
        {"type": "DIRECT_COMPONENT_CONTRADICTION", "item": "OSVT01_f15r", "value": "LIGHT_ROOT_NEGATIVE", "detail": "The author-visible root base and horizontal roots are solid dark red-brown, directly contradicting the frozen light-root component."},
        {"type": "LEAF_AMBIGUITY", "item": "OSVT01_f15r", "value": "DARK_LEAF_UNCERTAIN", "detail": "The pale circular painted region might supply a contrast, but fading and depiction identity make it unsafe to count as a qualifying leaf."},
        {"type": "PAGE_LEVEL_NO_OWNERSHIP", "item": "BOTH_TARGETS", "value": "RUNNING_TEXT", "detail": "The exact chos occurrences are running prose with only page-level plant association, not singular plant-part labels."},
        {"type": "HYPOTHESIS_AWARE_AI_REVIEW", "item": "BOTH_TARGETS", "value": "NOT_INDEPENDENT_HUMAN_CONFIRMATION", "detail": "Direct native inspection occurred after the public freeze but the same AI workflow knew the hypothesis."},
        {"type": "PRIOR_GLOBAL_COUNTEREVIDENCE", "item": "GDT090", "value": "EXACT_HOST_WIDE_VISUAL_DESCRIPTOR_STABILITY_NOT_SUPPORTED", "detail": "The one positive page does not override the earlier global exact-host visual-bundle failure."},
    ]
    write(COUNTER, counter)
    REPORT.write_text(f"""# GDT154 — exact `os` dark-leaf/light-root transfer

## Outcome

**{status}**

The exact frozen conjunction transfers on **{hits}/2** mechanically selected
new Herbal pages.

- **f15r — NEGATIVE.** The root base and long horizontal roots are filled
  dark red-brown, directly contradicting `LIGHT_ROOT`. A possible leaf-tone
  contrast is `UNCERTAIN` because the pale broad painted region is faded and
  its depiction identity is not secure.
- **f27r — POSITIVE.** Three small rounded leaves are conspicuously darker
  green than the main plant's pale turquoise leaves, while both depicted root
  systems are unfilled/light brown relative to those leaves.

The 1/2 split is useful but not a stable gloss. It shows that the original two
pharmaceutical `os` cases can generate one new page-level visual hit, while a
second new page supplies a direct component counterexample. Do not broaden
`os`, discard f15r, or search the remaining three eligible pages as a rescue.
The absence of singular ownership also means the f27r hit cannot identify
which plant or plant part the running-text occurrence concerns.

Both observations are direct hypothesis-aware AI judgments on exact official
Yale canvases after the public freeze, not independent human annotations. No
OCR or automated visual classifier was used.

Failure/instability applies only to the frozen dark-leaf/light-root gloss, not
to `os` as a formal PAGE_HOST. No word, morpheme, POS, sound, language,
plaintext, plant identity, meaning, or translation follows. f84r remained
sealed and was not opened, targeted, retained, joined, or scored.
""", encoding="utf8")
    result = {
        "schema": "GDT154_OS_VISUAL_TRANSFER_RESULT_V1", "status": status,
        "targets": 2, "joint_hits": hits, "joint_failures": 2 - hits,
        "component_counts": {
            "dark_leaf": {state: sum(r["dark_leaf_call"] == state for r in obs) for state in ("POSITIVE", "NEGATIVE", "UNCERTAIN")},
            "light_root": {state: sum(r["light_root_call"] == state for r in obs) for state in ("POSITIVE", "NEGATIVE", "UNCERTAIN")},
        },
        "interpretation": "One of two new page-level exact-chos targets matches the frozen dark-leaf/light-root conjunction; the other directly contradicts the root component, so the gloss is unstable/local only.",
        "claim_ceiling": "Prospective-but-hypothesis-aware page-level exact-gloss instability only; no word, morpheme, POS, sound, language, plaintext, plant identity, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "targeted", "retained", "joined", "scored")},
        "inputs": {path.name: sha(path) for path in (PRED, PRED_TSV, OBS)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in (SCORED, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "hits": hits, "targets": 2}, sort_keys=True))


if __name__ == "__main__": main()

