"""Strict source-only extraction. The modern edition cache is never published."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

MARKERS = {"Apparatus:", "Translation:", "Commentary:"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
INLINE = {"a", "b", "i", "em", "strong", "span", "br"}
SUCCESS = {"ACQUIRED", "ACQUIRED_FROM_IDENTICAL_CAPTURE_CACHE"}


class Node:
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []


class MainTree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = None
        self.stack = []
        self.closed = False
        self.errors = []
        self.main_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "div" and dict(attrs).get("id") == "mw-content-text":
            self.main_count += 1
            if self.root is not None:
                self.errors.append("duplicate_main")
            else:
                self.root = Node(tag, attrs)
                self.stack = [self.root]
                return
        if not self.stack:
            return
        child = Node(tag, attrs)
        self.stack[-1].children.append(child)
        if tag not in VOID:
            self.stack.append(child)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or tag in VOID:
            return
        if self.stack[-1].tag != tag:
            self.errors.append("mismatched_end:" + tag)
            return
        self.stack.pop()
        if not self.stack:
            self.closed = True

    def handle_data(self, data):
        if self.stack:
            self.stack[-1].children.append(data)


def rendered(node):
    if isinstance(node, str):
        return node
    if node.tag == "br":
        return "\n"
    return "".join(rendered(x) for x in node.children)


def descendants(node):
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from descendants(child)


def extract(data):
    result = {"html_sha256": hashlib.sha256(data).hexdigest(), "status": "EXCLUDED"}
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {**result, "reason": "INVALID_UTF8"}
    parser = MainTree()
    parser.feed(text)
    parser.close()
    if not parser.root or not parser.closed or parser.errors or parser.main_count != 1:
        return {**result, "reason": "INCOMPLETE_OR_MALFORMED_MAIN", "details": parser.errors}
    before = []
    boundary = None
    for child in parser.root.children:
        content = re.sub(r"\s+", " ", rendered(child)).strip()
        if not content:
            continue
        if content in MARKERS and isinstance(child, Node) and child.tag == "p":
            boundary = content
            break
        before.append(child)
    if boundary is None:
        return {**result, "reason": "MISSING_EXPLICIT_EDITORIAL_BOUNDARY"}
    if not before:
        return {**result, "reason": "EMPTY_MAIN"}
    paragraphs = []
    for child in before:
        if isinstance(child, str) or child.tag != "p":
            return {**result, "reason": "UNSUPPORTED_MAIN_STRUCTURE"}
        for node in descendants(child):
            if node is not child and node.tag not in INLINE:
                return {**result, "reason": "UNSUPPORTED_MAIN_TAG", "details": node.tag}
            style = re.sub(r"\s+", "", node.attrs.get("style", "")).lower()
            classes = set(node.attrs.get("class", "").lower().split())
            if "color:" in style or "font-weight:" in style or "display:" in style or classes.intersection({"noprint", "reference"}):
                return {**result, "reason": "UNSUPPORTED_EDITORIAL_MAIN_MARKUP"}
            if ("hidden" in node.attrs or node.attrs.get("aria-hidden", "").lower() == "true"
                    or "display:none" in style or "visibility:hidden" in style
                    or "line-through" in style):
                return {**result, "reason": "HIDDEN_MAIN_CONTENT"}
        paragraphs.append(rendered(child))
    main_text = " ".join("\n".join(paragraphs).split())
    if any(c in main_text for c in "$?[]<>{}…") or "..." in main_text:
        return {**result, "reason": "EXPLICIT_MAIN_UNCERTAINTY"}
    # No combining marks are dropped: a medieval macron may be an abbreviation.
    replacements = {chr(c): chr(c + 32) for c in range(ord("A"), ord("Z") + 1)}
    replacements.update({"æ": "ae", "Æ": "ae", "œ": "oe", "Œ": "oe"})
    normalized = main_text.translate(str.maketrans(replacements))
    unsupported = sorted(set(re.sub(r"[a-z\s.,;:!()]", "", normalized)))
    if unsupported:
        return {**result, "reason": "UNSUPPORTED_SOURCE_CHARACTER", "details": unsupported}
    words = re.findall(r"[a-z]+", normalized)
    if not words:
        return {**result, "reason": "EMPTY_WORD_SEQUENCE"}
    return {**result, "status": "ACCEPTED", "boundary": boundary,
            "main_text": main_text, "words": words, "paragraph_count": len(paragraphs)}


def build_pool(cache):
    capture_file = cache / "CAPTURES.json"
    captures = json.loads(capture_file.read_text())
    entries, exclusions, pending = [], [], []
    receipt_hashes = []
    for path in sorted((cache / "receipts").glob("*.json")):
        raw = path.read_bytes()
        receipt_hashes.append([path.name, hashlib.sha256(raw).hexdigest()])
        receipt = json.loads(raw)
        base = {"id": receipt["id"], "title": receipt["title"], "receipt": path.name}
        if receipt["status"] not in SUCCESS:
            dest = pending if receipt["status"] == "PENDING" else exclusions
            dest.append({**base, "reason": receipt["status"]})
            continue
        relative = Path(receipt["file"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("source receipt escapes cache")
        body = (cache / relative).read_bytes()
        parsed = extract(body)
        if parsed["html_sha256"] != receipt["sha256"]:
            raise ValueError("source HTML hash mismatch: " + str(base["id"]))
        base.update(html_sha256=parsed["html_sha256"], oldid=receipt["oldid"],
                    capture=receipt["selected"], final_url=receipt["final_url"])
        if parsed["status"] == "ACCEPTED":
            entries.append({**base, **parsed})
        else:
            exclusions.append({**base, **parsed})
    return {"schema": "gdt895-source-pool-v1", "status": "INCREMENTAL_UNFROZEN" if pending else "COMPLETE_RECEIPT_SCAN_NOT_YET_VALIDATED",
            "source_scope": "partial archived eclectic edition; not complete Simon lexicon or diplomatic witness",
            "capture_sha256": hashlib.sha256(capture_file.read_bytes()).hexdigest(),
            "receipt_hashes": receipt_hashes, "entries": entries, "exclusions": exclusions, "pending": pending,
            "counts": {"entries": len(entries), "exclusions": len(exclusions), "pending": len(pending),
                       "source_words": sum(len(e["words"]) for e in entries)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True, help="Local edition cache output, not a public repository artifact")
    args = ap.parse_args()
    result = build_pool(args.cache)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], **result["counts"]}))


if __name__ == "__main__":
    main()
