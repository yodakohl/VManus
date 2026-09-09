#!/usr/bin/env python3
"""Frozen source-only intake: no target-dependent windows or text repairs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

TEI = 'http://www.tei-c.org/ns/1.0'
NS = {'t': TEI}
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
ARTIFACTS = Path(__file__).resolve().parent.parent / 'artifacts'
COREMA_NAMES = ('w1', 'bs1', 'b6', 'gr1', 'b4', 'br1')
ALIM_IDS = {13001, 13000, 553, 427, 489, 279, 367, 213}
TRANSPARENT = {'ab', 'title', 'instruction', 'ingredient', 'alternative', 'kitchenTip',
               'tool', 'dish', 'closer', 'ref', 'time', 'servingTip', 'name', 'religion',
               'date', 'opener', 'dietetics', 'householdTip', 'foreign', 'sp'}
BAD = {'unclear', 'gap', 'supplied', 'choice'}
LACUNA = re.compile(r'\[[^\]]*(?:…|\.{3})[^\]]*\]')


def local(element):
    if not element.tag.startswith('{' + TEI + '}'):
        raise ValueError('Unexpected XML namespace')
    return element.tag.split('}', 1)[1]


def mixed_text(element):
    """Text/tails once, no spaces added at inline or page-break boundaries."""
    name = local(element)
    if name in {'note', 'pb'}:
        return ''
    if name in BAD:
        raise ValueError('Uncertain text cannot be rendered as complete')
    if name not in TRANSPARENT:
        raise ValueError('Unknown source tag: ' + name)
    return (element.text or '') + ''.join(mixed_text(c) + (c.tail or '') for c in element)


def tokenize(raw):
    """Offsets refer to ORIGINAL raw Python Unicode codepoints, end exclusive."""
    spans = []
    start = None
    for i, character in enumerate(raw):
        lexical = unicodedata.category(character)[0] in 'LMN'
        if lexical and start is None:
            start = i
        elif not lexical and start is not None:
            spans.append([start, i])
            start = None
    if start is not None:
        spans.append([start, len(raw)])
    words = [unicodedata.normalize('NFC', raw[a:b]).lower() for a, b in spans]
    return words, spans


def gap_intervals(raw):
    """Any square-bracket span is a barrier, also nested/unmatched brackets."""
    intervals = []
    start, depth = None, 0
    for i, c in enumerate(raw):
        if c == '[':
            if depth == 0:
                start = i
            depth += 1
        elif c == ']':
            if depth:
                depth -= 1
                if depth == 0:
                    intervals.append((start, i + 1))
            else:
                intervals.append((i, i + 1))
    if depth:
        intervals.append((start, len(raw)))
    intervals.extend((m.start(), m.end()) for m in re.finditer(r'\.{3,}|…+', raw))
    merged = []
    for a, b in sorted(intervals):
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def split_segments(raw):
    last = 0
    for a, b in gap_intervals(raw):
        if a > last:
            yield last, a, raw[last:a]
        last = b
    if last < len(raw):
        yield last, len(raw), raw[last:]


def verified(path, expected):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Source hash mismatch: ' + path.name)
    return data


def unit(uid, source, raw, digest, **extra):
    words, spans = tokenize(raw)
    return dict(id=uid, source=source, words=words, raw=raw, token_spans=spans,
                source_sha256=digest, **extra)


def top_recipes(root):
    body = root.find('t:text/t:body', NS)
    if body is None:
        raise ValueError('Missing TEI body')
    parent = {c: p for p in body.iter() for c in p}
    for recipe in body.findall('.//t:ab[@type="recipe"]', NS):
        ancestor = parent.get(recipe)
        nested = False
        while ancestor is not None:
            if local(ancestor) == 'ab' and ancestor.get('type') == 'recipe':
                nested = True
                break
            ancestor = parent.get(ancestor)
        if not nested:
            yield recipe


def build(cache_dir, corema_dir):
    alim = json.loads((ARTIFACTS / 'ALIM_SOURCES.json').read_text())
    intake = json.loads((ARTIFACTS / 'COREMA_INTAKE.json').read_text())
    if {s['id'] for s in alim} != ALIM_IDS or len(alim) != 8:
        raise ValueError('Unexpected ALIM pool')
    metadata = {s['source']: s for s in intake['sources']}
    if set(metadata) != set(COREMA_NAMES):
        raise ValueError('Unexpected COREMA pool')
    units, sources, exclusions = [], [], []
    for s in alim:
        source = 'ALIM:' + str(s['id'])
        f = next(f for f in s['files'] if f['name'] == 'alim%d.txt' % s['id'])
        raw = verified(cache_dir / f['name'], f['sha256']).decode('utf8')
        sources.append(dict(source=source, metadata=s, sha256=f['sha256'],
                            dependence='ALIM:13000 and ALIM:13001 are witnesses of the same work; no independence claim.'))
        for a, b in gap_intervals(raw):
            exclusions.append(dict(source=source, source_char_span=[a, b], reason='bracket_or_ellipsis_barrier'))
        for n, (a, b, segment) in enumerate(split_segments(raw), 1):
            u = unit(source + ':segment:%04d' % n, source, segment, f['sha256'], source_char_span=[a, b])
            if u['words']:
                units.append(u)
            else:
                exclusions.append(dict(source=source, source_char_span=[a, b], reason='no_LMN_tokens'))
    for name in COREMA_NAMES:
        s = metadata[name]
        source = 'COREMA:' + name
        root = ET.fromstring(verified(corema_dir / (name + '.recipes.xml'), s['sha256']))
        fixed_flags = {f['id']: f['reasons'] for f in s['flagged_top_level_units']}
        sources.append(dict(source=source, metadata=s, sha256=s['sha256'],
                            dependence='Related recipe witnesses, especially w1/b4; not independent evidence.'))
        for recipe in top_recipes(root):
            rid = recipe.get(XML_ID)
            if not rid:
                raise ValueError('Recipe lacks stable ID')
            reasons = list(fixed_flags.get(rid, []))
            reasons += sorted({local(e) for e in recipe.iter()} & BAD)
            if reasons:
                exclusions.append(dict(source=source, id=rid, reasons=sorted(set(reasons))))
                continue
            raw = mixed_text(recipe)
            if LACUNA.search(raw):
                exclusions.append(dict(source=source, id=rid, reasons=['literal_bracket_lacuna']))
                continue
            u = unit(source + ':' + rid, source, raw, s['sha256'], recipe_id=rid)
            if not u['words']:
                exclusions.append(dict(source=source, id=rid, reasons=['no_LMN_tokens']))
                continue
            units.append(u)
    return dict(schema='GDT893_SOURCE_UNITS_V1', units=units, sources=sources, exclusions=exclusions,
                normalization='NFC then lower; maximal original Unicode L/M/N runs; raw codepoint spans end-exclusive',
                boundaries='No source-unit bridging, gap bridging, target-length cuts or editorial corrections')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache-dir', type=Path, required=True)
    p.add_argument('--corema-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = build(args.cache_dir, args.corema_dir)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf8')
    print(json.dumps({'status': 'PASS', 'sources': len(result['sources']), 'units': len(result['units']),
                      'tokens': sum(len(u['words']) for u in result['units']), 'exclusions': len(result['exclusions'])}))


if __name__ == '__main__':
    main()
