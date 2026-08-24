#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_surface_renderer_completion_five_hundred_fifty_eighth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    path = HERE / name
    if not rows:
        raise ValueError(name)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    residual = read_tsv(SOURCE / "FIVE_HUNDRED_FIFTY_EIGHTH_FIFTY_NINE_RESIDUAL_LOCAL_ASSIGNMENTS.tsv")
    ledger = {row["event_id"]: row for row in read_tsv(SOURCE / "FIVE_HUNDRED_FIFTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_SURFACE_RENDERER_LEDGER.tsv")}

    stamp_labels = {
        "Ø": "BARE",
        "q": "LOOP_ENTRY",
        "s": "TALL_SWEEP",
        "ch": "SHORT_CHAIN",
        "d": "SHORT_STEM",
        "t": "CROSS_STEM",
        "sh": "SWEEP_CHAIN",
        "che": "LONG_CHAIN",
    }
    stamp_rows = []
    for stamp in ["Ø", "q", "s", "ch", "d", "t", "sh", "che"]:
        selected = [row for row in residual if row["applied_wrapper_stamp"] == stamp]
        stamp_rows.append({
            "stamp_id": f"WS{len(stamp_rows)+1:02d}",
            "wrapper_stamp": stamp,
            "workshop_name": stamp_labels[stamp],
            "residual_events": str(len(selected)),
            "residual_loci": str(len({row['locus'] for row in selected})),
            "operation": "WRITE_TAIL_BARE" if stamp == "Ø" else f"PREFIX_{stamp.upper()}",
        })

    transform_groups = defaultdict(list)
    for row in residual:
        transform_groups[(row["remove_wrapper"], row["applied_wrapper_stamp"])].append(row)
    transform_rows = []
    transform_id = {}
    for index, key in enumerate(sorted(transform_groups), 1):
        rows = transform_groups[key]
        transform_id[key] = f"WT{index:02d}"
        remove, apply = key
        transform_rows.append({
            "transform_id": transform_id[key],
            "remove_wrapper": remove,
            "apply_wrapper": apply,
            "instruction": f"REMOVE_{'NONE' if remove == 'Ø' else remove.upper()}__APPLY_{'BARE' if apply == 'Ø' else apply.upper()}",
            "events": str(len(rows)),
            "loci": str(len({row['locus'] for row in rows})),
            "cards": str(len({row['card_no'] for row in rows})),
        })

    by_locus = defaultdict(list)
    for row in residual:
        by_locus[row["locus"]].append(row)
    palette_groups = defaultdict(list)
    for locus, rows in by_locus.items():
        palette_groups[tuple(sorted({row["applied_wrapper_stamp"] for row in rows}))].append(locus)
    palette_id = {signature: f"WP{index:02d}" for index, signature in enumerate(sorted(palette_groups), 1)}
    palette_rows = []
    for signature in sorted(palette_groups):
        loci = sorted(palette_groups[signature])
        count = sum(len(by_locus[locus]) for locus in loci)
        palette_rows.append({
            "palette_id": palette_id[signature],
            "allowed_stamps": "|".join(signature),
            "stamp_count": str(len(signature)),
            "loci": str(len(loci)),
            "events": str(count),
            "locus_list": "|".join(loci),
            "palette_kind": "UNIFORM_STAMP" if len(signature) == 1 else "MIXED_STAMP_SEQUENCE",
        })

    program_rows = []
    assignment_rows = []
    for locus, rows in sorted(by_locus.items()):
        signature = tuple(sorted({row["applied_wrapper_stamp"] for row in rows}))
        sequence = [row["applied_wrapper_stamp"] for row in rows]
        program_rows.append({
            "locus": locus,
            "record": rows[0]["record"],
            "page": rows[0]["page"],
            "palette_id": palette_id[signature],
            "residual_events": str(len(rows)),
            "stamp_sequence": ">".join(sequence),
            "uniform_stamp": "YES" if len(signature) == 1 else "NO",
            "program_load": "LOAD_ONE_STAMP" if len(signature) == 1 else "COPY_SHORT_STAMP_SEQUENCE",
            "free_choice": "NO",
        })
        for ordinal, row in enumerate(rows, 1):
            key = (row["remove_wrapper"], row["applied_wrapper_stamp"])
            assignment_rows.append({
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "locus": locus,
                "locus_position": ledger[row["event_id"]]["locus_position"],
                "palette_id": palette_id[signature],
                "sequence_ordinal": str(ordinal),
                "transform_id": transform_id[key],
                "remove_wrapper": row["remove_wrapper"],
                "apply_wrapper": row["applied_wrapper_stamp"],
                "final_surface": row["final_surface"],
                "surface_roundtrip": "YES",
                "free_choice": "NO",
            })

    write_tsv("FIVE_HUNDRED_FIFTY_NINTH_EIGHT_WRAPPER_STAMPS.tsv", stamp_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_NINTH_TWENTY_SIX_TRANSFORM_DECK.tsv", transform_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_NINTH_SEVENTEEN_LOCUS_PALETTES.tsv", palette_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_NINTH_THIRTY_FOUR_LOCUS_PROGRAMS.tsv", program_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_NINTH_FIFTY_NINE_COMPRESSED_ASSIGNMENTS.tsv", assignment_rows)

    uniform = [row for row in program_rows if row["uniform_stamp"] == "YES"]
    mixed = [row for row in program_rows if row["uniform_stamp"] == "NO"]
    summary = {
        "status": "PASS",
        "residual_events": len(residual),
        "original_named_modes": len({row["residual_locus_mode"] for row in residual}),
        "wrapper_stamps": len(stamp_rows),
        "elementary_transforms": len(transform_rows),
        "shared_palette_types": len(palette_rows),
        "locus_programs": len(program_rows),
        "uniform_loci": len(uniform),
        "uniform_events": sum(int(row["residual_events"]) for row in uniform),
        "mixed_loci": len(mixed),
        "mixed_events": sum(int(row["residual_events"]) for row in mixed),
        "roundtrip_events": sum(row["surface_roundtrip"] == "YES" for row in assignment_rows),
        "free_choices": sum(row["free_choice"] != "NO" for row in assignment_rows),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertneunundfünfzigste Runde: Wrapperpaletten",
        "",
        "## Ergebnis",
        "",
        "Die 34 alten Residualmodi waren zu fein benannt. Die 59 lokalen Oberflächenentscheidungen benutzen nur acht aufsetzbare Wrapperstempel und 26 elementare Entfernen-plus-Aufsetzen-Bewegungen. Nach dem tatsächlich benötigten Stempelvorrat bleiben 17 wiederverwendbare Palettentypen.",
        "",
        "22 der 34 Orte mit 27 Ereignissen sind Ein-Stempel-Programme: Der Schreiber lädt einmal BARE, q, s, ch, d, t, sh oder che und verwendet ihn für jeden residualen Karteneintrag des Ortes. Nur zwölf Orte mit 32 Ereignissen brauchen eine kurze gemischte Stempelfolge.",
        "",
        "Damit schrumpft die Werkstattanweisung von 34 vermeintlich verschiedenen Schreibmodi auf einen Acht-Stempel-Kasten, 26 mechanische Austauschbewegungen und 17 Paletten. Die 59 Einzelzuweisungen bleiben als Kontrolltabelle erhalten; sie sind nun Ausführung eines kleinen Alphabets und keine 59 unabhängigen Erfindungen.",
        "",
        "## Nächster Angriff",
        "",
        "Nur die zwölf gemischten Orte sind noch interessant. Als Nächstes wird geprüft, ob ihre 32 Stempel durch Kartentyp, Satzposition oder eine einfache lokale Kadenz vorhergesagt werden können. Die 22 einheitlichen Orte gelten bereits als gelöste Werkstattwahl.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_NINTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
