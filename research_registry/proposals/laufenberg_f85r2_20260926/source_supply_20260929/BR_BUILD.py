"""Align four explicitly hypothetical readings; never infer or decode a word."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')
CACHED = Path('experiments/yolo/gdt1104_source_head_consumer_contrast/artifacts/RETAINED_SOURCE.json')
RAW = Path('experiments/semantic_assumptions/results/source_separator_transcription.tsv')
ALLOW = Path('experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')
COLS = 'source_group_id,edition,page,locus,kind,code,source_row_index,source_group_index,paragraph_start,paragraph_end,ivtff_group_raw,left_separator,right_separator'
CANDIDATES = ('E-S', 'E-A', 'D-S', 'D-A')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def native_blocks(rows, edition):
    lines = defaultdict(list)
    for r in rows:
        if r['edition'] == edition and r['kind'] == 'P':
            lines[r['locus']].append(r)
    ordered = sorted(lines.values(), key=lambda line: int(line[0]['source_row_index']))
    if edition == 'RF1b':
        return [('RF1b|f24r|unmarked1-20', ordered, False)]
    blocks, current = [], []
    for line in ordered:
        line.sort(key=lambda r: int(r['source_group_index']))
        if any(r['paragraph_start'] == '1' for r in line):
            assert not current, 'Unclosed native unit'
        current.append(line)
        if any(r['paragraph_end'] == '1' for r in line):
            first, last = current[0][0]['locus'], current[-1][0]['locus']
            assert any(r['paragraph_start'] == '1' for r in current[0])
            blocks.append((f'{edition}|f24r|{first}-{last}', current, True))
            current = []
    assert not current, 'Unclosed native unit'
    return blocks


def build_source():
    assert 'f24r' in ALLOW.read_text().splitlines()
    cmd = ['./vmanus-exp', 'query-tsv', str(RAW), '--selector', 'page',
           '--allow', 'f24r', '--columns', COLS]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=True)
    f24 = list(csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'))
    assert len(f24) == 325 and {r['page'] for r in f24} == {'f24r'}
    previous = json.loads(CACHED.read_text())
    units = []
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        for page, first, last in (('f32r', 1, 5), ('f22r', 4, 6)):
            lines = defaultdict(list)
            for r in previous['projected_rows']:
                # This cached packet contains only eight admitted selectors.
                if r['page'] == page and r['edition'] == edition and r['kind'] == 'P':
                    n = int(r['locus'].rsplit('.', 1)[1])
                    if first <= n <= last:
                        lines[r['locus']].append(r)
            ordered = sorted(lines.values(), key=lambda line: int(line[0]['source_row_index']))
            assert len(ordered) == last - first + 1
            for line in ordered:
                line.sort(key=lambda r: int(r['source_group_index']))
            uid = f'{edition}|{page}|{page}.{first}-{page}.{last}'
            native = edition != 'RF1b'
            if native:
                old = next(x for x in previous['matched_native_units'] if x['id'] == uid)
                assert old['lines'] == ordered
            units.append(dict(id=uid, native=native, lines=ordered))
        for uid, lines, native in native_blocks(f24, edition):
            units.append(dict(id=uid, native=native, lines=lines))
    return dict(units=units, receipts={
        'cached_packet': {'path': str(CACHED), 'sha256': digest(CACHED)},
        'raw_source': {'path': str(RAW), 'sha256': digest(RAW)},
        'admission': {'path': str(ALLOW), 'sha256': digest(ALLOW)},
        'guard_command': cmd, 'guard_stderr': proc.stderr.strip(),
        'all_f24_groups_retained': len(f24),
        'seals': ['f84', 'f84r'], 'reserve_opened': False,
        'previously_exposed': True, 'independent_confirmation_capacity': 0})


def render(form, candidate, previous):
    event, axis = candidate.split('-')
    if form == 'qotchy':
        return 'C0:abkochen' if event == 'E' else 'C0:abgekocht'
    if form == 'qokchy':
        return 'C0:als Trank einnehmen' if event == 'E' else 'C0:als Trank verwendet'
    if form in ('dain', 'daiin'):
        level = 'mittel' if form == 'dain' else 'hoch'
        if form == 'daiin' and previous == 'qokchy':
            return f'C0:{level}; ' + ('Wirkungsstärke' if axis == 'S' else 'Einnahmemenge')
        return f'C0:{level}; Träger/Achse UNGEBUNDEN'
    return f'UNGELESEN<{form}>'


def make_outputs(packet):
    align, md, evidence = [], [
        '# BR: vier partielle C0-Lesungen, vollständiger Rohtext',
        'Alle Gruppen bleiben erhalten. UNGELESEN ist keine übersetzte Lücke.',
        'Jeder C0-Wert ist angesetzt; Zeilenumbrüche werden nicht zu Sätzen.',
        'E/Achse S oder A; D/Achse S oder A. Keine Fassung ist ausgewählt.\n'], []
    counts = Counter()
    for u in packet['units']:
        md.append(f"## {u['id']} ({'native Absatzgrenzen' if u['native'] else 'RF: unmarkiertes Vergleichsfenster'})\n")
        previous = None
        for line in u['lines']:
            md.append(f"{line[0]['locus']} Roh: `{' '.join(r['ivtff_group_raw'] for r in line)}`\n")
            per = {c: [] for c in CANDIDATES}
            for r in line:
                form = r['ivtff_group_raw']
                values = {c: render(form, c, previous) for c in CANDIDATES}
                align.append(dict(unit=u['id'], native=u['native'],
                                  source_group_id=r['source_group_id'], locus=r['locus'],
                                  raw=form, **values))
                counts[(r['edition'], 'groups')] += 1
                counts[(r['edition'], 'hypothetical' if form in ('qotchy','qokchy','dain','daiin') else 'unread')] += 1
                for c in CANDIDATES:
                    per[c].append(values[c])
                previous = form
            for c in CANDIDATES:
                md.append(f"{c}: {' | '.join(per[c])}\n")
        flat = [r for line in u['lines'] for r in line]
        for i in range(len(flat)-1):
            pair = [flat[i]['ivtff_group_raw'], flat[i+1]['ivtff_group_raw']]
            if pair in (['qotchy','qokchy'], ['qokchy','qotchy']):
                for c in CANDIDATES:
                    if c.startswith('E'):
                        consequence = 'BOIL_THEN_INGEST_COMPATIBLE_UNBOUND_PATIENT' if pair[0] == 'qotchy' else 'INGEST_BEFORE_BOIL_CONFLICT_IF_SAME_PREPARED_PORTION'
                    else:
                        consequence = 'TWO_DESCRIPTION_FIELDS_ORDER_NOT_EVENT_ORDER'
                    evidence.append(dict(candidate=c, unit=u['id'],
                        locus=flat[i]['locus'], first_id=flat[i]['source_group_id'],
                        pair=' '.join(pair), predicted_surface_order=('qotchy before qokchy' if c.startswith('E') else 'no chronological order required'), model_consequence=consequence,
                        identity_status='HYPOTHESIZED_NOT_OBSERVED',
                        independent_confirmation_capacity=0))
    source_ids = [r['source_group_id'] for u in packet['units'] for line in u['lines'] for r in line]
    assert len(align) == len(source_ids) == len(set(source_ids))
    assert [r['source_group_id'] for r in align] == source_ids
    def tsv(path, rows):
        with path.open('w', newline='') as f:
            w=csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
            w.writeheader(); w.writerows(rows)
    tsv(OUT/'BR_ALIGNMENT.tsv',align)
    tsv(OUT/'BR_CANDIDATES.tsv',evidence)
    (OUT/'BR_READINGS.md').write_text('\n'.join(md).rstrip()+'\n')
    result = dict(phase='EXPLORATORY_NOT_BLIND_FIXED_TEST',
        total_groups=len(align), native_units=sum(u['native'] for u in packet['units']),
        unmarked_windows=sum(not u['native'] for u in packet['units']),
        counts={e:{k:counts[e,k] for k in ('groups','hypothetical','unread')} for e in ('ZL3b','IT2a','RF1b')},
        candidates={c:{'decision':('REJECT_STRICT_SAME_PREPARED_PORTION_CHRONOLOGICAL_CONJUNCTION' if c.startswith('E') else 'C0_UNSELECTED'),
            'chronological_countercase':'f24r.12 under shared same prepared portion' if c.startswith('E') else None,
            'scalar_axis':'effect_strength' if c.endswith('S') else 'administered_amount',
            'source_branches_instantiated':False} for c in CANDIDATES},
        axis_discriminating_written_meanings=0, confirmed_words=0,
        independently_bound_material=False, milk_bound=False,
        bowel_recipient_or_effect_bound=False, explicit_mild_strong_branch_bound=False,
        independent_confirmation_capacity=0, significance_claim=False,
        known_reversed_pair_is_not_new_discovery=True,
        decision='PARTIAL_PREPARATION_USE_READING_RETAINS_AMOUNT_STRENGTH_EQUIVALENCE_STOP_THIS_EXTENSION')
    (OUT/'BR_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch',action='store_true')
    args=parser.parse_args()
    if args.fetch:
        packet=build_source()
        (OUT/'BR_SOURCE.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
    else:
        packet=json.loads((OUT/'BR_SOURCE.json').read_text())
        assert packet['receipts']['cached_packet']['sha256'] == digest(CACHED)
    make_outputs(packet)
