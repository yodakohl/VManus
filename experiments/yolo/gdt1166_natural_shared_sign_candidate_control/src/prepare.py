#!/usr/bin/env python3
"""Frozen source projection only. No fitting, candidate selection or scoring."""
import argparse
import collections
import hashlib
import json
import random
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
PINS = {
    "b4": "ca890ca0820c1ec6b1cb713eeb75cda77a2c580d017c0fa8fcbb813da068938f",
    "b6": "40d585eddac00db4d889308c956f1dd446d4df769dadf478244bb77571c27985",
    "br1": "a097422700c50b9e21433e9ff4cd2ff5d213f05419c8ef22eee3d664bedbe8b6",
    "bs1": "28a46cdfef82975e4d834c081edc5465f887d9efa7b86b65f70ec12a7d0993a6",
    "gr1": "39285d4e49394c267de3d1cefbb7892538e08202a94ec72957d88b75574ed0a4",
    "w1": "d1ae0998ee0ef34573d8db8ab3ebac2e895ad12a0eaf23059ddbcc7a968373e7",
    "chardec": "09d35185befb273eb13d95fc4d8054afc5c358dc0caada03eb20f51e70ec3945",
    "editorialdec": "6d79574a35b88d51c5f9d5eae2edef71350d846d7f6b62c8c0f1cced2d96fb9e",
}
EXCLUDED = {"note", "anchor", "ptr", "listTranspose", "transpose", "del"}


def local(node):
    return node.tag.split("}")[-1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
                               separators=(",", ":") if compact else None) + "\n")


def glyph_table(root):
    result = {}
    for node in root.iter():
        if local(node) not in {"glyph", "char"} or XML_ID not in node.attrib:
            continue
        mappings = [(x.attrib, "".join(x.itertext()).strip()) for x in node
                    if local(x) == "mapping"]
        numbers = [text for attrs, text in mappings
                   if attrs.get("type") == "unicode_codepoint"
                   and attrs.get("subtype") != "unicode_symbol"]
        symbols = [text for attrs, text in mappings
                   if attrs.get("subtype") == "unicode_symbol"
                   or attrs.get("type") == "unicode_symbol"]
        norm = [text for attrs, text in mappings if attrs.get("type") == "normalized"]
        char = None
        if len(numbers) == 1 and re.fullmatch(r"[0-9a-fA-F]{4,6}", numbers[0]):
            point = int(numbers[0], 16)
            if point <= 0x10FFFF and not 0xD800 <= point <= 0xDFFF:
                char = chr(point)
                if symbols and any(symbol != char for symbol in symbols):
                    char = None
        result["#" + node.attrib[XML_ID]] = {
            "char": char, "normalized": norm[0] if len(norm) == 1 else None,
            "consistent": char is not None,
        }
    return result


