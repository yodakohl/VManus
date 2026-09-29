#!/usr/bin/env python3
"""Extract only the declared historical entries; no Voynich data access."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
import hashlib
import json
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
NS = {'t': 'http://www.tei-c.org/ns/1.0'}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def clean_html(fragment):
    fragment = re.sub(r'<a\b[^>]*class="fnanchor"[^>]*>.*?</a>', '',
                      fragment, flags=re.S)
    fragment = re.sub(r'<span\b[^>]*class="pagenum"[^>]*>.*?</span>', '',
                      fragment, flags=re.S)
    parser = Text()
    parser.feed(fragment)
    return ' '.join(''.join(parser.parts).split())


def receipt(path, url, attribution, license_note):
    return dict(path=path.relative_to(ROOT).as_posix(), url=url,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                attribution=attribution, license_note=license_note)


def greek_main(node):
    parts = [node.text or '']
    for child in node:
        if child.tag.rsplit('}', 1)[-1] != 'note':
            parts.append(greek_main(child))
        parts.append(child.tail or '')
    return ''.join(parts)


def build():
    ppath = BASE / 'D_SOURCE_PLINY_IV.html'
    original = ppath.read_text()
    fragment = original.split('<h3 id="BOOK_XXII_CHAP_29">', 1)[1]
    fragment = fragment.split('<h3 id="BOOK_XXII_CHAP_30">', 1)[0]
    paragraphs = [clean_html(p) for p in re.findall(r'<p>(.*?)</p>', fragment, re.S)]
    assert len(paragraphs) == 3
    notes = {}
    for n in range(2596, 2613):
        raw = original.split(f'<a id="Footnote_{n}_{n}"></a>', 1)[1].split('</p>', 1)[0]
        notes[str(n)] = clean_html(raw)
    pliny = dict(
        source=receipt(ppath, 'https://www.gutenberg.org/files/61113/61113-h/61113-h.htm#BOOK_XXII_CHAP_29',
                       'Pliny, Natural History XXII.29, Bostock/Riley historical translation, volume IV',
                       'Historical text and translation public domain; Gutenberg site boilerplate is not reproduced.'),
        unit='Entire XXII.29, all three HTML authorial paragraphs and notes2596–2612',
        paragraphs=paragraphs, editorial_notes=notes,
        qualification='Notes are the modern historical edition, not Pliny; current botanical identity is unestablished.')

    dpath = ROOT / 'research_registry/work_batches/ten_hours_20260915/dioscorides_cache/Wellmann_DMM.xml'
    doc = ET.parse(dpath).getroot()
    chapters = {}
    for number in ('190', '191'):
        found = doc.findall(f'.//t:div[@subtype="book"][@n="4"]//t:div[@subtype="chapter"][@n="{number}"]', NS)
        assert len(found) == 1
        chapter = found[0]
        paragraphs_greek = [' '.join(greek_main(p).split()) for p in chapter.findall('.//t:p', NS)]
        apparatus = [' '.join(''.join(n.itertext()).split()) for n in chapter.findall('.//t:note', NS)]
        chapters[number] = dict(paragraphs=paragraphs_greek, apparatus=apparatus,
                                original_xml=ET.tostring(chapter, encoding='unicode'),
                                editorial_additions=[''.join(n.itertext()) for n in chapter.findall('.//t:add', NS)])
    assert len(chapters['190']['paragraphs']) == len(chapters['191']['paragraphs']) == 2
    assert 'ἔμβρυα λεῖα προστεθέντα' in chapters['190']['paragraphs'][1]
    dioscorides = dict(
        source=receipt(dpath, 'https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0656/tlg001/tlg0656.tlg001.1st1K-grc1.xml',
                       'Dioscorides, De materia medica IV.190–191, Max Wellmann edition; Harvard College Library / First1KGreek TEI',
                       'TEI header: CC BY-SA4.0. Greek excerpts, XML and their adapted extraction in this packet retain CC BY-SA4.0 attribution.'),
        unit='Exact chapter nodes IV.190 and IV.191; not their incorrectly nested ancestor chapters',
        chapters=chapters,
        extraction='Main text excludes note elements but preserves their tails, page-break continuations and supplied add text. Complete original XML and apparatus remain separate.')

    ipath = BASE / 'AE_SOURCE_ISIDORE17.html'
    latin_html = ipath.read_text()
    unit = latin_html.split('<A CLASS="sec" NAME="9.37">37</A>', 1)[1]
    unit = unit.split('<A CLASS="sec" NAME="9.38">38</A>', 1)[0]
    latin = clean_html(unit)
    assert latin.startswith('Heliotropium nomen') and latin.endswith('abstergat.')
    isidore = dict(
        source=receipt(ipath, 'https://penelope.uchicago.edu/Thayer/L/Roman/Texts/Isidore/17%2A.html#9.37',
                       'Isidore, Etymologiae XVII.9.37; W. M. Lindsay1911 edition, LacusCurtius transcription by Bill Thayer',
                       'Latin source is identified as public domain by the host; only historical text is extracted.'),
        unit='Complete entry XVII.9.37, not a complete chapter9 or book17 reading',
        latin=latin,
        editorial_poor_reading=[clean_html(t) for t in re.findall(r'<SPAN CLASS="poor_reading">(.*?)</SPAN>', unit, re.S)])
    return dict(kind='HISTORICAL_SOURCE_EXTRACTION_NO_VOYNICH_DATA', pliny=pliny,
                dioscorides=dioscorides, isidore=isidore)


if __name__ == '__main__':
    result = build()
    out = BASE / 'AE_COMPLETE_SOURCES.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status='EXTRACTED', file=out.name,
                          pliny_paragraphs=3, pliny_notes=17,
                          dioscorides_entries=2, isidore_entries=1,
                          no_semantic_test=True)))
