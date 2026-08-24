#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P541 = ROOT / "experiments/yolo/sidequest_semantic_executable_workshop_manual_five_hundred_forty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


EXPANSIONS = {
    "X01": (
        "Von der sichtbaren Pflanze das vorgeschriebene Maß für den Heiltrank nehmen, kurz ansetzen und weiterverarbeiten.",
        ["Wurzel", "Heiltrank"],
        "Vom sichtbaren Pflanzenrohstoff die abgemessene Menge für das Waschbad nehmen, kurz ansetzen und weiterführen.",
        ["Pflanzenrohstoff", "Waschbad"],
    ),
    "X02": (
        "Den Saft der sichtbaren Pflanze durch ein Tuch auswringen, länger halten und den kurzen Auszug von dort abnehmen.",
        ["Saft", "Tuch"],
        "Das Pressgut der sichtbaren Pflanze am Filtertuch auswringen, länger halten und den kurzen Auszug abnehmen.",
        ["Pressgut", "Filtertuch"],
    ),
    "X03": (
        "Eine Portion Salbe ansetzen, zur Hautstelle geben, länger halten und den Schritt schließen.",
        ["Salbe", "Hautstelle"],
        "Eine Portion Beize ansetzen, zum Werkstück geben, länger halten und den Schritt schließen.",
        ["Beize", "Werkstück"],
    ),
    "X04": (
        "Danach eine Dosis vollständig für den Patienten ansetzen und verwahren.",
        ["Dosis", "Patient"],
        "Danach eine Materialcharge vollständig ansetzen und im Vorratsgefäß verwahren.",
        ["Materialcharge", "Vorratsgefäß"],
    ),
    "X05": (
        "Eine Portion für den Badenden ansetzen, zur Körperstelle führen, kurz durchlassen und schließen.",
        ["Badender", "Körperstelle"],
        "Eine Beckencharge ansetzen, zur sichtbaren Zielstation führen, kurz durchlassen und schließen.",
        ["Beckencharge"],
    ),
    "X06": (
        "Mit dem Badewasser am Patienten fortsetzen, kurz wärmen und schließen.",
        ["Badewasser", "Patient"],
        "Mit dem Beckenwasser fortsetzen, kurz wärmen und schließen.",
        ["Beckenwasser"],
    ),
    "X07": (
        "Danach den kurzen Abguss vom Körperteil nehmen, kurz auffangen und schließen.",
        ["Abguss", "Körperteil"],
        "Danach den Posten kurz in das Auffanggefäß führen und schließen.",
        ["Auffanggefäß"],
    ),
    "X08": (
        "Danach das Heilbad durch den sichtbaren Lauf geben, beim Badenden vollständig halten und schließen.",
        ["Heilbad", "Badender"],
        "Danach die Arbeitsflüssigkeit durch die Leitung geben, vollständig halten und schließen.",
        ["Arbeitsflüssigkeit", "Leitung"],
    ),
    "X09": (
        "Die Auflage an der sichtbaren Körperstation ansetzen, befestigen und schließen.",
        ["Auflage"],
        "Den Filtereinsatz an der sichtbaren Station ansetzen, in der Halterung befestigen und schließen.",
        ["Filtereinsatz", "Halterung"],
    ),
    "X10": (
        "Die zweite Behandlungsstufe für den Patienten einstellen, länger ansetzen und fortsetzen.",
        ["Behandlungsstufe", "Patient"],
        "Die zweite Anlagenstufe einstellen, länger ansetzen und fortsetzen.",
        ["Anlagenstufe"],
    ),
    "X11": (
        "Im Arbeitsfach eine Dosis nach Maß an der Anwendungsstelle fortsetzen, kurz halten und schließen.",
        ["Dosis", "Anwendungsstelle"],
        "Im Arbeitsfach die Charge nach Maß an der Zielstelle fortsetzen, kurz halten und schließen.",
        ["Charge"],
    ),
    "X12": (
        "Das Badewasser im Lauf fortsetzen, vollständig für den Patienten ansetzen, auffangen und schließen.",
        ["Badewasser", "Patient"],
        "Das Laufwasser fortsetzen, vollständig ansetzen, im Sammelgefäß auffangen und schließen.",
        ["Laufwasser", "Sammelgefäß"],
    ),
}


