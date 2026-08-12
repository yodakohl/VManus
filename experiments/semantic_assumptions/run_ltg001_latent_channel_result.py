#!/usr/bin/env python3
"""Run the frozen one-shot LTG001 held-folio manuscript evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ltg001_latent_channel_core import evaluate_panel, fit_channel, load_panel, select_channel


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CAPACITY = RESULTS / "ltg001_latent_channel_capacity.json"
CALIBRATION = RESULTS / "ltg001_latent_channel_calibration.json"
OUT_JSON = RESULTS / "ltg001_latent_channel_result.json"
OUT_ATLAS = RESULTS / "ltg001_latent_channel_atlas.json"
OUT_REPORT = RESULTS / "ltg001_latent_channel_result_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for output in (OUT_JSON, OUT_ATLAS, OUT_REPORT):
        if output.exists():
            raise SystemExit(f"refusing to overwrite {output.name}")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_IDENTIFIABLE_CROSS_FOLIO_CHANNEL":
        raise SystemExit("capacity not PASS")
    if calibration["status"] != "PASS_TARGET_FREE_LATENT_CHANNEL_INSTRUMENT":
        raise SystemExit("calibration not PASS")
    if calibration["real_panel_scored"] is not False:
        raise SystemExit("calibration target isolation drift")

    panel = load_panel(GROUPS)
    evaluation = evaluate_panel(panel, "LTG001_REAL_V1")
    selected, candidates = select_channel(
        panel.family, panel.observations, len(panel.family_names), len(panel.symbol_names),
        "LTG001_REAL_V1|FULL",
    )
    states = []
    for state in range(selected.k):
        emissions = {}
        for edition, name in enumerate(("ZL", "IT", "RF")):
            order = sorted(
                range(len(panel.symbol_names)),
                key=lambda symbol: (-selected.emissions[edition, state, symbol], panel.symbol_names[symbol].encode()),
            )[:5]
            emissions[name] = [
                {"suffix": panel.symbol_names[symbol], "probability": float(selected.emissions[edition, state, symbol])}
                for symbol in order
            ]
        family_order = sorted(
            range(len(panel.family_names)),
            key=lambda fam: (-selected.pi[fam, state], panel.family_names[fam]),
        )[:8]
        states.append({
            "latent_state": f"H{state + 1:02d}",
            "top_emissions_by_edition": emissions,
            "top_family_priors": [
                {"family": panel.family_names[fam], "probability": float(selected.pi[fam, state])}
                for fam in family_order
            ],
        })
    atlas = {
        "experiment": "LTG001_ANONYMOUS_LATENT_CHANNEL_ATLAS",
        "selected_k_full_panel_bic": selected.k,
        "states": states,
        "candidate_bic": {str(fit.k): fit.bic for fit in candidates},
        "claim_ceiling": "Anonymous statistical suffix states only; not physical glyphs, allographs, sounds, letters, words, language, cipher, plaintext, meanings, or translations.",
    }
    OUT_ATLAS.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = evaluation["summary"]
    result = {
        "experiment": "LTG001_LATENT_TRANSCRIPTION_CHANNEL_RESULT",
        "status": summary["decision"],
        "inputs": {
            path.name: {"sha256": sha(path), "bytes": path.stat().st_size}
            for path in (HERE / "LTG001_LATENT_TRANSCRIPTION_CHANNEL_METHOD.md", HERE / "ltg001_latent_channel_core.py", Path(__file__).resolve(), GROUPS, CAPACITY, CALIBRATION)
        },
        "counts": {
            "strict_positions": len(panel.family),
            "physical_folios": len(set(panel.folio)),
            "ambiguous_events": summary["event_count"],
            "ambiguous_folios": summary["folio_count"],
            "unseen_context_events": summary["unseen_context_events"],
        },
        "fold_models": evaluation["fold_models"],
        "summary": summary,
        "folio_gain_bits": evaluation["folio_gain"],
        "full_panel_model": {
            "selected_k": selected.k,
            "log_likelihood": selected.log_likelihood,
            "bic": selected.bic,
            "restart": selected.restart,
            "iterations": selected.iterations,
            "candidate_bic": {str(fit.k): fit.bic for fit in candidates},
        },
        "outputs": {OUT_ATLAS.name: sha(OUT_ATLAS)},
        "claim_ceiling": (
            "A pass establishes only a transferable anonymous model of manual-reading variation. "
            "No preferred reading, physical glyph identity, allography, sound, alphabet, word, "
            "language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    currier = summary["currier_gain_bits"]
    report = f"""# LTG001 latent transcription-channel result

Status: **{result['status']}**.

Across **{summary['event_count']:,}** held-folio events where the two predictor
readings disagree, the anonymous latent channel gains
**{summary['equal_folio_gain_bits']:+.6f} bit/event** over the direct train-only
triplet lookup. **{summary['positive_folios']}/{summary['folio_count']}** folios
are positive (exact sign p = **{summary['folio_sign_p']:.8f}**).

Currier A/B gains are **{currier.get('A', float('nan')):+.6f}** and
**{currier.get('B', float('nan')):+.6f}** bits. Deleting the dominant
`(B1,B1,Ba)` RF convention gives
**{summary['dominant_policy_deleted_gain_bits']:+.6f}**; the
**{summary['unseen_context_events']}** train-unseen exact contexts give
**{summary['unseen_context_gain_bits']:+.6f}**. The minimum leave-one-folio
aggregate is **{summary['minimum_leave_one_folio_gain_bits']:+.6f}**.

Full-panel BIC selects **K={selected.k}** anonymous states. They remain `H01`,
`H02`, ... and are published only as an inspectable observation-channel atlas.

This result does not choose a physically correct transcription or establish a
glyph identity, allograph, sound, alphabet, word, language, cipher, plaintext,
meaning, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": summary, "selected_k": selected.k}, sort_keys=True))


if __name__ == "__main__":
    main()
