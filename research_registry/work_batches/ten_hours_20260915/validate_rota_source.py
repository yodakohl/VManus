#!/usr/bin/env python3
"""Independent interval lookup for the declared source-only conditional periods.

Does not import the producer, read target data, or certify historical durations.
"""
import bisect
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    source_path = HERE / "ROTA_SOURCE_EVENTS.json"
    s = json.loads(source_path.read_text())
    original = HERE / "ROTA_SOURCE_EVENTS_PRECOMPARISON.json"
    assert hashlib.sha256(original.read_bytes()).hexdigest() == s["independent_comparison"]["own_event_matrix_precomparison_sha256"]
    assert json.loads(original.read_text()) == s["events"]
    assert digest(s["events"]) == s["independent_comparison"]["own_event_matrix_precomparison_sha256"]
    for name, key in [("ROTA_PES_RULES_INDEPENDENT.json", "independent_json_sha256"), ("ROTA_PES_RULES_INDEPENDENT.md", "independent_md_sha256")]:
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == s["independent_comparison"][key]
    assert hashlib.sha256((HERE / "rota_source_events.py").read_bytes()).hexdigest() == s["code_sha256"]
    parts = {p: [e for e in s["events"] if e["part"] == p] for p in ["M", "P1", "P2"]}
    assert [len(parts[p]) for p in parts] == [79, 9, 9]
    assert len({e["id"] for e in s["events"]}) == 97
    assert [e["note_ordinal_in_part"] for e in parts["M"] if e["kind"] == "note"] == list(range(1, 74))
    rests_after = []
    notes = 0
    for e in parts["M"]:
        if e["kind"] == "note":
            notes += 1
        else:
            rests_after.append(notes)
    assert rests_after == [14, 27, 30, 43, 56, 73]
    signature = lambda e: (e["kind"], e["visible_mark_class"], (e["pitch_reading"] or {}).get("diatonic_steps_above_c_reference"), "joined_group" in e)
    a, b = list(map(signature, parts["P1"])), list(map(signature, parts["P2"]))
    assert a[5:] + a[:5] == b
    checked = []
    for branch, output in zip(s["documentary_duration_branches"], s["executions"], strict=True):
        assert branch["id"] == output["branch"]
        durations = {k: Fraction(v) for k, v in s["baseline_conditional_duration_breves"].items()}
        durations.update({k: Fraction(v) for k, v in branch["changes"].items()})
        assert set(durations) == {e["id"] for e in s["events"]}

        def timeline(events):
            ends, values = [], []
            t = Fraction(0)
            for e in events:
                assert durations[e["id"]] > 0
                t += durations[e["id"]]
                ends.append(t)
                values.append(None if e["kind"] == "pause" else e["pitch_reading"]["midi_under_c4_octave_convention"])
            return ends, values

        def at(table, time):
            ends, values = table
            return values[bisect.bisect_right(ends, time % ends[-1])]

        tables = {p: timeline(events) for p, events in parts.items()}
        delay = sum(durations[e["id"]] for e in parts["M"][:9])
        assert str(delay) == output["entry_delay_breves"]
        assert {p: str(t[0][-1]) for p, t in tables.items()} == output["written_part_lengths_breves"]
        rotation = sum(durations[e["id"]] for e in parts["P1"][:5])
        assert [int(rotation * 2)] == output["pes2_equals_pes1_rotation_ticks"]
        for tick in range(int(tables["P1"][0][-1] * 2)):
            assert at(tables["P1"], Fraction(tick, 2) + rotation) == at(tables["P2"], Fraction(tick, 2))

        def performance(k, start, count, current_tables, current_delay):
            rows = []
            for tick in range(start, start + count):
                t = Fraction(tick, 2)
                row = [None if t < v * current_delay else at(current_tables["M"], t - v * current_delay) for v in range(k)]
                row += [at(current_tables[p], t) for p in ["P1", "P2"]]
                rows.append(row)
            return rows

        for result in output["execution"]:
            k, t0, count = result["upper_voices"], result["start_tick"], result["period_ticks"]
            for table in tables.values():
                assert Fraction(count, 2) % table[0][-1] == 0
            assert Fraction(t0, 2) >= (k - 1) * (delay + 1)
            baseline = performance(k, t0, count, tables, delay)
            assert digest(baseline) == result["source_branch_output_sha256"]
            for rival in result["rivals"]:
                name = rival["rival"]
                alt, d = dict(tables), delay
                if name == "entry_shift_plus_one_breve":
                    d += 1
                elif name == "upper_pes_rest_phase_swap":
                    alt["P1"] = timeline(parts["P1"][:-2] + list(reversed(parts["P1"][-2:])))
                elif name == "reverse_main_event_cycle":
                    alt["M"] = timeline(list(reversed(parts["M"])))
                else:
                    raise AssertionError(name)
                observed = performance(k, t0, count, alt, d)
                assert digest(observed) == rival["rival_output_sha256"]
                cells = [(t, v, x, y) for t, (xs, ys) in enumerate(zip(baseline, observed, strict=True)) for v, (x, y) in enumerate(zip(xs, ys, strict=True)) if x != y]
                assert len(cells) == rival["different_pitch_or_rest_cells"]
                assert sum((x is None) != (y is None) for _, _, x, y in cells) == rival["different_rest_mask_cells"]
                t, v, x, y = cells[0]
                assert rival["first_difference"] == {"sample_tick": t, "voice_index": v, "base_midi_or_rest": x, "rival_midi_or_rest": y}
                differences = 0
                for xs, ys in zip(baseline, observed, strict=True):
                    for i, j in itertools.combinations(range(k + 2), 2):
                        ix = None if xs[i] is None or xs[j] is None else xs[j] - xs[i]
                        iy = None if ys[i] is None or ys[j] is None else ys[j] - ys[i]
                        differences += ix != iy
                assert differences == rival["different_signed_interval_or_undefined_cells"]
                checked.append([branch["id"], k, name])
    result = {"status": "PASS", "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(), "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "written_events": 97, "conditional_performances": 12, "rival_comparisons": checked, "native_numeric_duration_certification": False, "initialization_comparison": "not performed; complete steady periods only", "target_access": False, "translated_words": 0}
    (HERE / "ROTA_SOURCE_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rival_comparisons"}))


if __name__ == "__main__":
    main()
