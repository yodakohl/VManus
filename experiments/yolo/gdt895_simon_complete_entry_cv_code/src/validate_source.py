#!/usr/bin/env python3
"""Independent strict source reconstruction; imports no primary parser or target data."""
from __future__ import annotations

import argparse
import base64
import collections
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urlsplit

CAPTURE_SHA256 = "033800bc117abe9031364800c703d4b061299d47a642b53398bd478429f9d322"
MARKERS = {"Apparatus:", "Translation:", "Commentary:"}
INLINE = {"a", "b", "i", "em", "strong", "span", "br"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
ACQUIRED = {"ACQUIRED", "ACQUIRED_FROM_IDENTICAL_CAPTURE_CACHE"}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def squash(text):
    return " ".join(text.split())


class Node:
    def __init__(self, tag, attrs=(), start=0):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.start = start
        self.end = None
        self.duplicate_attrs = len(self.attrs) != len(attrs)


class StrictTree(HTMLParser):
    """Track malformed nesting rather than silently repairing an HTML fragment."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.document = Node("#document")
        self.stack = [self.document]
        self.errors = []
        self.serial = 0

    def tick(self):
        self.serial += 1
        return self.serial

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.tick())
        self.stack[-1].children.append(n)
        if tag in VOID:
            n.end = n.start
        else:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        pos = self.tick()
        if len(self.stack) > 1 and self.stack[-1].tag == tag:
            self.stack.pop().end = pos
            return
        self.errors.append((pos, "UNBALANCED_TAG:" + tag))
        # Recover only to continue the audit; this error remains rejectable.
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack[i].end = pos
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.tick()
        self.stack[-1].children.append(data)

    def handle_comment(self, data):
        self.tick()

    def handle_decl(self, decl):
        self.tick()

    def unknown_decl(self, data):
        self.errors.append((self.tick(), "UNKNOWN_DECLARATION"))


def nodes(node):
    if isinstance(node, Node):
        yield node
        for child in node.children:
            yield from nodes(child)


def rendered(node):
    if isinstance(node, str):
        return node
    if node.tag == "br":
        return "\n"
    return "".join(rendered(x) for x in node.children)


def hidden(node):
    a = node.attrs
    style = re.sub(r"\s+", "", (a.get("style") or "").lower())
    return ("hidden" in a or (a.get("aria-hidden") or "").lower() == "true"
            or "display:none" in style or "visibility:hidden" in style
            or "line-through" in style)


def inline_problems(block, marker=False):
    problems = []
    allowed = {"span", "br"} if marker else INLINE
    for n in nodes(block):
        if n is not block and n.tag not in allowed:
            problems.append("UNSUPPORTED_INLINE:" + n.tag)
        if n.end is None:
            problems.append("UNCLOSED_MAIN_TAG:" + n.tag)
        if n.duplicate_attrs:
            problems.append("DUPLICATE_ATTRIBUTES")
        if hidden(n):
            problems.append("HIDDEN_OR_STRUCK_TEXT")
        style = (n.attrs.get("style") or "").lower()
        if not marker and any(x in style for x in ("color", "font-weight", "display")):
            problems.append("UNREVIEWED_STYLED_MAIN_TEXT")
        if (n.attrs.get("class") or "").split() and any(
                x in {"reference", "mw-ref", "noprint", "error"}
                for x in n.attrs["class"].split()):
            problems.append("EDITORIAL_OR_REFERENCE_CLASS")
    return problems


def extract(raw):
    """Return the exact complete initial edition block, or explicit quarantine."""
    reasons = []
    try:
        html = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {"eligible": False, "reasons": ["INVALID_UTF8"]}
    tree = StrictTree()
    try:
        tree.feed(html)
        tree.close()
    except Exception as exc:
        return {"eligible": False, "reasons": ["HTML_PARSE_ERROR:" + type(exc).__name__]}
    content = [n for n in nodes(tree.document) if n.attrs.get("id") == "mw-content-text"]
    if len(content) != 1:
        return {"eligible": False, "reasons": ["CONTENT_DIV_NOT_UNIQUE"]}
    content = content[0]
    if (any(content.start <= pos <= (content.end or tree.serial) for pos, _ in tree.errors)
            or any(n.end is None for n in nodes(content))):
        reasons.append("MALFORMED_CONTENT_STRUCTURE")
    if content.tag != "div" or content.end is None:
        reasons.append("CONTENT_DIV_NOT_CLOSED")
    if hidden(content) or content.duplicate_attrs:
        reasons.append("INVALID_CONTENT_ATTRIBUTES")
    parts, marker, boundary, paragraph_count = [], None, None, 0
    main_tags = collections.Counter()
    for block in content.children:
        if isinstance(block, str):
            if block.strip():
                reasons.append("NONPARAGRAPH_MAIN_TEXT")
            continue
        text = squash(rendered(block))
        if text in MARKERS:
            marker, boundary = text, block.start
            if block.tag != "p":
                reasons.append("NONPARAGRAPH_MARKER")
            reasons.extend(inline_problems(block, marker=True))
            break
        if block.tag != "p":
            reasons.append("UNSUPPORTED_MAIN_BLOCK:" + block.tag)
        reasons.extend(inline_problems(block))
        main_tags.update(n.tag for n in nodes(block))
        parts.append(rendered(block))
        paragraph_count += bool(text)
    if marker is None:
        reasons.append("NO_STANDALONE_EDITORIAL_MARKER")
    end = boundary if boundary is not None else (content.end or tree.serial)
    reasons.extend(problem for pos, problem in tree.errors if content.start <= pos <= end)
    main = squash("\n".join(parts))
    if not main:
        reasons.append("EMPTY_MAIN_TEXT")
    if any(c in main for c in "$?[]<>{}…") or "..." in main:
        reasons.append("UNCERTAIN_OR_INTERPOLATED_TEXT")
    accepted = set(".,;:!()")
    bad = sorted({c for c in main if not (
        "a" <= c <= "z" or "A" <= c <= "Z" or c in "æÆœŒ"
        or c.isspace() or c in accepted)})
    if bad:
        reasons.append("UNSUPPORTED_MAIN_CHARACTERS:" + " ".join("U+%04X" % ord(c) for c in bad))
    ligatures = {"æ": "ae", "Æ": "ae", "œ": "oe", "Œ": "oe"}
    normalized = "".join(c.lower() if "A" <= c <= "Z" else ligatures.get(c, c) for c in main)
    words = re.findall(r"[a-z]+", normalized)
    if not words:
        reasons.append("NO_LATIN_WORDS")
    result = {"eligible": not reasons, "reasons": sorted(set(reasons)),
              "main_text": main, "words": words, "boundary_marker": marker,
              "paragraph_count": paragraph_count,
              "main_tags": dict(sorted(main_tags.items())),
              "main_text_sha256": sha256(main.encode()),
              "words_sha256": sha256(json.dumps(words, ensure_ascii=False, separators=(",", ":")).encode())}
    headings = [squash(rendered(n)) for n in nodes(tree.document) if n.attrs.get("id") == "firstHeading"]
    result["heading"] = headings[0] if len(headings) == 1 else None
    result["document_titles"] = [squash(rendered(n)) for n in nodes(tree.document) if n.tag == "title"]
    for field in ("wgTitle", "wgPageName"):
        values = re.findall(r'"' + field + r'"\s*:\s*("(?:[^"\\]|\\.)*")', html)
        result[field] = [json.loads(v) for v in values]
    result["revision_ids"] = [int(v) for v in re.findall(r'"wgRevisionId"\s*:\s*(\d+)', html)]
    permalink_owners = [n for n in nodes(tree.document) if n.attrs.get("id") == "t-permalink"
                        or "printfooter" in (n.attrs.get("class") or "").split()]
    result["permalink_oldids"] = sorted({int(v) for owner in permalink_owners for n in nodes(owner)
        if n.tag == "a" for v in parse_qs(urlsplit(n.attrs.get("href") or "").query).get("oldid", []) if v.isdigit()})
    return result


def title_normal(title):
    return squash(title.replace("_", " "))


def archive_parts(url):
    match = re.fullmatch(r"https?://web\.archive\.org/web/(\d{14})(?:id_)?/(https?://.+)", url or "")
    if not match:
        return None
    return match.group(1), match.group(2)


def verify_binding(record, receipt, raw, parsed):
    problems = []
    if receipt.get("id") != record["id"] or receipt.get("title") != record["title"]:
        problems.append("RECEIPT_ID_TITLE_MISMATCH")
    if receipt.get("selected") != record.get("selected"):
        problems.append("SELECTED_CAPTURE_MISMATCH")
    if receipt.get("sha256") != sha256(raw) or receipt.get("bytes") != len(raw):
        problems.append("RAW_HASH_OR_LENGTH_MISMATCH")
    selected = record.get("selected") or {}
    digest = base64.b32encode(hashlib.sha1(raw).digest()).decode().rstrip("=")
    if selected.get("digest") != digest:
        problems.append("CDX_PAYLOAD_DIGEST_MISMATCH")
    if receipt.get("requested_url") != record.get("replay_url"):
        problems.append("REQUESTED_CAPTURE_MISMATCH")
    wanted = (selected.get("timestamp"), selected.get("original"))
    if archive_parts(receipt.get("final_url")) != wanted:
        problems.append("FINAL_CAPTURE_MISMATCH")
    expected = title_normal(record["title"])
    if parsed.get("heading") != expected:
        problems.append("HEADING_TITLE_MISMATCH")
    if parsed.get("wgTitle") != [expected]:
        problems.append("CONFIG_TITLE_MISMATCH")
    if len(parsed.get("wgPageName", [])) != 1 or title_normal(parsed["wgPageName"][0]) != expected:
        problems.append("CONFIG_PAGE_MISMATCH")
    if parsed.get("document_titles") != [expected + " - Simon Online"]:
        problems.append("DOCUMENT_TITLE_MISMATCH")
    if parsed.get("revision_ids") != [receipt.get("oldid")] or not receipt.get("oldid"):
        problems.append("REVISION_MISMATCH")
    if parsed.get("permalink_oldids") != [receipt.get("oldid")]:
        problems.append("PERMALINK_REVISION_MISMATCH")
    if receipt.get("status") == "ACQUIRED":
        matches = [a for a in receipt.get("attempts", []) if a.get("sha256") == sha256(raw)
                   and a.get("final_url") == receipt.get("final_url") and a.get("http_status") == 200]
        if not matches:
            problems.append("NO_SUCCESSFUL_BOUND_ATTEMPT")
    return problems


def verify_captures(corpus, raw, captures):
    problems = []
    if sha256(raw) != CAPTURE_SHA256:
        problems.append("FROZEN_CAPTURES_HASH_MISMATCH")
    anchor = dt.datetime.strptime(captures["anchor"], "%Y%m%d%H%M%S")
    seen_ids, seen_titles = set(), set()
    for r in captures["records"]:
        if r["id"] in seen_ids or r["title"] in seen_titles:
            problems.append("DUPLICATE_CAPTURE_ID_OR_TITLE")
        seen_ids.add(r["id"]); seen_titles.add(r["title"])
        eligible = r.get("candidate_captures", [])
        for c in eligible:
            p = urlsplit(c["original"])
            title = parse_qs(p.query, keep_blank_values=True).get("title", [])
            if title != [r["title"]] or p.hostname not in {"simonofgenoa.org", "www.simonofgenoa.org"}:
                problems.append("CAPTURE_ORIGINAL_TITLE_MISMATCH:" + r["id"])
        def key(c):
            when = dt.datetime.strptime(c["timestamp"], "%Y%m%d%H%M%S")
            return (abs((when - anchor).total_seconds()), when, c["original"])
        chosen = min(eligible, key=key) if eligible else None
        if r.get("selected") != chosen:
            problems.append("NONNEAREST_CAPTURE:" + r["id"])
    cdx = corpus / "CDX_ALL.raw"
    if not cdx.is_file() or sha256(cdx.read_bytes()) != captures["cdx_sha256"]:
        problems.append("CDX_RAW_HASH_MISMATCH")
    return sorted(set(problems))


def validate(corpus, source_pool=None):
    capture_raw = (corpus / "CAPTURES.json").read_bytes()
    captures = json.loads(capture_raw)
    issues = [{"id": None, "reasons": verify_captures(corpus, capture_raw, captures)}]
    issues = [i for i in issues if i["reasons"]]
    records, expected, pending, receipt_hashes, receipt_values = [], {}, [], {}, {}
    counts = collections.Counter()
    for record in captures["records"]:
        ident = record["id"]
        path = corpus / "receipts" / (ident + ".json")
        if not path.is_file():
            pending.append(ident); counts["MISSING_RECEIPT"] += 1
            continue
        receipt_raw = path.read_bytes()
        receipt = json.loads(receipt_raw)
        receipt_hashes[ident + ".json"] = sha256(receipt_raw)
        receipt_values[ident] = receipt
        status = receipt.get("status", "INVALID_RECEIPT")
        counts[status] += 1
        if status == "PENDING":
            pending.append(ident)
        if status not in ACQUIRED:
            continue
        if receipt.get("file") != "html/" + ident + ".html":
            issues.append({"id": ident, "reasons": ["INVALID_BODY_FILENAME"]})
            continue
        body = corpus / receipt["file"]
        if not body.is_file():
            issues.append({"id": ident, "reasons": ["MISSING_ACQUIRED_BODY"]})
            continue
        raw = body.read_bytes()
        parsed = extract(raw)
        problems = verify_binding(record, receipt, raw, parsed)
        if problems:
            issues.append({"id": ident, "reasons": problems})
        expected[ident] = {"id": ident, "title": record["title"], "html_sha256": sha256(raw),
                           "oldid": receipt.get("oldid"), **parsed}
        records.append({"id": ident, "title": record["title"], "html_sha256": sha256(raw),
                        "receipt_sha256": sha256(receipt_raw), "oldid": receipt.get("oldid"),
                        "eligible": parsed["eligible"], "reasons": parsed["reasons"],
                        "word_count": len(parsed.get("words", [])),
                        "main_text_sha256": parsed.get("main_text_sha256"),
                        "words_sha256": parsed.get("words_sha256"),
                        "boundary_marker": parsed.get("boundary_marker"),
                        "main_tags": parsed.get("main_tags", {})})
    pool_hash = None
    pool_status = None
    if source_pool is not None:
        pool_raw = source_pool.read_bytes(); pool_hash = sha256(pool_raw)
        pool = json.loads(pool_raw)
        pool_status = pool.get("status")
        if pool.get("capture_sha256") != sha256(capture_raw):
            issues.append({"id": None, "reasons": ["SOURCE_POOL_CAPTURE_HASH_MISMATCH"]})
        entries = pool.get("entries", [])
        exclusions = pool.get("exclusions", [])
        pool_pending = {e["id"] for e in pool.get("pending", [])}
        actual = {e["id"]: e for e in entries}
        excluded = {e["id"]: e for e in exclusions}
        if len(actual) != len(entries):
            issues.append({"id": None, "reasons": ["DUPLICATE_SOURCE_ENTRY"]})
        declared = list(actual) + list(excluded) + list(pool_pending)
        if (len(excluded) != len(exclusions) or len(declared) != len(set(declared))
                or set(declared) != {r["id"] for r in captures["records"]}):
            issues.append({"id": None, "reasons": ["SOURCE_POOL_PARTITION_MISMATCH"]})
        # Pending receipts may advance while an explicitly unfrozen pool is audited.
        # Completed receipts and their raw bodies must remain exactly bound.
        frozen_hashes = dict(pool.get("receipt_hashes", []))
        if len(frozen_hashes) != len(captures["records"]):
            issues.append({"id": None, "reasons": ["SOURCE_POOL_RECEIPT_INVENTORY_MISMATCH"]})
        for filename, digest in frozen_hashes.items():
            ident = filename.removesuffix(".json")
            if ident not in pool_pending and receipt_hashes.get(filename) != digest:
                issues.append({"id": ident, "reasons": ["SOURCE_POOL_RECEIPT_HASH_MISMATCH"]})
        wanted = {i for i, r in expected.items() if r["eligible"] and i not in pool_pending}
        if set(actual) != wanted:
            issues.append({"id": None, "reasons": ["SOURCE_POOL_ID_SET_MISMATCH"],
                           "missing": sorted(wanted - set(actual)), "extra": sorted(set(actual) - wanted)})
        for i in sorted(wanted & set(actual)):
            for field in ("title", "html_sha256", "oldid", "words", "main_text"):
                if actual[i].get(field) != expected[i].get(field):
                    issues.append({"id": i, "reasons": ["SOURCE_POOL_FIELD_MISMATCH:" + field]})
            for field, independent in (("boundary", "boundary_marker"), ("paragraph_count", "paragraph_count")):
                if actual[i].get(field) != expected[i].get(independent):
                    issues.append({"id": i, "reasons": ["SOURCE_POOL_FIELD_MISMATCH:" + field]})
        for i, e in excluded.items():
            if not e.get("reason"):
                issues.append({"id": i, "reasons": ["MISSING_EXCLUSION_REASON"]})
            if i in expected:
                if expected[i]["eligible"]:
                    issues.append({"id": i, "reasons": ["ELIGIBLE_BODY_EXCLUDED"]})
                for field in ("title", "html_sha256", "oldid"):
                    if e.get(field) != expected[i].get(field):
                        issues.append({"id": i, "reasons": ["SOURCE_EXCLUSION_FIELD_MISMATCH:" + field]})
            elif receipt_values.get(i, {}).get("status") == "PENDING":
                issues.append({"id": i, "reasons": ["PENDING_RECEIPT_CALLED_EXCLUDED"]})
        for i, e in {**actual, **excluded}.items():
            r = receipt_values.get(i, {})
            if i in expected and (e.get("capture") != r.get("selected") or e.get("final_url") != r.get("final_url")):
                issues.append({"id": i, "reasons": ["SOURCE_POOL_CAPTURE_FIELDS_MISMATCH"]})
        pending = sorted(set(pending) | pool_pending)
    eligible_count = sum(r["eligible"] for r in records)
    return {"schema": "gdt895-independent-source-validation-v1",
            "status": "FAIL" if issues else "INCOMPLETE" if pending or pool_status == "INCREMENTAL_UNFROZEN" else "PASS",
            "capture_sha256": sha256(capture_raw), "source_pool_sha256": pool_hash,
            "source_pool_status": pool_status,
            "validator_sha256": sha256(Path(__file__).read_bytes()),
            "counts": dict(sorted(counts.items())), "reviewed_bodies": len(records),
            "eligible_bodies": eligible_count, "quarantined_bodies": len(records) - eligible_count,
            "pending": pending, "issues": issues, "records": records,
            "claim_ceiling": "Independent reconstruction of the partial eclectic edition only; no target or meaning test."}


def self_test():
    def page(main, tail="<p><br/><span>Translation:</span></p><p>Modern Latin aqua.</p>"):
        return ("<html><body><div id='mw-content-text'>" + main + tail + "</div></body></html>").encode()
    clean = extract(page("<p>A<i>qu</i>a et <a href='x'>uena</a>.</p><p>Æqua<br/>œs.</p>"))
    assert clean["eligible"] and clean["words"] == ["aqua", "et", "uena", "aequa", "oes"]
    assert clean["main_text"] == "Aqua et uena. Æqua œs."
    cases = [
        ("<p>Aqua?</p>", None), ("<p>Aqua ... est.</p>", None),
        ("<p>Aqua &lt;est&gt;.</p>", None), ("<p>Aqua 1.</p>", None),
        ("<p>Aqua-rosae.</p>", None), ("<p>Aqua &amp; rosa.</p>", None),
        ("<p>Aqua<sup>1</sup>.</p>", None), ("<p>Aqua<img src='x'/></p>", None),
        ("<table><tr><td>Aqua</td></tr></table>", None),
        ("<p><span style='display: none'>Aqua</span>rosa.</p>", None),
        ("<p>Aqua <i>rosae</p>", None),
        ("<p>Aqua.</p>", "<p>Modern commentary without marker.</p>"),
        ("<p>Aqua.</p>", "<p>Translation: aqua is water.</p>"),
        ("<p>Aqua.</p>", "<h2>Translation:</h2>"),
        ("<p>Aqua.</p>", "<p><b>Translation:</b></p>"),
        ("<p><span style='color:green'>Complete text of entry:</span></p><p>Aqua.</p>", None),
        ("<p><span aria-hidden='true'>Aqua</span></p>", None),
        ("<p><span style='text-decoration:line-through'>Aqua</span></p>", None),
        ("<p><span class='noprint'>Aqua</span></p>", None),
        ("<p>Kelvin.</p>", None),
        ("<p>Aqua.</p>", "<p><span>Translation:</span></p><p><i>Broken.</p>"),
        ("<p>Aqua.</p>", "<p><span>Translation:</span></p>")]
    for i, (main, tail) in enumerate(cases):
        result = extract(page(main) if tail is None else page(main, tail))
        assert result["eligible"] == (i == len(cases) - 1), (i, result)
    full = ("<html><head><title>Aqua - Simon Online</title><script>"
            '{"wgTitle":"Aqua","wgPageName":"Aqua","wgRevisionId":7}'
            "</script></head><body><h1 id='firstHeading'>Aqua</h1>"
            "<div id='mw-content-text'><p>Aqua.</p><p>Translation:</p></div>"
            "<li id='t-permalink'><a href='http://simonofgenoa.org/index.php?title=Aqua&amp;oldid=7'>permalink</a></li>"
            "</body></html>").encode()
    selected = {"timestamp": "20220812000000", "original": "http://simonofgenoa.org/index.php?title=Aqua",
                "digest": base64.b32encode(hashlib.sha1(full).digest()).decode().rstrip("=")}
    url = "https://web.archive.org/web/20220812000000id_/" + selected["original"]
    record = {"id": "0000", "title": "Aqua", "selected": selected, "replay_url": url}
    receipt = {**record, "requested_url": url, "final_url": url, "bytes": len(full),
               "sha256": sha256(full), "oldid": 7, "status": "ACQUIRED_FROM_IDENTICAL_CAPTURE_CACHE"}
    parsed = extract(full)
    assert parsed["eligible"] and not verify_binding(record, receipt, full, parsed)
    mutations = [("sha256", "0" * 64, "RAW_HASH_OR_LENGTH_MISMATCH"),
                 ("oldid", 8, "REVISION_MISMATCH"),
                 ("title", "Rosa", "RECEIPT_ID_TITLE_MISMATCH"),
                 ("final_url", url.replace("20220812", "20220813"), "FINAL_CAPTURE_MISMATCH")]
    for field, value, reason in mutations:
        assert reason in verify_binding(record, {**receipt, field: value}, full, parsed)
    assert "CDX_PAYLOAD_DIGEST_MISMATCH" in verify_binding(record, receipt, full + b" ", parsed)
    return {"status": "PASS", "synthetic_cases": 1 + len(cases) + 1 + len(mutations) + 1}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus", type=Path)
    p.add_argument("--source-pool", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True)); return 0
    if args.corpus is None:
        p.error("--corpus is required except for --self-test")
    result = validate(args.corpus, args.source_pool)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    summary = {k: v for k, v in result.items() if k not in {"records", "pending", "issues"}}
    summary.update(pending_count=len(result["pending"]), issue_count=len(result["issues"]), issues=result["issues"][:12])
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
