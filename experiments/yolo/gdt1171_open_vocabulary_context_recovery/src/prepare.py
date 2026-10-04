"""Expose the fixed per-fold inputs; never train or select predictions."""
import sys
from common import *


def main():
    assert not (EXP / 'artifacts/PREDICTION_LOCK.json').exists()
    sys.path.insert(0, str(PACKET))
    import feasibility
    books, rules = feasibility.source_groups()
    raw, answers, expanded = {}, {}, {}
    for book, groups in books.items():
        raw[book], answers[book], expanded[book] = [], [], []
        for w in groups:
            base = dict(id=w['id'], record=w['record'], locator=w['locator'], selected=w['selected'])
            text = None if None in w['native'] else ''.join(w['native'])
            gold = w['expanded'] if '\uFFFC' not in w['expanded'] else None
            raw[book].append(dict(base, native=text))
            expanded[book].append(dict(base, gold=gold))
            answers[book].append(dict(base, native=text, gold=gold, flags=w['flags']))
    save(EXP / 'artifacts/GOLD.json.gz', answers)
    for book in BOOKS:
        reference = []
        known_written = set()
        for other in BOOKS:
            if other == book:
                continue
            reference.extend([[w['gold'] for w in s] for s in segments(expanded[other], 'gold')])
            known_written.update(w['native'] for w in raw[other] if w['native'] is not None)
        save(EXP / f'artifacts/INPUT_{book}.json.gz', raw[book])
        save(EXP / f'artifacts/REFERENCE_{book}.json.gz', dict(segments=reference, raw_types=sorted(known_written)))
    save(EXP / 'artifacts/RULES.json', rules['classes'])
    names = ['GOLD.json.gz', 'RULES.json'] + [f'{kind}_{b}.json.gz' for b in BOOKS for kind in ('INPUT','REFERENCE')]
    save(EXP / 'artifacts/PREPARATION.json', dict(
        scope='source-only; target raw and other-book expanded inputs separated; prior exposure retained',
        groups={b:len(raw[b]) for b in BOOKS}, selected=sum(w['selected'] for g in raw.values() for w in g),
        source_pins=load(PACKET/'SUMMARY.json')['source_pins'],
        inputs={n:sha(EXP/'artifacts'/n) for n in names},
        projector_sha256=sha(PACKET/'build.py'), record_projector_sha256=sha(PACKET/'feasibility.py')))
    print('Prepared all six folds; no language model fitted.')


if __name__ == '__main__':
    main()