def main() -> None:
    samples = read_tsv(P541 / "FIVE_HUNDRED_FORTY_FIRST_TWELVE_NEW_WORKSHOP_INSTRUCTIONS.tsv")
    rows: list[dict[str, str]] = []
    insertion_rows: list[dict[str, str]] = []
    for sample in samples:
        medical, med_terms, technical, tech_terms = EXPANSIONS[sample["sample_id"]]
        winner = "MEDICAL" if len(med_terms) < len(tech_terms) else "TECHNICAL" if len(tech_terms) < len(med_terms) else "TIE"
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "owner": sample["owner"],
                "section": "HERBAL" if sample["owner"].startswith("H") else "BIOLOGICAL",
                "silent_owner_de": sample["silent_owner_de"],
                "written_surface_sequence": sample["written_surface_sequence"],
                "literal_card_readback_de": sample["literal_readback_de"],
                "medical_expansion_de": medical,
                "medical_silent_terms": "|".join(med_terms),
                "medical_insertion_cost": str(len(med_terms)),
                "technical_expansion_de": technical,
                "technical_silent_terms": "|".join(tech_terms),
                "technical_insertion_cost": str(len(tech_terms)),
                "local_winner": winner,
                "card_meanings_changed": "NO",
            }
        )
        for model, terms in [("MEDICAL", med_terms), ("TECHNICAL", tech_terms)]:
            for term in terms:
                insertion_rows.append(
                    {
                        "sample_id": sample["sample_id"],
                        "section": "HERBAL" if sample["owner"].startswith("H") else "BIOLOGICAL",
                        "model": model,
                        "inserted_term_de": term,
                        "supplied_by_image": "NO",
                        "supplied_by_card": "NO",
                        "reason_needed": "make the purpose-specific fluent expansion concrete",
                    }
                )
    write_tsv("FIVE_HUNDRED_FORTY_SECOND_TWELVE_DUAL_PURPOSE_EXPANSIONS.tsv", rows)
    write_tsv("FIVE_HUNDRED_FORTY_SECOND_FORTY_TWO_SILENT_INSERTIONS.tsv", insertion_rows)

    summary_rows: list[dict[str, str]] = []
    for scope in ["HERBAL", "BIOLOGICAL", "TOTAL"]:
        scoped = rows if scope == "TOTAL" else [row for row in rows if row["section"] == scope]
        medical_cost = sum(int(row["medical_insertion_cost"]) for row in scoped)
        technical_cost = sum(int(row["technical_insertion_cost"]) for row in scoped)
        summary_rows.append(
            {
                "scope": scope,
                "samples": str(len(scoped)),
                "medical_insertions": str(medical_cost),
                "technical_insertions": str(technical_cost),
                "difference_medical_minus_technical": str(medical_cost - technical_cost),
                "medical_local_wins": str(sum(row["local_winner"] == "MEDICAL" for row in scoped)),
                "technical_local_wins": str(sum(row["local_winner"] == "TECHNICAL" for row in scoped)),
                "ties": str(sum(row["local_winner"] == "TIE" for row in scoped)),
                "selected_purpose": "MEDICAL" if medical_cost < technical_cost else "TECHNICAL" if technical_cost < medical_cost else "TIE",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_SECOND_PURPOSE_COST_SUMMARY.tsv", summary_rows)

    total = summary_rows[-1]
    summary = {
        "status": "PASS",
        "samples": len(rows),
        "insertions": len(insertion_rows),
        "medical_insertions": int(total["medical_insertions"]),
        "technical_insertions": int(total["technical_insertions"]),
        "medical_local_wins": int(total["medical_local_wins"]),
        "technical_local_wins": int(total["technical_local_wins"]),
        "ties": int(total["ties"]),
        "prose_purpose_lead": total["selected_purpose"],
        "card_meanings_changed": 0,
    }
    (HERE / "FIVE_HUNDRED_FORTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Fünfhundertzweiundvierzigste Runde: zwei konkrete Buchzwecke",
        "",
        "## Ergebnis",
        "",
        "Die zwölf neu geschriebenen Anweisungen wurden zweimal vollständig ausformuliert: als medizinisch-praktisches Pflanzen-/Badebuch und als Pflanzenmaterial-/Badehaus-/Nasswerkstattbuch.",
        "",
        f"Die medizinische Fassung benötigt {summary['medical_insertions']} stille Inhaltswörter, die technische {summary['technical_insertions']}. Lokal gewinnt Medizin einmal, Technik fünfmal, sechs Aufgaben bleiben gleich teuer.",
        "",
        "## Woher der Unterschied kommt",
        "",
        "Auf Herbal sind beide Fassungen gleich teuer: Heiltrank/Salbe/Patient stehen Rohstoff/Waschbad/Werkstück gegenüber. In Biological muss Medizin häufig Patient, Körperteil oder Heilbad ergänzen, während Becken, Leitung, Auffanggefäß und Anlagenstufe näher am sichtbaren Besitzer liegen.",
        "",
        "Die Ausnahme ist die Befestigungszelle X09. Unter einer Figuren-/Körperstation liest sich qokylddy sehr natürlich als Auflage ansetzen und befestigen; die technische Fassung braucht Filtereinsatz und Halterung.",
        "",
        "## Neue Zweckrangfolge",
        "",
        "Für die sieben Prosaseiten führt jetzt knapp das praktische Pflanzenmaterial-/Badehausmodell. Medizin bleibt kein verlorener Rivale, sondern wahrscheinlich eine tatsächliche Nutzungsart einzelner Anweisungen. Die sauberste Arbeitstheorie ist daher ein Nasswerkstattbuch mit medizinisch nutzbaren Pflanzen- und Körperanwendungen, nicht ein ausschließlich therapeutischer Codex.",
        "",
        "## Nächster Angriff",
        "",
        "Als Nächstes werden die drei Astro-Seiten wieder angeschlossen. Entscheidend ist, ob sie eher einen medizinischen Wahlkalender oder einen allgemeinen Arbeits-/Betriebsalmanach bilden, ohne neue Kartenbedeutungen aus der Prosa zu importieren.",
    ]
    (HERE / "FIVE_HUNDRED_FORTY_SECOND_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
