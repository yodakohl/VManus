#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXPERIMENTS = OUT.parents[1]
R134 = EXPERIMENTS / "yolo" / "sidequest_semantic_current_ten_page_edition_hundred_thirty_fourth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    if not rows:
        return
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    {
        "source_id": "S01_DURHAM_COSIN_V_IV_1",
        "date_place": "mid-late 15c; England",
        "genre": "medical bath recipes plus monthly regimen and astrological plague text",
        "short_period_evidence": "take lavender and chamomile; herbs for bath; pour into the bath",
        "slot_order": "INDICATION>TAKE_MATERIAL>PREPARE_BATH>POUR_TO_TARGET>USE_UNTIL_DONE",
        "architecture_fit": "Herbal material can feed a separate bathing instruction; use target comes late",
        "source_url": "https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s19s1616306.xml",
    },
    {
        "source_id": "S02_BL_HARLEY_1736_DAISY",
        "date_place": "mid 15c; England",
        "genre": "medical recipe",
        "short_period_evidence": "take daisy leaves and roots; stamp them; take the juice",
        "slot_order": "TAKE_PARTS>PROCESS_MATERIAL>TAKE_PRODUCT",
        "architecture_fit": "Picture-owner material precedes operation and recovered product",
        "source_url": "https://searcharchives.bl.uk/catalog/040-002047567",
    },
    {
        "source_id": "S03_BL_HARLEY_2390",
        "date_place": "15c; England",
        "genre": "medical remedy book",
        "short_period_evidence": "take one handful of herbs; seethe them; drink that juice",
        "slot_order": "TAKE_QUANTITY_MATERIAL>HEAT>USE_PRODUCT",
        "architecture_fit": "Measure can be fronted with material; use follows preparation",
        "source_url": "https://searcharchives.bl.uk/catalog/040-002048221",
    },
    {
        "source_id": "S04_WELLCOME_MS_418",
        "date_place": "mid 15c; France",
        "genre": "medicinal waters in Latin and Langue d'Oc",
        "short_period_evidence": "take named herb; prepare medicinal water; give that water as drink or wound remedy",
        "slot_order": "TAKE_PLANT>MAKE_WATER>PRODUCT>ADMINISTER",
        "architecture_fit": "A plant article and a later application can share a preparation owner",
        "source_url": "https://wellcomecollection.org/works/f6nzyzh4",
    },
    {
        "source_id": "S05_WELSH_MIDDLE_ENGLISH_PARALLELS",
        "date_place": "14-15c witnesses; Britain",
        "genre": "medical recipe parallels",
        "short_period_evidence": "take nettle; stamp; temper with vinegar; lay to wound",
        "slot_order": "TAKE_MATERIAL>COMMINUTE>ADD_MEDIUM>APPLY_TO_TARGET",
        "architecture_fit": "Target placement belongs at the end rather than inside the material name",
        "source_url": "https://www.ncbi.nlm.nih.gov/books/NBK558265/",
    },
    {
        "source_id": "S06_LIBER_CURE_COCORUM_AMIDON",
        "date_place": "c1430; northern England",
        "genre": "culinary/workshop recipe",
        "short_period_evidence": "steep; change water; bruise; seethe; strain; let stand; pour off; dry",
        "slot_order": "SOAK>RENEW_MEDIUM>COMMINUTE>HEAT>STRAIN>SETTLE>DECANT>END_STATE",
        "architecture_fit": "A long wet-process chain can be written as adjacent short imperatives without one sentence per line",
        "source_url": "https://medievalbritain.com/type/medieval-life/medieval-recipes/medieval-recipes-meat-of-cyprus-1430/",
    },
    {
        "source_id": "S07_OTHMER_MS_1",
        "date_place": "before 1438; north-west Italy",
        "genre": "520 numbered alchemical medical craft household recipes",
        "short_period_evidence": "large mixed practical recipe collection with numbered entries and alphabetical index",
        "slot_order": "ENTRY_ADDRESS>LOCAL_MATERIALS>LOCAL_OPERATIONS>LOCAL_RESULT",
        "architecture_fit": "A shared formula deck plus many learned specialist entries is period-plausible",
        "source_url": "https://openn.library.upenn.edu/Data/0025/html/OthmerMS1.html",
    },
    {
        "source_id": "S08_REGIMEN_SANITATIS_ARAGONUM",
        "date_place": "14c or c1400; Spain or southern France",
        "genre": "health regimen with bathing and appended recipes",
        "short_period_evidence": "bathing eating drinking sleeping regimen followed by a brief recipe section",
        "slot_order": "REGIMEN_CONDITION>BODY_PRACTICE>RECIPE_APPENDIX",
        "architecture_fit": "Bathing and recipes can coexist in one compact practitioner book without written crosslinks",
        "source_url": "https://openn.library.upenn.edu/Data/0027/html/cpp_10a_210.html",
    },
    {
        "source_id": "S09_LIBER_DIVERSARUM_ARCIUM",
        "date_place": "manuscript c1430; Venice region",
        "genre": "structured painters' technical recipe book",
        "short_period_evidence": "more than five hundred material and process instructions arranged as a workshop course",
        "slot_order": "MATERIAL_SELECTION>PREPARATION>MEDIUM>MIX>APPLICATION>FINISH",
        "architecture_fit": "The same formula architecture is equally compatible with a nonmedical workshop miscellany",
        "source_url": "https://initiale.irht.cnrs.fr/en/codex/8029",
    },
]


