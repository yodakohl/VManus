#!/usr/bin/env python3
"""Build one complete WHEN-WHAT-HOW workshop dossier."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NOUN_LOAD = ROOT / "experiments/yolo/sidequest_semantic_noun_load_twenty_sixth_edition/TWENTY_SIXTH_116_NOUN_LOAD_AUDIT.tsv"
BALANCED = ROOT / "experiments/yolo/sidequest_semantic_balanced_continuous_twenty_seventh_edition/TWENTY_SEVENTH_11_BALANCED_RECORDS.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_thirty_sixth_edition/THIRTY_SIXTH_142_SPOKEN_LOCI.tsv"
COPIES = ROOT / "experiments/yolo/sidequest_semantic_scribe_idiom_copybook_twenty_ninth_edition/TWENTY_NINTH_68_SCRIBE_IDIOM_COPIES.tsv"


STEP_READINGS = {
    "H3-S001": "Nimm ausgewähltes Material der abgebildeten Pflanze, bringe es zur Arbeitsstelle, wringe es aus, lasse den Auszug bis zum Sollstand stehen, seihe nach und stelle den sichtbaren klaren Anteil beiseite.",
    "H3-S002": "Behalte eine Portion des frischen Pflanzenmaterials für einen zweiten Ansatz zurück.",
    "H3-S003": "Nimm den ersten Auszug wieder auf, bearbeite ihn weiter und miss die vorgesehene Gebrauchsportion ab.",
    "H3-S004": "Nimm das zurückbehaltene Material als nächsten Posten, beginne den Fortsetzungsgang und halte die zweite Bereitung bereit.",
    "B2-S001": "Spüle oder übertrage den ersten Gang an den oberen Paarbecken und schließe diesen kurzen Schritt.",
    "B2-S002": "Führe die Übertragung weiter, stelle die erste Charge örtlich beiseite und schließe.",
    "B2-S003": "Gib eine abgemessene Portion ein, halte sie als aktiven Posten länger in der Station und schließe.",
    "B2-S004": "Setze die Charge an der bezeichneten oberen Station an, führe sie durch den örtlichen Ausgang weiter, halte sie länger und trenne sie am Ende ab.",
    "B2-S005": "Führe den Posten zum zweiten Lauf, sammle bis zum Sollwert, leite ihn durch die verbundenen Gänge, halte die Einstellung, wärme länger und führe den Rest ab.",
    "B2-S006": "Nimm den vorbereiteten Folgeposten, setze ihn am Ziel an, führe ihn kurz durch und halte ihn als laufenden Posten verfügbar.",
    "B2-S007": "Beginne am sichtbaren Mittelknoten eine neue örtliche Charge, lasse sie kurz absetzen und schließe.",
    "B2-S008": "Nimm den folgenden Sollwert, setze von der bezeichneten Quelle an, lasse die Charge stehen und schließe.",
    "B2-S009": "Führe denselben Absetzgang weiter und schließe ihn.",
    "B2-S010": "Halte die Charge länger, setze denselben Posten weiter, öffne den örtlichen Ausgang und prüfe das sichtbare Ergebnis.",
    "B2-S011": "Gib an der mittleren rechten Station eine Portion aus derselben Quelle und danach eine zweite Portion ein; halte länger und schließe.",
    "B2-S012": "Ziehe an der mittleren Station den sichtbaren Anteil ab; beginne nach dem Bildwechsel im unteren Mehrfigurenfeld einen neuen Posten, halte ihn bereit, temperiere länger, leite ihn weiter, miss ihn und vollende den Gang.",
    "B2-S013": "Führe im unteren Feld die verbrauchte Charge ab und schließe.",
    "B2-S014": "Führe vom bezeichneten unteren Ausgang weiter; der Posten bleibt für den nächsten Schritt offen.",
    "B2-S015": "Nimm an der Randstation den sichtbaren Ablauf als Eingang, halte den neuen Posten länger und schließe.",
    "B2-S016": "Führe zum Ziel und von der Quelle ab, teile den Posten, stelle ihn auf Sollmaß, nimm den längeren Folgeposten, setze ihn kurz ein und schließe.",
    "B2-S017": "Halte den Posten kurz am Ziel, führe ihn zur zweiten Zielöffnung und schließe.",
    "B2-S018": "Lasse den örtlichen Einsatz länger wirken und schließe.",
    "B2-S019": "Wasche den örtlichen Posten und schließe.",
    "B2-S020": "Führe den nächsten längeren Einsatzgang aus und schließe.",
    "B2-S021": "Halte den abschließenden Einsatz länger und schließe.",
    "B2-S022": "Führe den verbleibenden Rest in den Schlussgang und schließe.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source_steps = [row for row in read_tsv(NOUN_LOAD) if row["record_id"] in {"H3", "B2"}]
    if {row["statement_id"] for row in source_steps} != set(STEP_READINGS):
        raise RuntimeError("worked-step inventory does not match H3+B2")
    steps = []
    previous_owner = None
    for ordinal, row in enumerate(source_steps, 1):
        phase = "WHAT" if row["record_id"] == "H3" else "HOW"
        owner_reset = "YES" if previous_owner is not None and row["image_owner"] != previous_owner else "NO"
        previous_owner = row["image_owner"]
        steps.append({
            "job_step": ordinal,
            "phase": phase,
            "statement_id": row["statement_id"],
            "page": row["page"],
            "image_owner": row["image_owner"],
            "owner_reset": owner_reset,
            "group_count": row["group_count"],
            "surface_sequence": row["surface_sequence"],
            "literal_card_reading_de": row["literal_card_reading_de"],
            "master_dictation_de": STEP_READINGS[row["statement_id"]],
            "apprentice_readback_de": STEP_READINGS[row["statement_id"]],
            "scribe_profile": "S1_BARE_MASTER" if phase == "WHAT" else "S2_Q_CELL_SCRIBE",
            "translation_layer": "OWNER_PLUS_PORTABLE_COMPONENTS_PLUS_LEARNED_CARDS",
        })
    write_tsv(OUT / "THIRTY_SEVENTH_26_WORK_STEPS.tsv", steps, list(steps[0]))

    astro_rows = [row for row in read_tsv(ASTRO) if row["page"] == "f68r1"]
    selected_locus = "f68r1.14"
    lookup = []
    for row in astro_rows:
        lookup.append({
            "locus": row["locus"],
            "namespace_id": row["namespace_id"],
            "visible_owner": row["visible_owner"],
            "group_count": row["group_count"],
            "surface_sequence": row["surface_sequence"],
            "atom_sequence": row["atom_sequence"],
            "spoken_instruction_de": row["spoken_instruction_de"],
            "selected_for_worked_job": "YES" if row["locus"] == selected_locus else "NO",
            "worked_job_value_de": "nächsten sichtbaren Stationswert ablesen" if row["locus"] == selected_locus else "ALTERNATIVE_LOOKUP_VALUE",
        })
    write_tsv(OUT / "THIRTY_SEVENTH_F68_LOOKUP_OPTIONS.tsv", lookup, list(lookup[0]))
    selected = next(row for row in lookup if row["selected_for_worked_job"] == "YES")

    balanced = {row["record_id"]: row for row in read_tsv(BALANCED)}
    job_card = [{
        "job_id": "D2_CLEAR_EXTRACT_STAR_ATLAS_WORKED",
        "bench_order": "WHEN>WHAT>HOW",
        "when_page": "f68r1",
        "when_locus": selected_locus,
        "when_surface_sequence": selected["surface_sequence"],
        "when_reading_de": selected["worked_job_value_de"],
        "what_record": "H3",
        "what_reading_de": balanced["H3"]["balanced_continuous_reading_de"],
        "how_record": "B2",
        "how_reading_de": balanced["B2"]["balanced_continuous_reading_de"],
        "final_workshop_output_de": "zweistufig geklärter Pflanzenansatz mit zurückbehaltener zweiter Portion, ausgeführt als örtliches Mehrstations-, Tuch-, Temperier- und Ablaufprogramm unter dem gewählten Sternstationswert",
        "practical_rival_de": "Pflanzenmaterial-, Filtrations- und Wasserwerksauftrag mit separater astronomischer Stationsnotiz",
        "written_crosspage_pointer": "NONE__MASTER_ASSEMBLES_JOB",
    }]
    write_tsv(OUT / "THIRTY_SEVENTH_JOB_CARD.tsv", job_card, list(job_card[0]))

    copies = [row for row in read_tsv(COPIES) if row["pattern_id"] == "E11" and row["source_statement_id"] == "B2-S010"]
    write_tsv(OUT / "THIRTY_SEVENTH_FOUR_HAND_RENDERING.tsv", copies, list(copies[0]))

    lines = [
        "# Vollständig durchgespielter Werkstattauftrag",
        "",
        "## 1. Meisterauftrag",
        "",
        "Wähle auf der Sternstation den nächsten sichtbaren Wert. Nimm danach von der",
        "abgebildeten Pflanze einen Arbeitsanteil, wringe ihn aus, lasse ihn stehen, seihe",
        "nach und stelle den sichtbaren Auszug bereit. Führe diesen Auftrag anschließend",
        "durch die örtlichen Stationen auf f82r; beginne bei jedem sichtbaren Besitzerwechsel",
        "einen neuen lokalen Posten.",
        "",
        "## 2. WHEN — f68r1",
        "",
        f"Gewählte Demonstrationsadresse: `{selected_locus}` / `{selected['visible_owner']}`.",
        f"Sichtbar geschrieben: `{selected['surface_sequence']}`.",
        f"Werkstattlesung: {selected['spoken_instruction_de']}",
        "Diese Auswahl ist ein vorgeführtes Beispiel des Meisters; die übrigen 36 f68r1-Loci",
        "stehen als alternative Nachschlagewerte in der Lookup-Tabelle.",
        "",
        "## 3. WHAT und HOW — alle 26 Arbeitsschritte",
        "",
    ]
    for row in steps:
        reset = " **Neuer Bildbesitzer.**" if row["owner_reset"] == "YES" else ""
        lines.extend([
            f"### {row['job_step']}. {row['statement_id']} ({row['phase']}){reset}",
            "",
            f"Meister: {row['master_dictation_de']}",
            "",
            f"Schreiberform: `{row['surface_sequence']}`",
            "",
            f"Kartenrücklesung: {row['literal_card_reading_de']}",
            "",
        ])
    lines.extend([
        "## 4. Derselbe Idiomkern in vier Händen",
        "",
        "B2-S010 enthält die Wendung „den länger gehaltenen Posten weiter ansetzen“.",
        "Die vier Werkstatthände schreiben sie verschieden, ohne Karte oder Sinn zu ändern:",
        "",
    ])
    for row in copies:
        lines.append(f"- {row['scribe_id']}: `{row['scribe_surface_sequence']}` → {row['semantic_readback_de']}.")
    lines.extend([
        "",
        "## 5. Fließende Gesamtlesung",
        "",
        f"**WHEN:** An f68r1 den lokalen Wert `{selected_locus}` als nächsten sichtbaren Stationswert lesen.",
        "",
        f"**WHAT:** {balanced['H3']['balanced_continuous_reading_de']}",
        "",
        f"**HOW:** {balanced['B2']['balanced_continuous_reading_de']}",
        "",
        f"**Ausgabe:** {job_card[0]['final_workshop_output_de']}.",
        "",
        "Das ist eine vollständige Arbeitstheorie für diesen Auftrag, nicht die Behauptung, dass",
        "das Manuskript selbst H3, B2 und f68r1 durch einen geschriebenen Verweis verbindet.",
    ])
    (OUT / "THIRTY_SEVENTH_COMPLETE_WORKED_DOSSIER.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "counts": {
            "worked_jobs": 1,
            "astro_lookup_options": len(lookup),
            "selected_astro_loci": 1,
            "prose_steps": len(steps),
            "prose_groups": sum(int(row["group_count"]) for row in steps),
            "what_steps": sum(row["phase"] == "WHAT" for row in steps),
            "how_steps": sum(row["phase"] == "HOW" for row in steps),
            "scribe_renderings": len(copies),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (NOUN_LOAD, BALANCED, ASTRO, COPIES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
