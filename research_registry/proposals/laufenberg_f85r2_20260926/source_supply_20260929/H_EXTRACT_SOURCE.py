#!/usr/bin/env python3
"""Reproduce only two source excerpts from the previously cached Wellmann XML."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = next(p for p in BASE.parents if (p / 'vmanus-work').exists())
SOURCE = ROOT / 'research_registry/work_batches/ten_hours_20260915/dioscorides_cache/Wellmann_DMM.xml'
EXPECTED = 'e2a2175c5ca1c1a2313c5816bc79c7fa1c9103766fcad193356d0c13ce6746bc'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
tree = ET.parse(SOURCE).getroot()
book = tree.find('.//t:div[@subtype="book"][@n="2"]', NS)
parents = {c: p for p in tree.iter() for c in p}

def plain_without_notes(element):
    return (element.text or '') + ''.join(
        ('' if c.tag.endswith('}note') else plain_without_notes(c)) + (c.tail or '')
        for c in element
    )

for chapter in ('162', '164'):
    entry = book.find(f'.//t:div[@subtype="chapter"][@n="{chapter}"]', NS)
    assert entry is not None
    units = [entry]
    policy = ('Complete XML chapter retained. Reading text excludes note elements and '
              'line/page-break tags, preserves note tails; whitespace collapsed. '
              'No modern taxon identification.')
    if chapter == '164':
        siblings = list(parents[entry])
        units = siblings[siblings.index(entry):]
        assert [u.get('n') for u in units] == ['164', '2', '3', '4']
        policy = ('The source XML nests chapter164 and following section2/3/4 under chapter112. '
                  'A naive chapter164 extraction ends after the first paragraph and is INCOMPLETE. '
                  'This excerpt includes chapter164 plus its three immediately following section siblings, '
                  'and stops before chapter165. Complete printed entry retained with editorial notes '
                  'separate; note tails preserved; whitespace collapsed.')
    paragraphs = [' '.join(plain_without_notes(p).split())
                  for u in units for p in u.findall('.//t:p', NS)]
    notes = [' '.join(''.join(n.itertext()).split())
             for u in units for n in u.findall('.//t:note', NS)]
    if chapter == '164':
        assert len(paragraphs) == 4
        assert 'σκίλλα' in paragraphs[-1] and paragraphs[-1].endswith('δένδρα.')
    else:
        assert len(paragraphs) == 2 and paragraphs[-1].endswith('τόποις.')
    obj = dict(chapter=f'II.{chapter}', source_xml_sha256=EXPECTED,
               main_text_paragraphs=paragraphs, editorial_notes_separate=notes,
               policy=policy)
    (BASE / f'H_DIOSCORIDES_II_{chapter}_COMPLETE.json').write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    (BASE / f'H_DIOSCORIDES_II_{chapter}_GREEK.txt').write_text('\n\n'.join(paragraphs) + '\n')
    raw = '\n'.join(ET.tostring(u, encoding='unicode') for u in units)
    if len(units) > 1:
        raw = '<extracted-entry book="2" chapter="164">\n' + raw + '\n</extracted-entry>\n'
    (BASE / f'H_DIOSCORIDES_II_{chapter}_XML.txt').write_text(raw)
print(json.dumps({'status': 'PASS_SOURCE_EXTRACTION', 'entries': ['II.162', 'II.164'],
                  'main_paragraph_counts': [2, 4], 'target_access': False,
                  'meaning_validation': False}))
