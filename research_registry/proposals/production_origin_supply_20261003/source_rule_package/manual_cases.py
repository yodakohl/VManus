#!/usr/bin/env python3
"""Extract fixed manual source cases; no scorer, fit or Voynich input."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import build

HERE = Path(__file__).resolve().parent
FOCI = [
    ('A', 'b4:T006058', 'instrument/medium context'),
    ('B', 'b4:T007003', 'placement context'),
    ('C', 'b4:T001988', 'pounding location/direction ambiguity'),
    ('D', 'b4:T000557', 'literal spelling contrast, early witness'),
    ('E', 'b4:T008926', 'same literal form in broth context'),
    ('F', 'w1:T000064', 'preposition spelling contrast'),
    ('G', 'gr1:T003114', 'known outside-local-relation countercase'),
]


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--reveal', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for pin in json.loads((HERE / 'SUMMARY.json').read_text())['source_pins']:
        assert hashlib.sha256((build.SRC / pin['path']).read_bytes()).hexdigest() == pin['sha256']
    rules = json.loads((HERE / 'DECLARATION_RULES.json').read_text())
    source_rows = {w['id']: w for w in json.loads(gzip.decompress((HERE / 'GROUPS.json.gz').read_bytes()))}
    cases, answers = [], []
    for book in ('b4', 'w1', 'gr1'):
        body = ET.parse(build.SRC / ('sources/' + book + '.xml')).find('t:text/t:body', build.NS)
        nodes = list(body.iter())
        parents = {id(c): n for n in nodes for c in n}
        projection = build.Project(book, body, rules['refs'])
        projection.visit(body)
        projection.boundary()
        by_id = {w['id']: w for w in projection.groups}
        for label, word_id, purpose in FOCI:
            if not word_id.startswith(book + ':'):
                continue
            focus = by_id[word_id]
            assert focus['native'] == source_rows[word_id]['native']
            node = nodes[focus['locator']['element'] - 1]
            while not (build.tag(node) == 'seg' and build.tag(parents.get(id(node), body)) == 'ab'):
                node = parents[id(node)]
                assert node is not body, 'Focus lacks a bounded whole recipe record'
            descendants = {id(x) for x in node.iter()}
            ordinals = {i + 1 for i, x in enumerate(nodes) if id(x) in descendants}
            record = [w for w in projection.groups if w['locator']['element'] in ordinals]
            assert word_id in {w['id'] for w in record}
            candidates = [''.join(t) for t in itertools.product(*[
                rules['classes'].get(c, {'alternatives': [c]})['alternatives']
                for c in focus['native']])]
            cases.append(dict(case=label, id=word_id, purpose=purpose,
                              record_element=projection.meta[id(node)]['element'],
                              focus_location=focus['locator'],
                              native=''.join(focus['native']),
                              candidates=sorted(set(candidates)),
                              record=[dict(id=w['id'], native=w['native'], locator=w['locator'])
                                      for w in record]))
            answers.append(dict(case=label, id=word_id, expansion=focus['expanded'],
                                source_abbr_ids=focus['abbr_ids'],
                                flags=focus['flags'],
                                legal=focus['expanded'] in candidates))
    cases.sort(key=lambda x: x['case'])
    answers.sort(key=lambda x: x['case'])
    if args.check:
        assert cases == json.loads((HERE / 'MANUAL_WRITTEN_CASES.json').read_text())
        result = json.loads((HERE / 'MANUAL_ANSWER_COMPARISON.json').read_text())
        judgments = json.loads((HERE / 'MANUAL_JUDGMENTS.json').read_text())
        assert answers == result['answers']
        assert result['judgment_sha256'] == hashlib.sha256(
            (HERE / 'MANUAL_JUDGMENTS.json').read_bytes()).hexdigest()
        for c, j, a in zip(cases, judgments['cases'], answers):
            assert c['case'] == j['case'] == a['case']
            assert j['first_choice'] is None or j['first_choice'] in c['candidates']
            assert set(j['retained_rivals']) <= set(c['candidates'])
            assert a['legal'] == (a['expansion'] in c['candidates'])
        assert len(cases) == len(judgments['cases']) == len(answers) == 7
        files = ['manual_cases.py', 'build.py', 'DECLARATION_RULES.json',
                 'MANUAL_PLAUSIBILITY.md', 'MANUAL_WRITTEN_CASES.json',
                 'MANUAL_JUDGMENTS.json', 'MANUAL_ANSWER_COMPARISON.json',
                 'MANUAL_PRIMARY_FRAGMENTS.json']
        receipt = dict(status='SOURCE_CASE_CONSISTENCY_PASS', cases=7,
                       scientific_scope='manual plausibility only; no blind performance estimate',
                       limits='same extractor replay; no independent XML projection or image collation',
                       sha256={f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in files})
        save('MANUAL_CHECKS.json', receipt)
        print(json.dumps(receipt, indent=2))
    elif args.reveal:
        judgment = HERE / 'MANUAL_JUDGMENTS.json'
        assert judgment.exists(), 'Write manual judgments before answer display'
        save('MANUAL_ANSWER_COMPARISON.json', dict(
            judgment_sha256=hashlib.sha256(judgment.read_bytes()).hexdigest(),
            answers=answers, not_a_blind_test=True))
        print(json.dumps(answers, ensure_ascii=False, indent=2))
    else:
        save('MANUAL_WRITTEN_CASES.json', cases)
        for c in cases:
            print('\nCASE', c['case'], c['id'], c['focus_location'])
            print('LEGAL', c['candidates'])
            print('WHOLE_RECORD', ' '.join(
                ('⟦' if w['id'] == c['id'] else '') +
                ''.join(ch if ch is not None else '⟪UNKNOWN⟫' for ch in w['native']) +
                ('⟧' if w['id'] == c['id'] else '') for w in c['record']))


if __name__ == '__main__':
    main()
