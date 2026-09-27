"""Reproduce the selected complete source chapter from the recorded TITUS HTML.

No network, OCR, target data or semantic inference. Usage:
  python EXTRACT_MEGENBERG_II25.py INPUT_HTML
The exact source text is written to stdout after both input/output hash checks.
"""
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import sys

INPUT_SHA = "e6fbf4806c01415a848a6be173b2dfc82862dca9fb5c5732aaa8945559e03dbc"
OUTPUT_SHA = "c3f9442fe6b2134f3d93f6efa8f65b45d57bdcfc65e8c2a0e31071a2855cd61b"


class Chapter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.keep = False
        self.starts = self.ends = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        name = dict(attrs).get("name")
        if tag == "a" and name == "Konr.Meg._Nat._II_25":
            self.keep = True
            self.starts += 1
        if tag == "a" and name == "Konr.Meg._Nat._II_26":
            self.keep = False
            self.ends += 1
        if self.keep and tag in ("br", "div"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.keep and tag == "div":
            self.parts.append("\n")

    def handle_data(self, data):
        if self.keep:
            self.parts.append(data)


def extract(blob):
    if sha256(blob).hexdigest() != INPUT_SHA:
        raise ValueError("Input differs from the registered institutional HTML")
    parser = Chapter()
    parser.feed(blob.decode("utf-8", errors="replace"))
    if (parser.starts, parser.ends) != (1, 1):
        raise ValueError("Complete chapter boundaries are not unique")
    lines = (" ".join(line.split()) for line in "".join(parser.parts).splitlines() if line.strip())
    result = ("\n".join(lines) + "\n").encode("utf-8")
    if sha256(result).hexdigest() != OUTPUT_SHA:
        raise ValueError("Selected text differs from the registered extraction")
    return result


if __name__ == "__main__":
    sys.stdout.buffer.write(extract(Path(sys.argv[1]).read_bytes()))
