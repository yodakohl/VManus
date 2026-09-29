"""Check AF source extraction and registry receipt; not a semantic test."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[4]
checks = []


def check(name, value):
    checks.append({"name": name, "pass": bool(value)})


class Plain(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)


def plain(value):
    parser = Plain()
    parser.feed(value)
    return " ".join(" ".join(parser.parts).split())


def annotated(value):
    value = re.sub(r'<span class="pagenum"><a id="Page_(\d+)">\d+</a></span>',
                   lambda m: ' [page ' + m[1] + '] ', value)
    value = re.sub(r'<a href="#Footnote_(\d+)_\d+" class="fnanchor">\d+</a>',
                   lambda m: ' [note ' + m[1] + '] ', value)
    return plain(value)


inputs = json.loads((HERE / "AF_INPUTS.json").read_text())
for item in inputs["files"]:
    check("input_hash:" + item["path"], hashlib.sha256(
        (REPO / item["path"]).read_bytes()).hexdigest() == item["sha256"])

raw = (HERE / "D_SOURCE_PLINY_IV.html").read_bytes()
text = raw.decode("utf-8")
start = text.index('<h3 id="BOOK_XXII_CHAP_29">')
stop = text.index('<h3 id="BOOK_XXII_CHAP_30">', start)
chapter = text[start:stop]
source = json.loads((HERE / "AF_COMPLETE_SOURCE.json").read_text())
check("whole_chapter_bytes", (HERE / "AF_CHAPTER_SOURCE.html").read_bytes() == chapter.encode("utf-8"))
check("original_source_hash", source["source_sha256"] == hashlib.sha256(raw).hexdigest())
check("chapter_boundaries", source["start_anchor"] == "BOOK_XXII_CHAP_29" and source["stop_before"] == "BOOK_XXII_CHAP_30")
paragraphs = [annotated(p) for p in re.findall(r'<p>(.*?)</p>', chapter, re.S)]
check("all_three_paragraphs", len(paragraphs) == 3 and source["paragraphs"] == paragraphs)
check("all_seventeen_notes", [n["number"] for n in source["edition_notes"]] == list(range(2596, 2613)))
check("all_chapter_note_links", sorted(set(map(int, re.findall(r'id="FNanchor_(\d+)_\d+"', chapter)))) == list(range(2596, 2613)))
display = (HERE / "AF_COMPLETE_PASSAGE.md").read_text()
for i, paragraph in enumerate(paragraphs, 1):
    check("display_complete_paragraph:" + str(i), paragraph in display)
for note in source["edition_notes"]:
    check("note_original_html:" + str(note["number"]), note["html"] in text)
    check("note_full_display:" + str(note["number"]), note["text"] == plain(note["html"]) and note["text"] in display)
check("notes_fragment_bytes", (HERE / "AF_NOTES_SOURCE.html").read_bytes() ==
      ("\n".join(n["html"] for n in source["edition_notes"]) + "\n").encode("utf-8"))
check("1856_edition_layer", "MDCCCLVI" in text and "1856" in source["source_layer"])
receipt = json.loads((HERE / "AF_ADD_RECEIPT.json").read_text())
cardpath = HERE / receipt["card"]
card = json.loads(cardpath.read_text())
check("registered_card_hash", hashlib.sha256(cardpath.read_bytes()).hexdigest() == receipt["card_sha256"])
check("raw_784_not_reviewed", receipt["id"] == "IDEA000784" and receipt["status"] == "UNTESTED_PROPOSAL" and receipt["review_performed_by_producer"] is False)
check("no_target_selection_or_new_values", card["design"]["target_and_free_meaning_scope"]["target_selected"] is False and card["design"]["target_and_free_meaning_scope"]["new_Voynich_word_values"] == 0)
check("three_distinct_source_sequences", [c["id"] for c in card["design"]["complete_local_sequences"]] == ["CIRCLE_SCORPION", "CARRY_PATIENT", "ROOTED_KNOTS"])
result = {"status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
          "claim_ceiling": "Documentary hashes and complete extraction only; no source efficacy, morphology, target interpretation or scientific selection validated.",
          "checks_passed": sum(c["pass"] for c in checks), "checks_total": len(checks), "checks": checks}
(HERE / "AF_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["status", "checks_passed", "checks_total", "claim_ceiling"]}))
raise SystemExit(0 if result["status"] == "PASS" else 1)
