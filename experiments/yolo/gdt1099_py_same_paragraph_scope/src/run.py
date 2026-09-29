#!/usr/bin/env python3
"""Complete frozen p/y same-leaf census using owned boundary metadata only."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / 'artifacts'


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def write(path, rows, fields=None):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main():
    spec = json.loads((EXP / 'src/INPUTS.json').read_text())
    for item in spec['files']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    events, metadata = read(ROOT / spec['events']), read(ROOT / spec['metadata'])
    assert len(events) == 214
    assert {r['page'] for r in metadata} == set(spec['pages'])
    assert not any(r['page'].startswith('f84') for r in metadata)
    lines = defaultdict(list)
    for r in metadata:
        lines[(r['edition'], r['page'], r['locus'])].append(r)
    line_info = {}
    for key, rows in lines.items():
        n = int(rows[0]['source_group_count'])
        ok = sorted(int(r['source_group_index']) for r in rows) == list(range(1, n + 1))
        for name in ('kind', 'source_row_index', 'source_group_count', 'paragraph_start', 'paragraph_end'):
            ok &= len({r[name] for r in rows}) == 1
        line_info[key] = dict(rows[0], complete=int(ok))
    ordered = {}
    for ed in ('ZL3b', 'IT2a', 'RF1b'):
        for page in spec['pages']:
            ordered[ed, page] = sorted((v for (e, p, _), v in line_info.items() if (e, p) == (ed, page)),
                                       key=lambda r: int(r['source_row_index']))
    frames, exclusions, consensus = [], [], []
    membership, rank = {}, {}
    for page in spec['pages']:
        z, it = ordered['ZL3b', page], ordered['IT2a', page]
        if [r['locus'] for r in z] != [r['locus'] for r in it]:
            exclusions.append(dict(page=page, loci='|'.join(r['locus'] for r in z), reason='PAGE_ORDER_OR_LOCUS_DISAGREEMENT'))
            continue
        pending = []
        for index, (a, b) in enumerate(zip(z, it)):
            locus = a['locus']
            rank[locus] = index
            valid = a['complete'] and b['complete'] and all(a[k] == b[k] for k in ('kind', 'paragraph_start', 'paragraph_end'))
            valid = valid and a['paragraph_start'] in ('0', '1') and a['paragraph_end'] in ('0', '1')
            consensus.append(dict(page=page, locus=locus, index=index, kind=a['kind'] if valid else 'UNKNOWN',
                                  start=a['paragraph_start'] if valid else 'NA', end=a['paragraph_end'] if valid else 'NA'))
            if not valid or a['kind'] != 'P':
                if pending:
                    exclusions.append(dict(page=page, loci='|'.join(pending), reason='INTERRUPTED_OR_UNKNOWN_BOUNDARY'))
                pending = []
                exclusions.append(dict(page=page, loci=locus, reason='UNKNOWN_BOUNDARY' if not valid else 'NON_P'))
                continue
            if a['paragraph_start'] == '1':
                if pending:
                    exclusions.append(dict(page=page, loci='|'.join(pending), reason='NEW_START_BEFORE_END'))
                pending = [locus]
            elif pending:
                pending.append(locus)
            else:
                exclusions.append(dict(page=page, loci=locus, reason='NO_KNOWN_START'))
            if a['paragraph_end'] == '1' and pending:
                fid = pending[0] + '--' + pending[-1]
                frames.append(dict(frame=fid, page=page, start=pending[0], end=pending[-1], loci='|'.join(pending)))
                for loc in pending:
                    membership[loc] = fid
                pending = []
        if pending:
            exclusions.append(dict(page=page, loci='|'.join(pending), reason='NO_KNOWN_END'))
    groups = defaultdict(list)
    for e in events:
        groups[(e['edition'], e['base'], e['folio'])].append(e)
    pairs, cells = [], []
    for (ed, base, folio), es in sorted(groups.items()):
        ps, ys = [e for e in es if e['lead'] == 'p'], [e for e in es if e['lead'] == 'y']
        if not ps or not ys:
            continue
        local = []
        for p in ps:
            for y in ys:
                pl, yl = p['locus'], y['locus']
                pp, yp = pl.rsplit('.', 1)[0], yl.rsplit('.', 1)[0]
                pf, yf = membership.get(pl, ''), membership.get(yl, '')
                order = 'UNRESOLVED'
                if pp != yp:
                    status = 'CROSS_SIDE_SELECTOR'
                else:
                    if pl in rank and yl in rank:
                        order = 'P_BEFORE_Y' if rank[pl] < rank[yl] else 'Y_BEFORE_P'
                    status = 'UNRESOLVED_BOUNDARY' if not pf or not yf else 'SAME_PARAGRAPH' if pf == yf else 'DIFFERENT_PARAGRAPHS'
                row = dict(edition=ed, base=base, folio=folio, p_locus=pl, y_locus=yl,
                           p_form=p['form'], y_form=y['form'], p_start=p['start'], y_start=y['start'],
                           p_frame=pf, y_frame=yf, order=order, status=status)
                pairs.append(row)
                local.append(row)
        cells.append(dict(edition=ed, base=base, folio=folio, pairs=len(local),
                          statuses='|'.join(sorted({r['status'] for r in local})),
                          same_paragraph_p_before_y=sum(r['status'] == 'SAME_PARAGRAPH' and r['order'] == 'P_BEFORE_Y' for r in local),
                          paragraph_head_p_before_y=sum(r['status'] == 'SAME_PARAGRAPH' and r['order'] == 'P_BEFORE_Y' and r['p_start'] == '1' for r in local)))
    assert len(cells) == 30
    write(OUT / 'PAIRS.tsv', pairs)
    write(OUT / 'CELLS.tsv', cells)
    write(OUT / 'FRAMES.tsv', frames)
    write(OUT / 'BOUNDARY_EXCLUSIONS.tsv', exclusions, ['page', 'loci', 'reason'])
    write(OUT / 'CONSENSUS_LINES.tsv', consensus)
    result = {'scope': 'All frozen same-base/same-leaf p/y cells; source-marked same-side paragraphs only',
              'cells': len(cells), 'pairs': len(pairs), 'complete_physical_frames': len(frames),
              'reader_counts': {ed: dict(Counter(r['status'] for r in pairs if r['edition'] == ed)) for ed in ('ZL3b', 'IT2a', 'RF1b')},
              'ordered_same_paragraph': [r for r in pairs if r['status'] == 'SAME_PARAGRAPH'],
              'claim_ceiling': 'Local scope opportunity only; no shared referent, meaning, normalization, significance or independent confirmation'}
    (OUT / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
