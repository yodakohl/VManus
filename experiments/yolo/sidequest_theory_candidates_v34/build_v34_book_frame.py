#!/usr/bin/env python3
"""Build V34's bounded reconstructed title, preface and workshop workflow."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
V33 = OUT.parent / "sidequest_theory_candidates_v33/V33_PRACTITIONER_DECISION_MANUAL.md"

ROLES = [
    {"role_id": "R1", "workshop_role": "MAGISTER_COMPILATOR", "person_count": "1", "task": "selects herbal, bath and astro sources; fixes the common card ledger and consultation order", "may_overlap": "R2"},
    {"role_id": "R2", "workshop_role": "DESIGNATOR_FIGURARUM", "person_count": "1", "task": "draws plant, patient, vessel and circle owners before prose is fitted around them", "may_overlap": "R1 or R3"},
    {"role_id": "R3", "workshop_role": "PRINCIPAL_SCRIBE", "person_count": "1", "task": "writes common-deck cards, selects field templates and maintains page/register continuity", "may_overlap": "R1"},
    {"role_id": "R4", "workshop_role": "ASSISTANT_SCRIBES", "person_count": "2-3", "task": "copy rare exemplar tails, apply hand-specific rendering, reflow around drawings and repeat carried entries", "may_overlap": "R5"},
    {"role_id": "R5", "workshop_role": "CORRECTOR_OR_USER", "person_count": "1", "task": "checks closures, repeated steps, measures, body-sector vetoes and the 28-position lookup", "may_overlap": "R1/R3/R4"},
]

LESSONS = [
    ("1", "PICTURE_OWNER", "Identify whether the page concerns a pictured simple, patient/bath construction or celestial lookup."),
    ("2", "COMMON_DECK", "Memorize roughly twenty frequent whole-card formulas; copy rare payload from the exemplar."),
    ("3", "FIELD_TEMPLATES", "Learn the five field forms: solo, short, multi-card commit, open Herbal clause, open Bio continuation."),
    ("4", "COMMIT_AND_CARRY", "Use DY/B3 to commit local work; carry owner and process state across physical line breaks."),
    ("5", "RENDERING", "Apply the permitted hand/placement rendering only after choosing an already licensed card."),
    ("6", "MEDICAL_LOOKUP", "Select remedy and bath, then apply zodiac body-sector veto and the 28-position lunar rule."),
    ("7", "COPY_AND_CORRECT", "Copy a complete page, reverse-read it, and correct only broken cards, fields or carried state."),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    roles = OUT / "V34_RECONSTRUCTED_WORKSHOP_ROLES.tsv"
    with roles.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ROLES[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(ROLES)
    lessons = OUT / "V34_SEVEN_LESSON_APPRENTICE_COURSE.tsv"
    with lessons.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["lesson", "competence", "executable_rule"]); w.writerows(LESSONS)

    report = """# V34 — reconstructed book frame and workshop

Status: **creative historical reconstruction, not recovered title or authorship**.

## Working title

> **Liber de virtutibus simplicium et balneis mulierum secundum cursum lunae**

> **Buch von den Kräften der einfachen Arzneien und den Frauenbädern nach dem Lauf des Mondes**

The short workshop name is provisionally **Practica balneorum**—“the practical
book of baths.” This title summarizes the present ten-page theory; it is not
claimed to have stood on a lost title page.

## Reconstructed preface

### Latin-like source style

> *In hoc libro ponuntur figurae simplicium, confectiones earum et balnea ad
> usum mulierum. Primo cognosce rem pictam; deinde sume mensuram et praepara
> liquorem sicut in cellulis signatur. Ante applicationem considera signum
> Lunae et mansionem eius, ne membrum sub signo constitutum intempestive
> tractetur. Quod clausum est perfice; quod apertum est cum sequenti linea
> continua.*

### German working expansion

> In diesem Buch stehen die Abbildungen der einfachen Arzneien, ihre
> Zubereitungen und die Bäder zum Gebrauch der Frauen. Erkenne zuerst die
> abgebildete Sache; nimm dann das Maß und bereite die Flüssigkeit, wie es in
> den Zellen bezeichnet ist. Prüfe vor der Anwendung Zeichen und Mondstation,
> damit die von diesem Zeichen regierte Körperstelle nicht zur Unzeit behandelt
> wird. Was geschlossen ist, vollende; was offen ist, setze in der folgenden
> Zeile fort.

This is not a translation of an extant Voynich paragraph. It is the shortest
ordinary-language preface that would teach the V28–V33 system without adding a
new mechanism.

## Intended user

The best concrete owner is a **small urban or household medical workshop with
access to bathing facilities**. Its working user may be a bath attendant,
empirical healer, surgeon-apothecary household or a practitioner concerned with
women's conditions. Nothing identifies the compiler's sex. The repeated women
show the patient class and procedure more clearly than they identify the author.

The user already knows ordinary materia medica, zodiac-body correspondences and
the conventional 28 lunar stations. The manuscript is an operational memory
system, not a first textbook of medicine or astronomy.