REVISIONS = {
    "MC019": ("fertig", "A standalone or final card is better read as DONE than as two verbs"),
    "MC026": ("einsetzen", "The inherited work item need not be repeated inside the verb"),
    "MC039": ("Sollmaß", "Already period-sized and stable"),
    "MC040": ("dorthin einsetzen", "Action plus late target matches recipe order"),
    "MC055": ("davon", "Period recipes repeatedly resume a prepared batch with thereof/from it"),
    "MC074": ("überführen", "Current-item reference is supplied by the running register"),
    "MC080": ("Ansatz", "Short preparation noun is enough"),
    "MC086": ("Anteil", "After DAVON and before measure/target it behaves better as a part noun"),
    "MC119": ("Klarauszug", "A compact recovered product is better than a whole until-clear clause"),
    "MC120": ("bemessen", "Imperative measure action fits early and medial recipe slots"),
    "MC123": ("dies", "The active-item register supplies the noun"),
    "MC153": ("weiter", "Already atomic"),
    "MC154": ("dorthin", "Already atomic target anaphor"),
    "MC157": ("damit weiter", "Compact carried-preparation construction"),
    "MC161": ("bereit", "State/result is shorter and works before a share or target"),
    "MC171": ("das nächste", "Item class is inherited from the active register"),
    "MC032": ("länger bearbeiten", "No specific heat or contact sense is forced"),
}


