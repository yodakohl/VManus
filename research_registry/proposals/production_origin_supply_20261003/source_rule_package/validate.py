#!/usr/bin/env python3
"""Independent relation/receipt validation; does not import the builder."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())
SOURCE = ROOT / 'experiments/yolo/gdt1166_natural_shared_sign_candidate_control'
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'


def read(name):
    data = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def main():
    summary, declarations = read('SUMMARY.json'), read('DECLARATION_RULES.json')
    groups, conservation = read('GROUPS.json.gz'), read('CONSERVATION.json.gz')
    pairs, failures = read('OPTIONAL_PAIRS.json.gz'), read('COUNTEREXAMPLES.json')
    for pin in summary['source_pins']:
        b = (SOURCE / pin['path']).read_bytes()
        assert len(b) == pin['bytes'] and hashlib.sha256(b).hexdigest() == pin['sha256']
    # Independently reconstruct all declaration-domain alternatives.
    from_xml = collections.defaultdict(set)
    for node in ET.parse(SOURCE / 'sources/chardec.xml').iter():
        if node.tag.rsplit('}', 1)[-1] not in {'glyph', 'char'}:
            continue
        cp, sy, no = [], [], []
        for m in node.findall('t:mapping', NS):
            value = ''.join(m.itertext()).strip()
            if m.get('type') == 'unicode_codepoint' and m.get('subtype') != 'unicode_symbol':
                cp.append(value)
            if m.get('type') == 'unicode_symbol' or m.get('subtype') == 'unicode_symbol':
                sy.append(value)
            if m.get('type') == 'normalized':
                no.append(value)
        char = None
        if len(cp) == 1 and re.fullmatch('[0-9a-fA-F]{4,6}', cp[0]):
            v = int(cp[0], 16)
            if v <= 0x10FFFF and not 0xD800 <= v <= 0xDFFF:
                char = chr(v)
                if sy and set(sy) != {char}:
                    char = None
        if char is not None:
            from_xml[char].update(no if len(no) == 1 else [])
            if ord(char) < 128:
                from_xml[char].add(char)
    assert {c: sorted(v) for c, v in from_xml.items()} == {
        c: d['alternatives'] for c, d in declarations['classes'].items()}
    counts = collections.defaultdict(collections.Counter)
    represented = collections.defaultdict(set)
    verified_failures, ambiguous = [], 0
    for g in groups:
        assert g['selected'] and g['native']
        represented[g['source']].update(g['abbr_ids'])
        known = None not in g['native'] and '\uFFFC' not in g['expanded']
        if not known:
            status = 'UNRESOLVED'
        else:
            alternatives = [from_xml[c] if c in from_xml else {c} for c in g['native']]
            pattern = ''.join('(?:' + '|'.join(re.escape(v) for v in sorted(a)) + ')'
                              for a in alternatives)
            ok = re.fullmatch(pattern, g['expanded']) is not None
            status = 'LOCAL_COMPATIBLE' if ok else 'LOCAL_INCOMPATIBLE'
            ambiguous += ok and any(len(a) > 1 for a in alternatives)
            if not ok:
                verified_failures.append(g)
        assert status == g['status'], g['id']
        counts[g['source']][status] += 1
        # Check every reported glyph against the original body element ordinal.
    assert verified_failures == failures
    for book, record in conservation.items():
        body = ET.parse(SOURCE / ('sources/' + book + '.xml')).find('t:text/t:body', NS)
        nodes = list(body.iter())
        abbreviations = [x for x in nodes if x.tag.endswith('}abbr')]
        assert len(abbreviations) == len(record['raw_abbreviations'])
        raw_ids = {'%s:A%05d' % (book, i + 1) for i in range(len(abbreviations))}
        excluded = {x['id'] for x in record['excluded']}
        assert not represented[book] & excluded
        assert represented[book] | excluded == raw_ids
        assert record['represented'] == len(represented[book])
        for g in [x for x in groups if x['source'] == book]:
            for event in g['glyphs']:
                node = nodes[event['element'] - 1]
                assert node.tag.endswith('}g') and node.get('ref') == event['ref']
                assert g['native'][event['index']] == event['char']
            for aid in g['abbr_ids']:
                node = abbreviations[int(aid.rsplit('A', 1)[1]) - 1]
                assert node.tag.endswith('}abbr')
        for status in ('LOCAL_COMPATIBLE', 'LOCAL_INCOMPATIBLE', 'UNRESOLVED'):
            assert counts[book][status] == summary['books'][book].get(status, 0)
    for pair in pairs:
        a, b = pair['abbreviated'], pair['unabbreviated']
        assert a['source'] == b['source'] == pair['source']
        assert a['expanded'] == b['expanded'] == pair['expansion']
        assert a['abbr_ids'] and not b['selected']
        assert len(a['native']) < len(a['expanded']) and a['native'] != b['native']
        assert None not in a['native'] + b['native']
    assert len(pairs) == summary['totals']['optional_expansion_types']
    files = ('PROTOCOL.md', 'build.py', 'DECLARATION_RULES.json', 'GROUPS.json.gz',
             'CONSERVATION.json.gz', 'OPTIONAL_PAIRS.json.gz', 'COUNTEREXAMPLES.json',
             'SUMMARY.json', 'validate.py')
    receipt = dict(status='PASS', source_pins=8, independently_checked_groups=len(groups),
                   compatible_but_multiple_unrestricted_outputs=ambiguous,
                   optional_pairs=len(pairs), mismatch_groups=len(failures),
                   limits=['No independent full XML projection replay',
                           'Supplied source values; not unknown-key recovery',
                           'No native image collation, statistical or Voynich claim'],
                   bindings={name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                             for name in files})
    (HERE / 'VALIDATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