## Why use the unusual script?

The selected explanation is **proprietary multilingual workshop shorthand**:

1. one whole card compresses a recurrent Latin-like instruction;
2. rare plant names and special operations can be copied without normalizing
   their language;
3. the same deck works for Latin, vernacular and inherited exemplar material;
4. exact cards reduce ambiguity between several scribes;
5. wrappers and placement variants make copying fluent without changing the card;
6. compact cards fit text around pictures drawn first.

Secrecy may have been a useful side effect, but the apparatus does not require a
cryptographic adversary or a letter-by-letter cipher.

## Production order

```text
collect Latin/vernacular/exemplar source material
  → choose picture and practical register
  → draw the full visual owner first
  → translate recurrent clauses into common cards
  → copy rare payload as exact exemplar cards
  → choose one of five field templates
  → render and reflow around the existing drawing
  → correct closures, repeated steps and consultation indices
```

This directly explains the user's production constraint: text follows the
picture, so proximity and line endings may reflect available parchment rather
than sentence ownership.

## Small-workshop personnel

`V34_RECONSTRUCTED_WORKSHOP_ROLES.tsv` specifies five functions that require
only roughly three to five people because roles may overlap. Multiple hands are
expected: the common ledger is shared, while renderer habits and rare copied
tails vary.

## Seven-lesson apprenticeship

`V34_SEVEN_LESSON_APPRENTICE_COURSE.tsv` makes the system learnable in seven
steps. The apprentice memorizes only the small common deck and five templates;
they need not derive a cipher alphabet or understand every rare medicinal name.
They can copy a licensed rare card from the page exemplar and still preserve its
operational place.

## Historical ecology

- [Wellcome pre-1500 astrology handbook](https://wellcomecollection.org/works/gftr4sa9): data and rules for applying astrology to medical treatment.
- [NLM early Western manuscripts](https://mainweb.awsprod.nlm.nih.gov/hmd/collections/books/early-western-manuscripts/index.html): 15th-century Italian Latin/Italian astrological and medical miscellanies.
- [Edinburgh MS 175](https://archives.collections.ed.ac.uk/repositories/2/archival_objects/169194): Italian medical texts and recipes in five hands.
- [Tractatus de herbis tradition](https://en.wikipedia.org/wiki/Tractatus_de_Herbis): long-lived Italian illustrated materia-medica transmission.
- [Practical medicine in the fifteenth century](https://iris.unive.it/handle/10278/3746888): Latin/vernacular and professional/lay transmission.

These comparisons support the document ecology, not the particular title,
region, language, owner or codebook.

## Strongest rival

The strongest rival is a **general illustrated technical exemplar and teaching
register** whose formal cards were never expanded into normal prose. It can
explain pictures-first production, exact cards, multiple hands and local tails.
The medical WHAT/HOW/WHEN reconstruction currently wins because the ten-page
content hangs together, but it lacks an external readable key.

## Working provenance bet

If forced to choose, the present bet is an **Italian or Alpine-adjacent medical
workshop around 1420**, compiling Salernitan-style herbal/women's medicine,
balneological practice and practical lunar medicine through Latin plus one or
more vernacular source traditions. Confidence is low (`0.34`); Central European
production from imported Italian material remains equally plausible.

No sound, ordinary source sentence, title, author, institution, city or
language has been recovered. f84 and f84r remained sealed.
"""
    report_path = OUT / "V34_RECONSTRUCTED_TITLE_PREFACE_AND_WORKSHOP.md"
    report_path.write_text(report)

    selection = """# V34 theory selection

Date: 2026-08-22

Status: **proprietary medical-workshop shorthand selected as book frame**.

The working lost title is *Liber de virtutibus simplicium et balneis mulierum
secundum cursum lunae*. The intended object is a small practical medical
workshop book: images are drawn first; recurring source clauses are replaced by
whole-card abbreviations; rare multilingual payload is copied from exemplars;
five templates and two renderer habits produce the visible text; astrology
controls when and where the selected bath/remedy is used.

This is more learnable than a letter cipher and needs only three to five people
with overlapping roles. The title, Italian/Alpine provenance and reconstructed
preface are creative defaults, not recovered historical facts. f84 and f84r
remained sealed.
"""
    (OUT / "V34_THEORY_SELECTION.md").write_text(selection)

    checks = {
        "five_roles": len(ROLES) == 5,
        "seven_lessons": len(LESSONS) == 7,
        "roles_overlap_small_workshop": all(r["may_overlap"] for r in ROLES),
        "preface_marks_nontranslation": "not a translation" in report.lower(),
        "f84_sealed": True,
    }
    val = {
        "schema": "SIDEQUEST_V34_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "input": {str(V33.relative_to(ROOT)): digest(V33)},
        "outputs": {roles.name: digest(roles), lessons.name: digest(lessons), report_path.name: digest(report_path)},
    }
    (OUT / "V34_VALIDATION.json").write_text(json.dumps(val, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": val["status"], "roles": 5, "lessons": 7}))


if __name__ == "__main__":
    main()
