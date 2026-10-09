"""Bounded existing-cache concordance; no normalization or relation score."""
from pathlib import Path
import sys, json, hashlib
from collections import Counter, defaultdict

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT))
from tools import word_profiles as wp

A = D / 'artifacts'
FORMS = ('daldy', 'daly', 'dal', 'aldy', 'dy')
EDITIONS = ('ZL3b', 'IT2a', 'RF1b')

def write(name, data):
    (A / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def main():
    for name, digest in json.loads((A / 'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    conn = wp.ensure_cache(ROOT)
    receipt = wp.receipt(conn)
    pages = set(receipt['inputs']['selectors'])
    assert len(pages) == 179 and not any(p.startswith('f84') or p == 'f116v' for p in pages)
    rows = [dict(r) for r in conn.execute(
        'SELECT ' + ','.join(wp.COLUMNS) + ' FROM groups WHERE ivtff_group_raw IN (?,?,?,?,?) '
        'ORDER BY page,locus,edition,source_group_index', FORMS)]
    contexts = []
    for row in rows:
        assert row['page'] in pages and row['edition'] in EDITIONS
        near = [dict(r) for r in conn.execute(
            'SELECT ' + ','.join(wp.COLUMNS) + ' FROM groups WHERE edition=? AND page=? AND locus=? '
            'AND source_group_index BETWEEN ? AND ? ORDER BY source_group_index',
            (row['edition'], row['page'], row['locus'], row['source_group_index'] - 2, row['source_group_index'] + 2))]
        at = {r['source_group_index']: r for r in near}
        contexts.append(dict(target=row, window=near,
            previous=at.get(row['source_group_index']-1), next=at.get(row['source_group_index']+1)))
    loci = sorted({(r['page'], r['locus']) for r in rows if r['ivtff_group_raw'] == 'daldy'})
    lines = []
    for page, locus in loci:
        for edition in EDITIONS:
            line = [dict(r) for r in conn.execute(
                'SELECT ' + ','.join(wp.COLUMNS) + ' FROM groups WHERE page=? AND locus=? AND edition=? '
                'ORDER BY source_group_index', (page, locus, edition))]
            lines.append(dict(page=page, locus=locus, edition=edition, groups=line))
    conn.close()
    write('CONTEXT_PACKET.json', dict(source_receipt=receipt, forms=FORMS, contexts=contexts, daldy_lines=lines))
    summaries = {}
    shared = []
    for edition in EDITIONS:
        summaries[edition] = {}
        frames = defaultdict(lambda: defaultdict(list))
        for form in FORMS:
            own = [c for c in contexts if c['target']['edition']==edition and c['target']['ivtff_group_raw']==form]
            prev = Counter(c['previous']['ivtff_group_raw'] if c['previous'] else '<LINE_START>' for c in own)
            after = Counter(c['next']['ivtff_group_raw'] if c['next'] else '<LINE_END>' for c in own)
            summaries[edition][form] = dict(count=len(own), loci=len({c['target']['locus'] for c in own}),
                previous=sorted(prev.items(), key=lambda x:(-x[1],x[0])), next=sorted(after.items(), key=lambda x:(-x[1],x[0])))
            if form in ('daldy','daly','dal'):
                for c in own:
                    if c['previous'] is not None and c['next'] is not None:
                        t = c['target']
                        frame = (c['previous']['ivtff_group_raw'], c['next']['ivtff_group_raw'],t['left_separator'],t['right_separator'])
                        frames[frame][form].append(dict(page=t['page'], locus=t['locus'], id=t['source_group_id']))
        for frame, members in sorted(frames.items()):
            if len(members)>1:
                shared.append(dict(edition=edition, left=frame[0], right=frame[1], left_separator=frame[2],
                    right_separator=frame[3], members=dict(members)))
    presence = []
    for page, locus in loci:
        presence.append(dict(page=page, locus=locus, readers={e:sum(r['ivtff_group_raw']=='daldy'
            for line in lines if line['page']==page and line['locus']==locus and line['edition']==e for r in line['groups']) for e in EDITIONS}))
    write('RESULT.json', dict(status='DESCRIPTIVE_CONTEXTS_NO_SEMANTIC_SELECTION', summaries=summaries,
        daldy_locus_union=len(loci), daldy_presence=presence, exact_two_sided_shared_frames=shared,
        frame_caution='Within-reader descriptive identity only; no physical alignment, morphology, relation score or significance.',
        scientific_claim='Existing exposed exact forms and neighbours, retaining reader and boundary disagreement.'))
    for line in lines:
        forms = [r['ivtff_group_raw'] for r in line['groups']]
        print(line['locus'], line['edition'], ' '.join('['+s+']' if s in FORMS else s for s in forms))
    print(json.dumps({'daldy_loci':len(loci),'shared_two_sided_frames':len(shared),'counts':{e:{f:x['count'] for f,x in v.items()} for e,v in summaries.items()}}))

if __name__ == '__main__':
    main()
