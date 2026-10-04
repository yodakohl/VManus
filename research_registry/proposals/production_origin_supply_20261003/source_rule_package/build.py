#!/usr/bin/env python3
"""Source-only finite declaration relation; no fitted or target rules."""
import collections as C
import gzip
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as E

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())
SRC = ROOT / 'experiments/yolo/gdt1166_natural_shared_sign_candidate_control'
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
XID = '{http://www.w3.org/XML/1998/namespace}id'
SKIP = {'note', 'anchor', 'ptr', 'listTranspose', 'transpose', 'del'}
UNKNOWN = {'unclear', 'supplied', 'expan', 'gap', 'metamark', 'choice'}
BOOKS = ('b4', 'b6', 'br1', 'bs1', 'gr1', 'w1')


def tag(x):
    return x.tag.rsplit('}', 1)[-1]


def dump(name, obj, compressed=False):
    data = (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       indent=None if compressed else 2) + '\n').encode()
    if compressed:
        data = gzip.compress(data, mtime=0)
    (HERE / name).write_bytes(data)


def declarations(tree):
    refs, classes = {}, {}
    for x in tree.iter():
        if tag(x) not in {'glyph', 'char'} or XID not in x.attrib:
            continue
        maps = [(m.attrib, ''.join(m.itertext()).strip()) for m in x
                if tag(m) == 'mapping']
        cp = [v for a, v in maps if a.get('type') == 'unicode_codepoint'
              and a.get('subtype') != 'unicode_symbol']
        sy = [v for a, v in maps if a.get('subtype') == 'unicode_symbol'
              or a.get('type') == 'unicode_symbol']
        no = [v for a, v in maps if a.get('type') == 'normalized']
        char = None
        if len(cp) == 1 and re.fullmatch('[0-9a-fA-F]{4,6}', cp[0]):
            number = int(cp[0], 16)
            if number <= 0x10FFFF and not 0xD800 <= number <= 0xDFFF:
                char = chr(number)
                if any(v != char for v in sy):
                    char = None
        ref = '#' + x.get(XID)
        refs[ref] = dict(ref=ref, char=char, normalized=no[0] if len(no) == 1 else None,
                         category=x.get('ana'), abbreviation=(x.get('n') == 'abbr' or
                         x.get('ana') in {'brevigraph', 'abbreviation_mark', 'contraction'}),
                         codepoints=cp, symbols=sy,
                         name=x.findtext('t:glyphName', namespaces=NS))
        if char is not None:
            d = classes.setdefault(char, dict(codepoint='U+%04X' % ord(char),
                                             refs=[], alternatives=[]))
            d['refs'].append(ref)
            if len(no) == 1:
                d['alternatives'].append(no[0])
    for ch, d in classes.items():
        if ord(ch) < 128:
            d['alternatives'].append(ch)
        d['alternatives'] = sorted(set(d['alternatives']))
    return refs, classes


def accepts(chars, gold, classes):
    offsets = {0}
    for ch in chars:
        alternatives = classes.get(ch, {'alternatives': [ch]})['alternatives']
        offsets = {i + len(a) for i in offsets for a in alternatives if gold.startswith(a, i)}
        if not offsets:
            return False
    return len(gold) in offsets


def surviving_content(node):
    if tag(node) in SKIP:
        return False
    return (tag(node) in UNKNOWN | {'g'} or bool((node.text or '').strip())
            or any(surviving_content(c) or bool((c.tail or '').strip()) for c in node))