class Projection:
    """Native whitespace defines tokens; reference letters never create boundaries."""
    def __init__(self, glyphs):
        self.glyphs = glyphs
        self.words = []
        self.keys = []
        self.reference = []
        self.flags = set()
        self.abbreviated = False
        self.input_unknown = False
        self.expansion_unknown = False

    def boundary(self):
        if self.keys:
            self.words.append({
                "native_keys": self.keys, "reference": "".join(self.reference),
                "input_unknown": self.input_unknown,
                "expansion_unknown": self.expansion_unknown or not "".join(self.reference),
                "abbreviated": self.abbreviated, "flags": sorted(self.flags),
            })
        elif self.reference:
            raise ValueError("Reference-only characters without an observed token")
        self.keys, self.reference, self.flags = [], [], set()
        self.abbreviated = self.input_unknown = self.expansion_unknown = False

    def text(self, text, joined, abbreviated, mark=False):
        for char in text or "":
            if char.isspace():
                if not joined:
                    self.boundary()
            else:
                self.keys.append(char)
                if not mark:
                    self.reference.append(char)
                self.abbreviated |= abbreviated

    def unknown(self, reason, abbreviated):
        self.keys.append(None)
        self.input_unknown = self.expansion_unknown = True
        self.abbreviated |= abbreviated
        self.flags.add(reason)

    def visit(self, node, joined=False, abbreviated=False, mark=False):
        tag = local(node)
        if tag in EXCLUDED:
            return
        if tag in {"unclear", "supplied", "expan", "gap", "metamark"}:
            self.unknown(tag, abbreviated)
            return
        if tag in {"pb", "lb", "cb"}:
            if not joined:
                self.boundary()
            return
        if tag == "handShift":
            return
        if tag == "choice":
            self.unknown("unsupported_choice", abbreviated)
            return
        if tag == "ex":
            text = "".join(node.itertext())
            if any(char.isspace() for char in text):
                self.expansion_unknown = True
                self.flags.add("restoration_has_whitespace")
            else:
                self.reference.append(text)
            return
        if tag == "g":
            value = self.glyphs.get(node.get("ref"))
            if not value or not value["consistent"]:
                self.unknown("undocumented_or_conflicting_glyph", abbreviated)
            else:
                self.keys.append(value["char"])
                self.abbreviated |= abbreviated
                if not mark:
                    if value["normalized"] is None:
                        self.expansion_unknown = True
                        self.flags.add("missing_reference_normalization")
                    else:
                        self.reference.append(value["normalized"])
            return
        joined = joined or tag == "w"
        abbreviated = abbreviated or tag == "abbr"
        mark = mark or tag == "am"
        if tag == "add" and any(local(x) in {"unclear", "supplied", "gap"} for x in node.iter()):
            self.unknown("ambiguous_addition", abbreviated)
            return
        self.text(node.text, joined, abbreviated, mark)
        for child in node:
            self.visit(child, joined, abbreviated, mark)
            self.text(child.tail, joined, abbreviated, mark)


def reference_words(node, glyphs):
    """Readable external-reference view; no pairing to B4 is supplied."""
    output = []
    def visit(x, joined=False, parent_tag=None):
        tag = local(x)
        if tag in EXCLUDED or tag in {"am", "handShift"}:
            return
        if tag == "add" and any(local(y) in {"unclear", "supplied", "gap"} for y in x.iter()):
            output.append("\uFFFC")
            return
        if tag in {"unclear", "supplied", "gap", "metamark", "choice"}:
            output.append("\uFFFC")
            return
        if tag in {"lb", "pb", "cb"}:
            if not joined:
                output.append(" ")
            return
        if tag == "g":
            value = glyphs.get(x.get("ref"))
            output.append(value["normalized"] if value and value["consistent"]
                          and value["normalized"] is not None else "\uFFFC")
            return
        record_boundary = tag == "seg" and parent_tag == "ab"
        if record_boundary:
            output.append(" ")
        joined = joined or tag == "w"
        def text(s):
            output.append("".join(char for char in s or "" if not char.isspace())
                          if joined else s or "")
        text(x.text)
        for child in x:
            visit(child, joined, tag)
            text(child.tail)
        if record_boundary:
            output.append(" ")
    visit(node)
    tokens = "".join(output).split()
    return [x for x in tokens if "\uFFFC" not in x], sum("\uFFFC" in x for x in tokens)


