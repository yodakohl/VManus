#!/usr/bin/env python3
"""Fixed source-only capacity census; no fitted contextual model."""
import collections as C
import functools
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E
import build

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name, obj):
    raw = (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      indent=None if name.endswith('.gz') else 2) + '\n').encode()
    (HERE / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)


def read(name):
    data = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def source_groups():
    package = read('SUMMARY.json')
    for pin in package['source_pins']:
        assert sha(build.SRC / pin['path']) == pin['sha256']
    rules = read('DECLARATION_RULES.json')
    frozen = {r['id']: r for r in read('GROUPS.json.gz')}
    books = {}
    for book in build.BOOKS:
        body = E.parse(build.SRC / ('sources/' + book + '.xml')).find('t:text/t:body', build.NS)
        p = build.Project(book, body, rules['refs'])
        p.visit(body)
        p.boundary()
        nodes = list(body.iter())
        ordinal = {id(n): i + 1 for i, n in enumerate(nodes)}
        owners = {}

        def visit(n, owner=None, parent=''):
            name = build.tag(n)
            if name == 'ab' or name == 'seg' and parent == 'ab':
                owner = ordinal[id(n)]
            owners[ordinal[id(n)]] = owner
            for c in n:
                visit(c, owner, name)

        visit(body)
        for w in p.groups:
            if w['selected']:
                assert all(w[k] == v for k, v in frozen[w['id']].items() if k != 'status')
                w['status'] = frozen[w['id']]['status']
            w['record'] = owners[w['locator']['element']]
        assert len(p.groups) == package['books'][book]['all_groups']
        books[book] = p.groups
    assert sum(w['selected'] for rows in books.values() for w in rows) == len(frozen)
    return books, rules


def native(w):
    return None if None in w['native'] else ''.join(w['native'])


def known_gold(w):
    return '\uFFFC' not in w['expanded']


def adjacent(groups):
    return [(a, b) for a, b in zip(groups, groups[1:])
            if a['record'] is not None and a['record'] == b['record']]


class Lexicon:
    def __init__(self, counts, classes):
        self.counts, self.classes = counts, classes
        self.trie = [{}]
        self.ends = {}
        for word in sorted(counts):
            node = 0
            for ch in word:
                nxt = self.trie[node].get(ch)
                if nxt is None:
                    nxt = len(self.trie)
                    self.trie[node][ch] = nxt
                    self.trie.append({})
                node = nxt
            self.ends[node] = word

    @functools.lru_cache(None)
    def candidates(self, written):
        if written is None:
            return ()
        states = {0}
        for ch in written:
            later = set()
            for node in states:
                for alt in self.classes.get(ch, {'alternatives': [ch]})['alternatives']:
                    current = node
                    for char in alt:
                        current = self.trie[current].get(char)
                        if current is None:
                            break
                    if current is not None:
                        later.add(current)
            states = later
            if not states:
                break
        words = [self.ends[n] for n in states if n in self.ends]
        return tuple(sorted(words, key=lambda s: (-self.counts[s], s)))


BOOLS = ('rule_covered', 'reference_covered', 'intersection_covered',
         'frequency_correct', 'gold_in_frequency_tie', 'ambiguous',
         'gold_covered_ambiguous', 'support_differs', 'gold_sole_supported',
         'wrong_sole_supported', 'support_repairs_frequency_error')


def summarize(rows):
    result = {}
    for book in (*build.BOOKS, 'ALL'):
        result[book] = {}
        for group in ('ALL', 'NOVEL', 'SHARED', 'UNKNOWN_WRITTEN'):
            selected = [r for r in rows if (book == 'ALL' or r['book'] == book)
                        and (group == 'ALL' or r['partition'] == group)]
            types = C.defaultdict(list)
            for r in selected:
                if r['native'] is not None:
                    types[(r['book'], r['native'])].append(r)
            d = dict(occurrences=len(selected), book_written_types=len(types),
                     unresolved=sum(r['status'] == 'UNRESOLVED' for r in selected),
                     empty_domains=sum(r['domain_size'] == 0 for r in selected),
                     singleton_domains=sum(r['domain_size'] == 1 for r in selected))
            d.update({k: sum(r[k] for r in selected) for k in BOOLS})
            d['oracle_headroom_occurrences'] = d['intersection_covered'] - d['frequency_correct']
            d['type_macro'] = {k: (sum(sum(r[k] for r in rr) / len(rr) for rr in types.values())
                                  / len(types) if types else None)
                               for k in ('rule_covered', 'reference_covered', 'intersection_covered',
                                         'frequency_correct')}
            result[book][group] = d
    return result