class Project:
    def __init__(self, book, body, refs):
        self.book, self.refs = book, refs
        self.meta, self.end_meta, self.abbr_ids, self.raw = {}, {}, {}, []
        page = line = ''
        for ordinal, x in enumerate(body.iter(), 1):
            if tag(x) == 'pb':
                page, line = x.get('n') or x.get(XID) or '', ''
            if tag(x) == 'lb':
                line = x.get('n') or x.get(XID) or ''
            self.meta[id(x)] = dict(element=ordinal, page=page, line=line)
            if tag(x) == 'abbr':
                aid = '%s:A%05d' % (book, len(self.raw) + 1)
                self.abbr_ids[id(x)] = aid
                self.raw.append(dict(id=aid, **self.meta[id(x)]))
        for x in reversed(list(body.iter())):
            self.end_meta[id(x)] = self.end_meta[id(x[-1])] if len(x) else self.meta[id(x)]
        self.current = self.meta[id(body)]
        self.groups, self.skipped = [], []
        self.reset()

    def reset(self):
        self.native, self.gold, self.events = [], [], []
        self.flags, self.aids = set(), set()
        self.selected = False
        self.location = None

    def start(self, node, active):
        if self.location is None:
            self.location = dict(self.current)
        self.aids.update(active)
        self.selected |= bool(active)

    def boundary(self):
        if self.native or self.gold:
            self.groups.append(dict(id='%s:T%06d' % (self.book, len(self.groups) + 1),
                                    source=self.book, locator=self.location,
                                    native=self.native, expanded=''.join(self.gold),
                                    flags=sorted(self.flags), abbr_ids=sorted(self.aids),
                                    selected=self.selected, glyphs=self.events))
        self.reset()

    def text(self, s, node, joined, active, mark=False):
        for ch in s or '':
            if ch.isspace():
                if not joined:
                    self.boundary()
            else:
                self.start(node, active)
                self.native.append(ch)
                if not mark:
                    self.gold.append(ch)

    def unknown(self, node, active, reason):
        self.start(node, active)
        self.native.append(None)
        self.gold.append('\uFFFC')
        self.flags.add(reason)
        for x in node.iter():
            if id(x) in self.abbr_ids:
                self.aids.add(self.abbr_ids[id(x)])
                self.selected = True

    def visit(self, node, joined=False, active=(), mark=False, parent=''):
        self.current = self.meta[id(node)]
        name = tag(node)
        if name in SKIP:
            if name == 'del' and (self.native or self.gold):
                self.flags.add('final_state_deletion')
            for x in node.iter():
                if id(x) in self.abbr_ids:
                    self.skipped.append(dict(id=self.abbr_ids[id(x)], reason=name))
            return
        if name in UNKNOWN:
            self.unknown(node, active, name)
            return
        if name == 'handShift':
            return
        if name in {'lb', 'pb', 'cb'}:
            if not joined:
                self.boundary()
            return
        if name == 'ex':
            self.start(node, active)
            self.selected = True
            text = ''.join(node.itertext())
            if any(c.isspace() for c in text):
                self.flags.add('reference_whitespace')
            self.gold.append(text)
            return
        if name == 'abbr':
            active = active + (self.abbr_ids[id(node)],)
        if name == 'g':
            self.start(node, active)
            d = self.refs.get(node.get('ref'))
            self.selected |= bool(d and d['abbreviation']) or mark
            char = d['char'] if d else None
            self.events.append(dict(ref=node.get('ref'), char=char, index=len(self.native),
                                    in_am=mark, **self.meta[id(node)]))
            if char is None:
                self.unknown(node, active, 'unknown_graphic')
            else:
                self.native.append(char)
                if not mark:
                    norm = d['normalized']
                    if norm is None:
                        self.flags.add('unknown_expansion')
                        self.gold.append('\uFFFC')
                    else:
                        self.gold.append(norm)
            return
        if name in {'add', 'mod'}:
            self.flags.add('editorial_order_' + name)
        record = name == 'ab' or name == 'seg' and parent == 'ab'
        if record:
            self.boundary()
        joined = joined or name == 'w'
        mark = mark or name == 'am'
        if name == 'am':
            self.selected = True
        self.text(node.text, node, joined, active, mark)
        for child in node:
            self.visit(child, joined, active, mark, name)
            self.current = self.end_meta[id(child)]
            self.text(child.tail, node, joined, active, mark)
        if record:
            self.boundary()


def main():
    pins = json.loads((SRC / 'src/SOURCE.json').read_text())['source_pins']
    for pin in pins:
        data = (SRC / pin['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == pin['sha256']
        assert len(data) == pin['bytes']
    refs, classes = declarations(E.parse(SRC / 'sources/chardec.xml').getroot())
    dump('DECLARATION_RULES.json', dict(refs=refs, classes=classes))
    rows, conservation, summary, optional = [], {}, {}, []
    for book in BOOKS:
        body = E.parse(SRC / ('sources/' + book + '.xml')).find('t:text/t:body', NS)
        p = Project(book, body, refs)
        p.visit(body)
        p.boundary()
        seen = {a for w in p.groups for a in w['abbr_ids']}
        skipped = {a['id'] for a in p.skipped}
        for x in body.iter():
            aid = p.abbr_ids.get(id(x))
            if aid and aid not in seen | skipped:
                assert not surviving_content(x), aid
                p.skipped.append(dict(id=aid, reason='empty_final_state_container'))
                skipped.add(aid)
        assert not seen & skipped
        assert seen | skipped == {a['id'] for a in p.raw}
        conservation[book] = dict(raw_abbreviations=p.raw, excluded=p.skipped,
                                  represented=len(seen), all_groups=len(p.groups))
        counts = C.Counter(all_groups=len(p.groups), raw_abbreviations=len(p.raw),
                           excluded_abbreviations=len(skipped))
        plain, shortened = {}, {}
        for w in p.groups:
            known = None not in w['native'] and '\uFFFC' not in w['expanded']
            if w['selected']:
                w['status'] = ('UNRESOLVED' if not known else 'LOCAL_COMPATIBLE'
                               if accepts(w['native'], w['expanded'], classes)
                               else 'LOCAL_INCOMPATIBLE')
                counts[w['status']] += 1
                rows.append(w)
            if known:
                if w['abbr_ids'] and len(w['expanded']) > len(w['native']):
                    shortened.setdefault(w['expanded'], w)
                elif not w['selected']:
                    plain.setdefault(w['expanded'], w)
        for word in sorted(plain.keys() & shortened.keys()):
            optional.append(dict(source=book, expansion=word,
                                 abbreviated=shortened[word], unabbreviated=plain[word]))
        counts['optional_expansion_types'] = len(plain.keys() & shortened.keys())
        summary[book] = dict(counts)
    dump('GROUPS.json.gz', rows, True)
    dump('CONSERVATION.json.gz', conservation, True)
    dump('OPTIONAL_PAIRS.json.gz', optional, True)
    dump('COUNTEREXAMPLES.json', [r for r in rows if r['status'] == 'LOCAL_INCOMPATIBLE'])
    counts = C.Counter()
    for d in summary.values():
        counts.update(d)
    dump('SUMMARY.json', dict(scope='source-only supplied declaration relation; no fitted key',
                              books=summary, totals=dict(counts),
                              declaration_classes=len(classes),
                              used_classes=len({g['char'] for r in rows for g in r['glyphs']
                                                if g['char'] is not None}),
                              source_pins=pins))
    print(json.dumps(dict(books=summary, totals=dict(counts)), indent=2))


if __name__ == '__main__':
    main()
