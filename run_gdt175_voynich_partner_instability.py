#!/usr/bin/env python3
"""Apply the publicly frozen GDT175 control diagnostic to Voynich."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from run_gdt174_voynich_calibrated_fingerprint import hpr2_panel
from run_gdt175_control_partner_instability import csha, make_events, scope_metrics, sha, write_tsv

R = Path(__file__).resolve().parent
DESIGN = R / "gdt175_design.json"
CONTROL = R / "gdt175_control_result.json"
CONTROL_VALIDATION = R / "gdt175_control_validation.json"
CONTROL_BINS = R / "gdt175_control_bin_summary.tsv"
CONTROL_RUNNER = R / "run_gdt175_control_partner_instability.py"
PANEL_RUNNER = R / "run_gdt174_voynich_calibrated_fingerprint.py"
HPR2 = R / "gdt062_right_family_inventory.tsv"
FRAMES = R / "gdt046_line_frames.tsv"
PARENT = R / "gdt174_result.json"
METHOD = R / "GDT175_RECURRENCE_PARTNER_INSTABILITY_METHOD.md"
HOSTS = R / "gdt175_voynich_host_metrics.tsv"
BINS = R / "gdt175_voynich_bin_summary.tsv"
SCOPES = R / "gdt175_voynich_scope_summary.tsv"
SIDE = R / "gdt175_side_by_side.tsv"
COUNTER = R / "gdt175_counterexamples.tsv"
REPORT = R / "GDT175_RECURRENCE_PARTNER_INSTABILITY_REPORT.md"
RESULT = R / "gdt175_result.json"


def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def position(value: float, interval: list[float]) -> str:
    if value < interval[0]:
        return "BELOW_CONTROL_RANGE"
    if value > interval[1]:
        return "ABOVE_CONTROL_RANGE"
    return "INSIDE_CONTROL_RANGE"


def powered_registers(scope_rows: list[dict]) -> list[dict]:
    return [row for row in scope_rows if row["scope_type"] == "REGISTER" and int(row["powered"])]


def diagnose(global_row: dict, global_bins: list[dict], scope_rows: list[dict], envelopes: dict) -> tuple[str, dict]:
    bins = [row for row in global_bins if int(row["powered"])]
    inside = []
    unstable = []
    for row in bins:
        envelope = envelopes[row["occurrence_bin"]]
        inside.append(all(envelope[key][0] <= float(row[key]) <= envelope[key][1] for key in ("held_bits_per_event", "mean_overlap_excess", "mean_jsd_excess")))
        unstable.append(
            float(row["held_bits_per_event"]) < envelope["held_bits_per_event"][0]
            and (
                float(row["mean_overlap_excess"]) < envelope["mean_overlap_excess"][0]
                or float(row["mean_jsd_excess"]) > envelope["mean_jsd_excess"][1]
            )
        )
    registers = powered_registers(scope_rows)
    aggregate_register_gain = sum(float(row["held_gain_bits"]) for row in registers)
    positive_registers = sum(float(row["held_bits_per_event"]) > 0 for row in registers)
    negative_registers = sum(float(row["held_bits_per_event"]) < 0 for row in registers)
    details = {
        "powered_bins": len(bins),
        "bins_inside_all_control_envelopes": sum(inside),
        "bins_meeting_instability_rule": sum(unstable),
        "powered_registers": len(registers),
        "positive_registers": positive_registers,
        "negative_registers": negative_registers,
        "aggregate_powered_register_gain_bits": aggregate_register_gain,
    }
    if len(bins) >= 3 and all(inside):
        return "SAMPLING_FREQUENCY_SUFFICIENT", details
    if (
        float(global_row["held_gain_bits"]) < 0
        and len(registers) >= 3
        and positive_registers / len(registers) >= 0.75
        and aggregate_register_gain > 0
    ):
        return "REGISTER_MIXTURE_DOMINANT", details
    if (
        float(global_row["held_gain_bits"]) < 0
        and len(bins) >= 3
        and sum(unstable) / len(bins) >= 0.75
        and len(registers) >= 3
        and negative_registers / len(registers) >= 0.75
    ):
        return "FOLIO_CONDITIONED_INSTABILITY_SUPPORTED", details
    return "MIXED_OR_UNRESOLVED", details


def main() -> None:
    design = json.loads(DESIGN.read_text())
    control = json.loads(CONTROL.read_text())
    control_validation = json.loads(CONTROL_VALIDATION.read_text())
    parent = json.loads(PARENT.read_text())
    assert design["status"] == "DIAGNOSTIC_FROZEN_BEFORE_CONTROL_CALIBRATION"
    assert control["status"] == "CONTROL_CALIBRATION_FROZEN_BEFORE_VOYNICH_SCORING"
    assert control_validation["status"] == "PASS_INDEPENDENT_CONTROL_SOURCE_RECONSTRUCTION"
    assert parent["status"] == "VOYNICH_PARTLY_OUTSIDE_FROZEN_SYNTHETIC_ENVELOPE"
    assert control["firewall"]["voynich_inputs"] == 0 and control["firewall"]["build_b3"] is False
    assert sha(CONTROL_BINS) == control["outputs"][CONTROL_BINS.name]
    rows, census = hpr2_panel()
    assert census == parent["census"] and census["groups"] == 8448 and census["folios"] == 91
    assert not any(str(row["page"]).startswith("f84") or str(row["locus"]).startswith("f84") for row in rows)
    events = make_events(rows)
    assert len(events) == 7305
    line_section = {str(row["physical_line_id"]): str(row["section"]) for row in rows}
    assert all(line_section[str(row["physical_line_id"])] == str(row["section"]) for row in rows)
    for event in events:
        event["section"] = line_section[event["line_id"]]
    all_host_rows, scope_rows, bin_rows = [], [], []
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 1)) as executor:
        host, scope, bins = scope_metrics("VOYNICH", "GLOBAL", "ALL", rows, events, executor)
        scope["physical_folios"] = census["folios"]
        for item in bins: item["physical_folios"] = census["folios"]
        all_host_rows.extend(host); scope_rows.append(scope); bin_rows.extend(bins)
        for register in sorted({str(row["register"]) for row in rows}):
            subrows = [row for row in rows if str(row["register"]) == register]
            subevents = [event for event in events if event["register"] == register]
            host, scope, bins = scope_metrics("VOYNICH", "REGISTER", register, subrows, subevents, executor)
            folios = len({str(row["folio_id"]) for row in subrows})
            scope["physical_folios"] = folios
            for item in bins: item["physical_folios"] = folios
            all_host_rows.extend(host); scope_rows.append(scope); bin_rows.extend(bins)
        for section in sorted({str(row["section"]) for row in rows}):
            subrows = [row for row in rows if str(row["section"]) == section]
            subevents = [event for event in events if event["section"] == section]
            host, scope, bins = scope_metrics("VOYNICH", "SECTION", section, subrows, subevents, executor)
            folios = len({str(row["folio_id"]) for row in subrows})
            scope["physical_folios"] = folios
            for item in bins: item["physical_folios"] = folios
            all_host_rows.extend(host); scope_rows.append(scope); bin_rows.extend(bins)
    all_host_rows.sort(key=lambda row: (row["scope_type"], row["scope_value"], row["occurrence_bin"], row["host"]))
    scope_rows.sort(key=lambda row: (row["scope_type"], row["scope_value"]))
    bin_rows.sort(key=lambda row: (row["scope_type"], row["scope_value"], row["occurrence_bin"]))
    write_tsv(HOSTS, all_host_rows); write_tsv(BINS, bin_rows); write_tsv(SCOPES, scope_rows)

    control_bins = read_tsv(CONTROL_BINS)
    global_voynich = next(row for row in scope_rows if row["scope_type"] == "GLOBAL")
    global_bins = [row for row in bin_rows if row["scope_type"] == "GLOBAL"]
    decision, decision_details = diagnose(global_voynich, global_bins, scope_rows, control["control_envelopes"])
    side_rows = []
    for bin_name in ("N2_4", "N5_15", "N16_63", "N64_PLUS"):
        for row in [x for x in control_bins if x["scope_type"] == "GLOBAL" and x["occurrence_bin"] == bin_name]:
            side_rows.append({**row, "source": "FROZEN_CONTROL", "held_placement": "CALIBRATION", "overlap_placement": "CALIBRATION", "jsd_placement": "CALIBRATION"})
        row = next(x for x in global_bins if x["occurrence_bin"] == bin_name)
        envelope = control["control_envelopes"][bin_name]
        side_rows.append({**row, "source": "VOYNICH_APPLICATION", "held_placement": position(float(row["held_bits_per_event"]), envelope["held_bits_per_event"]), "overlap_placement": position(float(row["mean_overlap_excess"]), envelope["mean_overlap_excess"]), "jsd_placement": position(float(row["mean_jsd_excess"]), envelope["mean_jsd_excess"])})
    write_tsv(SIDE, side_rows)

    counter_rows = [
        {"counterexample": "GDT174_NEXT_HOST_NEGATIVE", "observation": f"GDT174 all-host gain was {parent['voynich']['next_host_gain_bits']:.6f} bits on 91/91 nonpositive folios.", "implication": "Motivates diagnosis but is not itself a new GDT175 result."},
        {"counterexample": "CONTROL_HIGH_FREQUENCY_GAIN_CAN_BE_NEGATIVE", "observation": "The frozen N64_PLUS control envelope includes negative held gain.", "implication": "A negative high-count Voynich bin alone cannot diagnose folio conditioning."},
        {"counterexample": "COVERAGE_IS_NOT_RECURRENCE_MASS", "observation": f"Eligible next-event coverage is {float(global_voynich['event_coverage']):.6f}; GDT174 recurrent group mass was {parent['voynich']['recurrent_host_mass']:.6f}.", "implication": "These denominators are separate and must not be merged."},
        {"counterexample": "SECTION_IS_SENSITIVITY_ONLY", "observation": "Section scopes reuse the frozen metric but are not part of the preregistered diagnosis gate.", "implication": "A section-local improvement cannot override a failed register diagnosis."},
    ]
    write_tsv(COUNTER, counter_rows)

    register_rows = [row for row in scope_rows if row["scope_type"] == "REGISTER"]
    section_rows = [row for row in scope_rows if row["scope_type"] == "SECTION" and int(row["powered"])]
    report = [
        "# GDT175 — recurrence with next-partner instability",
        "",
        f"Status: **{decision}**.",
        "",
        f"The publicly frozen GDT175 diagnostic was applied unchanged to {census['groups']} PAGE_HOST groups on {census['lines']} complete physical lines and {census['folios']} folios. It yields {len(events)} within-line next events. Every f84* source row was rejected before retention; no f84r row was retained, joined, or scored.",
        "",
        "## Global result by frozen occurrence bin",
        "",
        "| bin | hosts | covered events | held bits/event | overlap excess | JSD excess | control placement (held / overlap / JSD) |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in side_rows:
        if row["system"] != "VOYNICH": continue
        report.append(f"| {row['occurrence_bin']} | {row['eligible_hosts']} | {row['eligible_next_events']} | {float(row['held_bits_per_event']):.6f} | {float(row['mean_overlap_excess']):.6f} | {float(row['mean_jsd_excess']):.6f} | {row['held_placement']} / {row['overlap_placement']} / {row['jsd_placement']} |")
    report += [
        "",
        f"Overall eligible-event coverage is {float(global_voynich['event_coverage']):.6f}. The global held gain is {float(global_voynich['held_gain_bits']):.6f} bits ({float(global_voynich['held_bits_per_event']):.6f} bits/event). Coverage is reported independently of GDT174's ~91% recurrent-group mass.",
        "",
        "## Register and section diagnosis",
        "",
        "| register | folios | hosts | events | held bits/event | powered |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in register_rows:
        value = "NA" if row["held_bits_per_event"] == "NA" else f"{float(row['held_bits_per_event']):.6f}"
        report.append(f"| {row['scope_value']} | {row['physical_folios']} | {row['eligible_hosts']} | {row['eligible_next_events']} | {value} | {row['powered']} |")
    report += [
        "",
        f"Powered registers: {decision_details['powered_registers']}; positive: {decision_details['positive_registers']}; negative: {decision_details['negative_registers']}. Powered section sensitivities: {len(section_rows)}. The frozen decision is therefore **{decision}**.",
        "",
        "## What explains the GDT174 negative NEXT_HOST result?",
        "",
        "Register mixture is not the dominant explanation: every one of the five powered register-specific gains remains negative. Count/frequency alone is also not sufficient across the panel: the N2_4 and N5_15 bins are below the held-gain and overlap control envelopes and above the JSD envelope. But the preregistered folio-instability diagnosis requires at least three of four bins, and only those two qualify. N16_63 has negative held gain without the matched overlap/JSD signature, while N64_PLUS has held gain inside the synthetic envelope despite unusually low overlap and high divergence.",
        "",
        "The useful conclusion is therefore heterogeneous partner instability: a folio-conditioned signal is concentrated in low-to-mid recurrence hosts, while the two high-count regimes do not form one coherent mechanism. This rejects a simple register-mixture story and a single pooled sampling story, but it does not justify inventing a new architecture or B3.",
        "",
        "The exact per-host rows include partner-set overlap, Jeffreys-smoothed pairwise JSD, pooled and within-folio target entropy, and 256-world host-specific sampling nulls. `gdt175_side_by_side.tsv` retains the three unscaled control rows beside Voynich for every count bin.",
        "",
        "## Claim ceiling",
        "",
        "This diagnoses recurrence-with-partner-instability on the frozen panel. It creates no architecture, codebook, word, language, morphology, role, meaning, plaintext, or translation. B3 was not built.",
    ]
    REPORT.write_text("\n".join(report) + "\n")
    result = {
        "schema": "GDT175_VOYNICH_PARTNER_INSTABILITY_RESULT_V1",
        "status": decision,
        "decision_details": decision_details,
        "census": {**census, "next_events": len(events), "eligible_hosts_global": int(global_voynich["eligible_hosts"]), "eligible_events_global": int(global_voynich["eligible_next_events"]), "eligible_event_coverage": float(global_voynich["event_coverage"])},
        "global": global_voynich,
        "global_bins": global_bins,
        "powered_registers": [row for row in register_rows if int(row["powered"])],
        "powered_sections": section_rows,
        "control_envelopes_used_unchanged": control["control_envelopes"],
        "chronology": {"design_commit": "f6fb14c", "control_calibration_commit": "6817afd", "voynich_scored_after_both_public_freezes": True},
        "inputs": {path.name: sha(path) for path in (DESIGN, CONTROL, CONTROL_VALIDATION, CONTROL_BINS, HPR2, FRAMES, PARENT, METHOD)},
        "outputs": {path.name: sha(path) for path in (HOSTS, BINS, SCOPES, SIDE, COUNTER, REPORT)},
        "commitments": {"host_rows_content_sha256": csha(all_host_rows), "bin_rows_content_sha256": csha(bin_rows), "scope_rows_content_sha256": csha(scope_rows), "side_rows_content_sha256": csha(side_rows)},
        "implementation": {Path(__file__).name: sha(Path(__file__)), CONTROL_RUNNER.name: sha(CONTROL_RUNNER), PANEL_RUNNER.name: sha(PANEL_RUNNER)},
        "build_b3": False,
        "no_rescaling": True,
        "no_tuning_to_voynich": True,
        "f84_source_rows_rejected_before_retention": census["f84_hpr2_rows_rejected"] + census["f84_frame_rows_rejected"],
        "f84_rows_retained": 0,
        "f84r_access": False,
        "claim_ceiling": "Partner-instability diagnosis only; no architecture codebook word language morphology role meaning plaintext or translation.",
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": decision, "census": result["census"], "global": global_voynich, "decision_details": decision_details}, sort_keys=True))


if __name__ == "__main__":
    main()