def main():
    books, rules = source_groups()
    rows, reference, domains = [], {}, {}
    for book, target in books.items():
        other = [groups for b, groups in books.items() if b != book]
        written = {native(w) for groups in other for w in groups if native(w) is not None}
        counts = C.Counter(w['expanded'] for groups in other for w in groups if known_gold(w))
        bigrams = C.Counter((a['expanded'], b['expanded']) for groups in other
                            for a, b in adjacent(groups) if known_gold(a) and known_gold(b))
        lex = Lexicon(counts, rules['classes'])
        left, right = {}, {}
        for a, b in adjacent(target):
            left[b['id']] = a
            right[a['id']] = b
        reference[book] = dict(counts=dict(counts), written=sorted(written),
                               bigrams=[[a, b, n] for (a, b), n in sorted(bigrams.items())])
        domains[book] = {}
        for w in target:
            if not w['selected']:
                continue
            text = native(w)
            candidates = lex.candidates(text)
            if text is not None:
                domains[book][text] = list(candidates)
            near, support = {}, {}
            for direction, index in (('left', left), ('right', right)):
                n = index.get(w['id'])
                nc = lex.candidates(native(n)) if n else ()
                near[direction] = (dict(id=n['id'], native=native(n), locator=n['locator'],
                                        candidates=list(nc)) if n else None)
                for c in candidates:
                    hits = [(a, bigrams[(a, c) if direction == 'left' else (c, a)])
                            for a in nc if bigrams[(a, c) if direction == 'left' else (c, a)]]
                    support.setdefault(c, {})[direction] = hits
            supported = [c for c, sides in support.items() if any(sides.values())]
            gold = w['expanded'] if known_gold(w) else None
            intersection = gold is not None and gold in candidates
            best = candidates[0] if candidates else None
            tie = [c for c in candidates if counts[c] == counts[best]] if candidates else []
            sole = supported[0] if len(supported) == 1 else None
            row = dict(id=w['id'], book=book, locator=w['locator'], record=w['record'],
                       native=text, native_units=w['native'], gold=gold, flags=w['flags'],
                       status=w['status'],
                       partition=('UNKNOWN_WRITTEN' if text is None else
                                  'SHARED' if text in written else 'NOVEL'),
                       domain_size=len(candidates), frequency_choice=best, frequency_ties=tie,
                       neighbours=near, candidate_support=support,
                       rule_covered=w['status'] == 'LOCAL_COMPATIBLE',
                       reference_covered=gold is not None and gold in counts,
                       intersection_covered=intersection,
                       frequency_correct=gold is not None and gold == best,
                       gold_in_frequency_tie=gold is not None and gold in tie,
                       ambiguous=len(candidates) > 1,
                       gold_covered_ambiguous=intersection and len(candidates) > 1,
                       support_differs=bool(supported) and len(supported) < len(candidates),
                       gold_sole_supported=gold is not None and sole == gold and len(candidates) > 1,
                       wrong_sole_supported=sole is not None and sole != gold and len(candidates) > 1,
                       support_repairs_frequency_error=(gold is not None and sole == gold
                                                       and best != gold and len(candidates) > 1))
            assert intersection == (row['rule_covered'] and row['reference_covered'])
            rows.append(row)
        print(book, len([r for r in rows if r['book'] == book]), 'groups', flush=True)
    dump('FEASIBILITY_REFERENCES.json.gz', reference)
    dump('FEASIBILITY_DOMAINS.json.gz', domains)
    dump('FEASIBILITY_ROWS.json.gz', rows)
    result = dict(scope='exposed source capacity; known sign values; no contextual fit',
                  summaries=summarize(rows),
                  inputs={name: sha(HERE / name) for name in ('FEASIBILITY_PROTOCOL.md',
                          'feasibility.py', 'build.py', 'SUMMARY.json', 'DECLARATION_RULES.json',
                          'GROUPS.json.gz')},
                  artifacts={name: sha(HERE / name) for name in ('FEASIBILITY_REFERENCES.json.gz',
                             'FEASIBILITY_DOMAINS.json.gz', 'FEASIBILITY_ROWS.json.gz')})
    dump('FEASIBILITY_RESULT.json', result)
    print(json.dumps(result['summaries']['ALL'], indent=2))


if __name__ == '__main__':
    main()