def main():
    cards = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv")
    jobs = read_tsv(R134 / "HUNDRED_THIRTY_FOURTH_FOUR_JOBS.tsv")
    active = [row for row in cards if row["teaching_layer"] != "SPECIALIST_DRAWER_WHOLE_CARD"]
    revised = []
    for row in active:
        new, reason = REVISIONS.get(row["master_card_id"], (row["current_spoken_default_de"], "Retain pending a stronger multi-context phrase match"))
        revised.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "event_count": row["event_count"],
            "old_default_de": row["current_spoken_default_de"],
            "period_sized_default_de": new,
            "decision": "REVISE" if new != row["current_spoken_default_de"] else "KEEP",
            "reason": reason,
        })
    write_tsv("HUNDRED_THIRTY_FIFTH_PERIOD_SOURCE_COMPARATORS.tsv", SOURCES)
    write_tsv("HUNDRED_THIRTY_FIFTH_41_ACTIVE_CARD_REVISIONS.tsv", revised)

    job_rows = []
    plans = {
        "J1_ROOT_AND_LEAF_BASIN": ("TAKE_PARTS>COMMINUTE>ADD_MEDIUM>MEASURE>PREPARE>TRANSFER_TO_BATH>WASH_OR_HOLD>FINISH", "S01|S02|S03|S04|S05", "Strong period order; exact plant and ailment remain picture/exemplar content"),
        "J2_CLEAR_EXTRACT_STATIONS": ("TAKE_PARTS>EXTRACT>WRING>SETTLE>RESTRAIN>TAKE_CLEAR_PRODUCT>TRANSFER>DECANT", "S02|S04|S06", "Best phrase-order match; station identities remain image-local"),
        "J3_BOUND_APPLICATION_SERVICE": ("PREPARE>MEASURE>TAKE_SHARE>PLACE_AT_TARGET>FASTEN>WASH>REMOVE_OR_COLLECT", "S05|S07|S09", "Application order is plausible; bound-cloth specificity is only locally supported"),
        "J4_FRESH_PLANT_LONG_ROUTE": ("TAKE_FRESH_MATERIAL>MAKE_WASH>RETAIN_SECOND_SHARE>EXTRACT>MEASURE>LONG_TRANSFER_CHAIN", "S01|S04|S06|S07", "Herbal half fits; the long apparatus route has no single period textual twin"),
    }
    for job in jobs:
        order, sources, verdict = plans[job["job_id"]]
        job_rows.append({
            "job_id": job["job_id"],
            "title_de": job["title_de"],
            "period_normalized_order": order,
            "closest_sources": sources,
            "phrase_order_verdict": verdict,
            "recommended_reading_de": job["complete_job_instruction_de"],
        })
    write_tsv("HUNDRED_THIRTY_FIFTH_FOUR_JOB_PERIOD_ORDER.tsv", job_rows)

    report = [
        "# Hundertfünfunddreißigste Runde: echte Formelsätze um 1400", "",
        "This is a fast creative phrase-order comparison, not a blind test. Nine real recipe, bath, regimen and",
        "technical-book comparators from the fourteenth and fifteenth centuries were placed beside the four",
        "current jobs. The strongest recurring order is short and paratactic: TAKE material; PROCESS it; ADD a",
        "medium; MEASURE a part; HEAT/HOLD; STRAIN or DECANT; PUT/APPLY at the target; finish.", "",
        "The current WHAT-to-HOW architecture survives. Durham Cosin V.iv.1 actually places herb bath recipes",
        "beside a monthly regimen and an astrological plague text. Harley 1736 gives the compact sequence take",
        "leaves and roots, stamp them, take the juice. The c1430 amidon procedure independently supplies soak,",
        "renew water, bruise, heat, strain, stand, pour off and dry. Othmer MS 1 and the Liber diversarum arcium",
        "show that the same terse architecture also belongs to large nonmedical practical recipe collections.", "",
        "## Lexical consequence", "",
        "Seventeen shared cards are shortened to period-sized utterances. The strongest repairs are `chety =",
        "ANTEIL`, not the sentence 'einen Teil abtrennen'; `oldy = FERTIG`; `okaiin = BEMESSEN`; `chdy =",
        "ÜBERFÜHREN`; `checthy = BEREIT`; and `cheey/shey = KLARAUSZUG`. Active owner and target registers",
        "supply omitted nouns. This is closer to a learned workshop codebook in which one sign stands for one",
        "short prompt, state, product or anaphor.", "",
        "## Job verdicts", "",
    ]
    for row in job_rows:
        report += [f"- **{row['job_id']}**: `{row['period_normalized_order']}`. {row['phrase_order_verdict']}"]
    report += ["", "## Sources", ""]
    for src in SOURCES:
        report += [f"- [{src['source_id']}]({src['source_url']}): {src['date_place']}; {src['genre']}."]
    report += ["", "Next propagate the seventeen shortened values through all 173 cards, 381 events and 116 statements,",
               "then rewrite all four work orders in literal period-sized clauses before adding any new meanings."]
    (OUT / "HUNDRED_THIRTY_FIFTH_PERIOD_PHRASE_ORDER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"sources": len(SOURCES), "active_cards": len(revised), "jobs": len(job_rows), "revised_cards": sum(r["decision"] == "REVISE" for r in revised)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