def fixtures(glyphs):
    def project(xml):
        p = Projection(glyphs); p.visit(ET.fromstring(xml)); p.boundary()
        return p.words
    a = project('<seg>x<abbr>a<ex>e</ex><am><g ref="#bar_e"/></am>b</abbr> z</seg>')
    b = project('<seg>xa<g ref="#bar_n"/>b z</seg>')
    assert [x["native_keys"] for x in a] == [x["native_keys"] for x in b]
    assert a[0]["reference"] == "xaeb"
    assert len(project('<seg><w>a<g ref="#dbloblhyph"/><lb/>b</w> c</seg>')) == 2
    assert len(project('<seg>a<lb/>b</seg>')) == 2
    assert project('<seg>a<ex>long</ex>b</seg>')[0]["native_keys"] == list("ab")
    assert project('<seg>a<del>bad</del><add>b</add></seg>')[0]["native_keys"] == list("ab")
    assert project('<seg>a<note>gold hint</note>b</seg>')[0]["native_keys"] == list("ab")
    literal_mark = project('<seg>a<ex>long</ex><am>x</am>b</seg>')[0]
    assert literal_mark["native_keys"] == list("axb") and literal_mark["reference"] == "alongb"
    assert project('<seg><g ref="#bar_tl">e</g></seg>')[0]["input_unknown"]
    assert project('<seg>a<supplied>b</supplied>c</seg>')[0]["input_unknown"]
    addition = ET.fromstring('<seg>x <add>first <unclear>?</unclear> second</add> y</seg>')
    reference, unknowns = reference_words(addition, glyphs)
    assert reference == ["x", "y"] and unknowns == 1
    projection = Projection(glyphs); projection.visit(addition); projection.boundary()
    assert len(projection.words) == 3 and projection.words[1]["native_keys"] == [None]
    adjacent_records = ET.fromstring('<body><ab><seg>a</seg><seg>b</seg></ab></body>')
    assert reference_words(adjacent_records, glyphs) == (["a", "b"], 0)
    assert glyphs["#bar_e"]["char"] == glyphs["#bar_n"]["char"] == glyphs["#bar_m"]["char"]
    assert not glyphs["#tlbar"]["consistent"]
    return {"status": "PASS", "scope": "independent source-projection fixtures; not recovery"}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--fixtures-only", action="store_true")
    args = parser.parse_args()
    trees, receipts = {}, []
    for name, pin in PINS.items():
        path = ROOT / "sources" / (name + ".xml"); data = path.read_bytes()
        assert digest(data) == pin, f"changed source: {name}"
        trees[name] = ET.fromstring(data)
        receipts.append({"path": str(path.relative_to(ROOT)), "sha256": pin,
                         "bytes": len(data), "url": f"https://gams.uni-graz.at/o:corema.{name}/TEI_SOURCE"})
    glyphs = glyph_table(trees["chardec"])
    checks = fixtures(glyphs)
    if args.fixtures_only:
        print(json.dumps(checks)); return
    body = trees["b4"].find("t:text/t:body", NS); ab = body.find("t:ab", NS)
    page_names = [x.get("n") for x in body.iter() if local(x) == "pb"]
    assert all(re.fullmatch(r"\d+[rv]", x or "") for x in page_names)
    leaves = sorted({int(x[:-1]) for x in page_names})
    assert all({f"{x:03d}r", f"{x:03d}v"} <= set(page_names) for x in leaves)
    cut = leaves[len(leaves) // 2 - 1]
    records = []; current_page = None
    for child in ab:
        if local(child) == "pb":
            current_page = child.get("n"); continue
        if local(child) != "seg":
            raise ValueError(f"Unaccounted top-level body element: {local(child)}")
        pages, source_events = set(), []
        for x in child.iter():
            if local(x) == "pb": current_page = x.get("n")
            assert current_page is not None
            pages.add(current_page)
            if local(x) in {"pb", "lb", "cb"}:
                source_events.append({"tag": local(x), "page": current_page, "attributes": x.attrib})
        leaf_set = sorted({int(x[:-1]) for x in pages})
        split = "TRAIN" if max(leaf_set) <= cut else "TEST" if min(leaf_set) > cut else "BRIDGE"
        projection = Projection(glyphs); projection.visit(child); projection.boundary()
        rid = f"R{len(records) + 1:04d}"
        for i, word in enumerate(projection.words):
            word["occurrence_id"] = f"{rid}:W{i:05d}"; word["word_index"] = i
        records.append({"record_id": rid, "source_locator": f"/TEI/text/body/ab/seg[{len(records)+1}]",
                        "physical_leaves": leaf_set, "pages": sorted(pages), "split": split,
                        "source_events": source_events,
                        "original_element_xml": ET.tostring(child, encoding="unicode"),
                        "words": projection.words})
    alphabet = sorted({k for r in records for w in r["words"] for k in w["native_keys"] if k is not None})
    permutation = list(range(len(alphabet))); random.Random(20261003).shuffle(permutation)
    opaque = dict(zip(alphabet, permutation))
    for record in records:
        for word in record["words"]:
            word["atoms"] = [opaque[k] if k is not None else -1 for k in word["native_keys"]]
    def packet(split):
        rows = [{"record_id": r["record_id"], "words": [w["atoms"] for w in r["words"]]}
                for r in records if r["split"] == split]
        counts = collections.Counter(tuple(w) for r in rows for w in r["words"])
        return {"schema_version": 1, "n_atoms": len(alphabet), "unknown_atom": -1,
                "records": rows, "words": [{"atoms": list(w), "count": c} for w, c in sorted(counts.items())]}
    reference_counts = collections.Counter(); reference_receipts = []
    for name in ["b6", "br1", "bs1", "gr1", "w1"]:
        refbody = trees[name].find("t:text/t:body", NS)
        words, unknowns = reference_words(refbody, glyphs)
        reference_counts.update(words)
        reference_receipts.append({"source": name, "sha256": PINS[name],
                                   "word_occurrences": len(words), "unknown_word_spans": unknowns})
    artifacts = ROOT / "artifacts"
    dump(artifacts / "TRAIN_INPUT.json", packet("TRAIN"))
    dump(artifacts / "HOLDOUT_INPUT.json", packet("TEST"))
    dump(artifacts / "REFERENCE_INPUT.json", {"schema_version": 1, "source_hashes": reference_receipts,
         "words": [{"word": w, "count": c} for w, c in sorted(reference_counts.items())]})
    dump(artifacts / "SOURCE_GOLD_LEDGER.json", {"schema_version": 1, "records": records}, compact=True)
    dump(artifacts / "OPAQUE_KEY_PRIVATE_TO_PREPARATION.json", {"seed": 20261003,
         "symbols": [{"character": k, "atom_id": opaque[k]} for k in alphabet]})
    split_receipt = {"ordered_physical_leaves": leaves, "cut_after_leaf": cut,
        "train_physical_leaves": leaves[:len(leaves)//2], "test_physical_leaves": leaves[len(leaves)//2:],
        "complete_recto_verso_pairs": True,
        "record_counts": dict(collections.Counter(r["split"] for r in records)),
        "bridge_record_ids": [r["record_id"] for r in records if r["split"] == "BRIDGE"]}
    outputs = [artifacts / name for name in ["TRAIN_INPUT.json", "HOLDOUT_INPUT.json", "REFERENCE_INPUT.json",
               "SOURCE_GOLD_LEDGER.json", "OPAQUE_KEY_PRIVATE_TO_PREPARATION.json"]]
    dump(artifacts / "SOURCE_RECEIPT.json", {"schema_version": 1, "source_pins": receipts,
        "projection_fixtures": checks, "split": split_receipt, "n_atoms": len(alphabet),
        "outputs": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p.read_bytes()),
                      "bytes": len(p.read_bytes())} for p in outputs],
        "claim_ceiling": "Source preparation only; no candidate recovery or oracle capacity scored"})
    dump(ROOT / "src" / "SOURCE.json", {"schema_version": 1, "source_pins": receipts,
         "control": "B4 original TEI only", "external_reference": ["b6", "br1", "bs1", "gr1", "w1"],
         "text_license": "CC BY4.0", "split": split_receipt,
         "model_input_paths": ["artifacts/TRAIN_INPUT.json", "artifacts/REFERENCE_INPUT.json"],
         "held_input_path": "artifacts/HOLDOUT_INPUT.json",
         "forbidden_fitter_paths": ["artifacts/SOURCE_GOLD_LEDGER.json", "artifacts/OPAQUE_KEY_PRIVATE_TO_PREPARATION.json"],
         "seed": 20261003, "unknown_atom": -1,
         "policy_document": "PREPARATION.md"})
    print(json.dumps({"status": "SOURCE_PREPARED_NOT_SCORED", "fixtures": checks["status"],
                      "split": split_receipt, "n_atoms": len(alphabet)}))


if __name__ == "__main__":
    main()
