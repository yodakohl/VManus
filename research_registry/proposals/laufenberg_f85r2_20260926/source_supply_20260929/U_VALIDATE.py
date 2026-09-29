#!/usr/bin/env python3
"""Local U packet integrity only; no target query or semantic experiment."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(name):
    return json.loads((HERE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []

    def check(label, condition):
        checks.append({"check": label, "pass": bool(condition)})

    closure = read("U_CLOSURE.json")
    for name, expected in closure["files"].items():
        check("packet hash " + name, sha(HERE / name) == expected)

    receipts = read("U_ADD_RECEIPTS.json")
    check("exactly two raw adds", len(receipts) == 2)
    check("raw IDs", [r["stdout"]["id"] for r in receipts] ==
          ["IDEA000777", "IDEA000778"])
    cards = []
    for receipt in receipts:
        path = ROOT / receipt["file"]
        check("registered bytes " + path.name, sha(path) == receipt["sha256"])
        card = json.loads(path.read_text())
        cards.append(card)
        check("unreviewed label " + path.name,
              card["status"] == "RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED")
        check("two explicit consequences " + path.name,
              len(card["two_discriminating_consequences"]) == 2)
        for primary, expected in card["primary_hashes"].items():
            check("primary hash " + primary, sha(ROOT / primary) == expected)
    check("998 retained", "GDT998" in cards[0]["predecessor_ids"])
    check("680 and550 retained",
          {"IDEA000680", "IDEA000550"} <= set(cards[1]["predecessor_ids"]))

    carmina = read("U_CARMINA_COMPLETE_PASSAGES.json")
    poems = {x["number"]: x for x in carmina["poems"]}
    check("complete five edited sections",
          set(poems) == {"016", "017", "018", "018a", "019"})
    check("16 explicit participant change",
          "alter in altum tollitur" in poems["016"]["complete_section_text"] and
          "Hecubam reginam" in poems["016"]["complete_section_text"])
    check("18a exact full inscription sequence",
          poems["018a"]["lines"][1] ==
          "Regnabo; regno; regnavi; sum sine regno.")
    check("17 complete ending and lunar simile",
          poems["017"]["lines"][-1] == "mecum omnes plangite!" and
          "velut luna" in poems["017"]["complete_section_text"])
    check("19 complete last stanza retained",
          poems["019"]["lines"][-1] == "omnibus habundas.")

    pliny = read("U_PLINY_COMPLETE_PASSAGES.json")
    check("four complete numbered packets",
          [(p["book"], p["sections"]) for p in pliny] ==
          [(13, [107, 108, 109, 110]), (18, [218, 219]),
           (2, [108, 109, 110]), (2, [36, 37, 38, 39])])
    for packet in pliny:
        check("all section bodies " + str(packet["sections"]),
              [p["section"] for p in packet["parts"]] == packet["sections"] and
              all(len(p["latin"].split()) >= 30 for p in packet["parts"]))
    herb = {p["section"]: p["latin"] for p in pliny[0]["parts"]}
    check("both boundary events retained",
          "donec maturescant flosque, qui est candidus, decidat" in herb[108])
    check("Euphrates separate section",
          "in Euphrate tradunt" in herb[109] and
          "medias noctes" in herb[109])
    check("source astronomical scope retained",
          "quas adhaerere caelo diximus" in pliny[1]["parts"][-1]["latin"])

    manifest = read("U_FORTUNE_MANIFEST.json")
    check("official full source canvas",
          any(c.get("label") == "1r (0005)" and
              c.get("@id", "").endswith("/canvas/5")
              for c in manifest["sequences"][0]["canvases"]))
    check("source public-domain attribution",
          manifest["license"] == "https://creativecommons.org/publicdomain/mark/1.0/"
          and "Bayerische Staatsbibliothek" in json.dumps(manifest["attribution"]))
    check("whole source image receipt",
          sha(HERE / "U_FORTUNE_CLM4660_1R.jpg") ==
          "7805ad0cec253fc3929db3abc41db37bab2da1c68815c633d39784e654cdcfea")

    start = datetime.datetime.fromisoformat(closure["started_utc"])
    close = datetime.datetime.fromisoformat(closure["closed_utc"])
    deadline = datetime.datetime.fromisoformat(closure["deadline_utc"])
    check("inclusive45minute bound", start <= close <= deadline)
    result = {
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "scope": "Hash, raw-label and source-boundary integrity only. No Latin, image, target grammar or meaning validation.",
        "checks": checks,
        "check_count": len(checks),
        "elapsed_seconds": (close - start).total_seconds(),
        "new_target_tests": 0,
        "new_confirmed_lexemes": 0,
        "closed_utc": closure["closed_utc"],
    }
    (HERE / "U_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "check_count", "elapsed_seconds"]}))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
