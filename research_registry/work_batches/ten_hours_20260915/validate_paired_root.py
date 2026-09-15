#!/usr/bin/env python3
"""Check fixed cohort, published source extraction and optional original caches.
No automated validation of botanical judgments or proposed meanings is claimed.
Run from repository root. With --fetch, download only these named public sources.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
EXPECTED = 'f2r f4r f6v f9v f10r f11r f13r f17r f18r f20v f21r f24v f31r f32v f55v f56r'.split()
EXTRACT_SHA = '064bd2b5ba162ad4016d60d6c64fddbb101c464a776c771608b1abd9b2660f40'
XML_URL = 'https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0656/tlg001/tlg0656.tlg001.1st1K-grc1.xml'
args = argparse.ArgumentParser()
args.add_argument('--fetch', action='store_true')
args = args.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def obtain(path, url):
    if not path.exists() and args.fetch:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    return path.read_bytes() if path.exists() else None

rows = list(csv.DictReader((BASE / 'PAIRED_ROOT_NATIVE_MATRIX.tsv').open(), delimiter='\t'))
images = json.loads((BASE / 'PAIRED_ROOT_IMAGE_SOURCES.json').read_text())['images']
assert [r['page'] for r in rows] == EXPECTED == [r['page'] for r in images]
assert all(r['strict_xiphion_picture_conjunction'] in {'NO', 'UNCLEAR'} for r in rows)
assert sum(r['strict_orchis_picture_conjunction'] == 'PARTIAL_UNRESOLVED' for r in rows) == 1
checked = 0
for row in images:
    assert row['sha256'] == row['expected_sha256'] and row['root_viewed'] is True
    data = obtain(ROOT / row['cache'], row['url'])
    if data is not None:
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
        checked += 1
comparators = json.loads((BASE / 'PAIRED_ROOT_COMPARATOR_SOURCES.json').read_text())
assert [r['id'] for r in comparators] == ['morgan_121v', 'bnf_58r', 'bnf_58v']
assert all(r['status'] == 'UNAVAILABLE' for r in comparators[1:])
morgan = comparators[0]
data = obtain(ROOT / morgan['cache'], morgan['url'])
if data is not None:
    assert data[:2] == b'\xff\xd8' and sha(data) == morgan['sha256'] and len(data) == morgan['bytes']
assert morgan['root_viewed'] is True
extract_data = (BASE / 'PAIRED_ROOT_CONTENT_EXTRACT.xml').read_bytes()
assert sha(extract_data) == EXTRACT_SHA
extract = ET.fromstring(extract_data)
assert [(c.get('book'), c.get('number')) for c in extract.findall('chapter')] == [('3', '126'), ('3', '127'), ('3', '128'), ('4', '20')]
original = obtain(BASE / 'dioscorides_cache/Wellmann_DMM.xml', XML_URL)
source_replayed = False
if original is not None:
    assert sha(original) == extract.get('source_sha256')
    source = ET.fromstring(original)
    ns = {'t': 'http://www.tei-c.org/ns/1.0'}
    def plain(el):
        s = el.text or ''
        for child in el:
            if child.tag.rsplit('}', 1)[-1] not in {'note', 'head'}:
                s += plain(child)
            s += child.tail or ''
        return s
    for c in extract.findall('chapter'):
        book = source.find('.//t:div[@subtype="book"][@n="' + c.get('book') + '"]', ns)
        chapter = book.find('./t:div[@subtype="chapter"][@n="' + c.get('number') + '"]', ns)
        sections = chapter.findall('./t:div[@subtype="section"]', ns)
        if not sections:
            sections = [chapter]
        assert [s.get('n') if s is not chapter else '1' for s in sections] == [s.get('number') for s in c.findall('section')]
        for old, new in zip(sections, c.findall('section')):
            assert ' '.join(plain(old).split()) == ' '.join(new.itertext()).strip()
    source_replayed = True
print(json.dumps({'status': 'PASS', 'fixed_images': len(rows), 'cached_image_hashes_checked': checked,
                  'morgan_hash_checked': data is not None, 'original_source_replayed': source_replayed,
                  'meaning_validation': False, 'missing_cache_requires_fetch_for_full_replay': True}, indent=2))
