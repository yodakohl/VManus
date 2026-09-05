#!/usr/bin/env python3
"""One joined-form trial over admitted cached complete paragraphs."""
import argparse
import json
import runpy
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
HELPERS = runpy.run_path(str(ROOT/'experiments/yolo/gdt823_qol_source_anaphor_trial/src/run.py'))
read, table, enc = [HELPERS[k] for k in ['read','table','enc']]


def build():
    spec = json.loads((EXP/'src/SPEC.json').read_text())
    assert spec['whole'] == 'qolchedy' and spec['gloss_de'] == 'daraus? wird?'
    assert spec['components'] == ['qol','chedy'] and spec['sealed_data'] == ['f84','f84r']
    prior = ROOT/spec['prior']/'artifacts'
    groups, contexts, blocks, originals = [read(prior/n) for n in
        ['SOURCE_GROUPS.tsv','CONTEXTS.tsv','BLOCKS.tsv','TRIALS.tsv']]
    assert len(groups) == 8391 and len(contexts) == 320
    assert all(not r['page'].startswith('f84') for r in groups + contexts)
    by = defaultdict(list)
    for g in groups: by[g['locus'],g['edition']].append(g)
    hits = []
    for (loc,edition), gs in by.items():
        gs.sort(key=lambda g:int(g['source_group_index']))
        for i,g in enumerate(gs):
            joined = g['ivtff_group_raw'] == 'qolchedy'
            split = g['ivtff_group_raw'] == 'qol' and i+1 < len(gs) and gs[i+1]['ivtff_group_raw'] == 'chedy'
            if not (joined or split): continue
            end = i if joined else i+1
            hits.append(dict(hit_id=g['source_group_id'],locus=loc,page=g['page'],edition=edition,
                form='JOINED' if joined else 'SPLIT', group_ids_json=enc([x['source_group_id'] for x in gs[i:end+1]]),
                source_groups_json=enc([x['ivtff_group_raw'] for x in gs[i:end+1]]),
                internal_separator='NONE_JOINED' if joined else g['right_separator'],
                preceding=gs[i-1]['ivtff_group_raw'] if i else 'LINE_START',
                following=gs[end+1]['ivtff_group_raw'] if end+1 < len(gs) else 'LINE_END',
                earlier_exact_chedy=sum(x['ivtff_group_raw']=='chedy' for x in gs[:i]),
                final_group_id=gs[end]['source_group_id'],
                next_group_id=gs[end+1]['source_group_id'] if end+1<len(gs) else 'NONE'))
    targets = {h['locus'] for h in hits}
    block_ids = {c['block_id'] for c in contexts if c['locus'] in targets}
    coverage = [b for b in blocks if b['block_id'] in block_ids]
    assert all(b['complete']=='1' and b['kind']=='P' for b in coverage)
    trials = []
    for old in originals:
        if old['locus'] not in targets: continue
        words, literal = json.loads(old['source_groups_json']), json.loads(old['literal_json'])
        for i,w in enumerate(words):
            if w == 'qol': literal[i] = 'daraus?'
            elif w == 'qolchedy': literal[i] = spec['gloss_de']
        trials.append(old | {'literal_json':enc(literal),'confidence':spec['confidence']})
    docs = ['# GDT824 affected full-line trial vectors','','One cell per source group; joined whole remains ONE cell. Source groups and separators remain in TRIALS.',
        'Full nine paragraphs: manifest-bound GDT822 FULL_READER, COVERAGE.tsv. All words are C0 guesses.','']
    for c in contexts:
        if c['locus'] not in targets: continue
        docs += ['## '+c['locus'],'']
        for t in [t for t in trials if t['locus']==c['locus']]:
            docs += [t['edition']+' '+t['world']+': '+' | '.join(json.loads(t['literal_json']))]
        docs.append('')
    packet = []
    for i,h in enumerate(hits,1):
        assert h['next_group_id'] != 'NONE'
        packet.append(dict(edge_id=f'G824-E{i:03d}',batch_id='GDT824_'+h['form'],page=h['page'],physical_folio=h['page'][:-1],
            diagram_unit_id='LINE:'+h['locus'],pivot_visual_id='GROUP:'+h['final_group_id'].replace('|',':'),
            pivot_locus=h['locus']+'@'+h['edition']+'G'+h['final_group_id'].split('G')[-1],
            target_visual_id='GROUP:'+h['next_group_id'].replace('|',':'),
            target_locus=h['locus']+'@'+h['edition']+'G'+h['next_group_id'].split('G')[-1],
            relation_type='NEXT_TOKEN',direction_basis='TRANSCRIPTION_ORDER_ONLY',ownership_basis='NONVISUAL_TEXT_ADJACENCY',
            geometry_only_selection='FALSE',source_manifest_id='GDT822',page_crop_sha256='NONE',pivot_crop_sha256='NONE',target_crop_sha256='NONE',
            source_aware_localizer='GDT824_RUNNER',relation_reviewer='SAME_AUTHOR_ACCOUNTING_ONLY',relation_confidence='EXPLORATORY',
            ambiguity_state='UNREVIEWED_TEXT_RELATION',formal_access_state='PREVIOUSLY_ACCESSED',fold_assignment='NONE',
            eligibility_status='INELIGIBLE_EXPLORATORY_TEXT_RELATION'))
    reviewed = [c for c in contexts if c['block_id'] in block_ids]
    result = dict(experiment_id='GDT824',status='C0_COMPOSITION_RETAINED_PREDICATE_AND_REFERENT_DEBTS',
        cache_loci=320,source_groups=8391,reader_hits=len(hits),forms=dict(Counter(h['form'] for h in hits)),
        loci=len(targets),joined_loci=len({h['locus'] for h in hits if h['form']=='JOINED'}),
        split_loci=len({h['locus'] for h in hits if h['form']=='SPLIT'}),
        paragraphs=len(coverage),reread_loci=len(reviewed),reread_kinds=dict(Counter(c['kind'] for c in reviewed)),
        literal_rows=len(trials),joined_cells_changed=sum(json.loads(t['source_groups_json']).count('qolchedy') for t in trials),
        following_by_form={f:dict(Counter(h['following'] for h in hits if h['form']==f)) for f in ['JOINED','SPLIT']},
        previously_known_exact_split_join_bridge_loci=['f77r.34'],new_admissions=0,new_downloads=0,cached_images_reinspected=2,
        image_pages_reinspected=1,all39_census=False,confirmed_lexemes=0,confirmed_clauses=0,dictionary_changed=False,meanings_validated=False,
        sealed_data=['f84','f84r'])
    return {'HITS.tsv':table(hits),'COVERAGE.tsv':table(coverage),'TRIALS.tsv':table(trials),
        'READER.md':'\n'.join(docs).rstrip()+'\n','RELATION_PACKET.tsv':table(packet),
        'RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,text in build().items():
        path=EXP/'artifacts'/name
        if args.check: assert path.read_text()==text,name
        else: path.write_text(text)
    intake = subprocess.run([str(ROOT/'vmanus-exp'),'check-edge-packet',str((EXP/'artifacts/RELATION_PACKET.tsv').relative_to(ROOT))],
        cwd=ROOT,text=True,capture_output=True)
    report = json.loads(intake.stdout)
    assert intake.returncode == 1 and report['status'] == 'INVALID_PACKET' and report['eligible_edges'] == 0
    assert len(report['errors']) == 27 and all(e.endswith('formal access is not sealed') for e in report['errors'])
    path = EXP/'artifacts/RELATION_INTAKE.json'
    if args.check: assert path.read_text() == intake.stdout
    else: path.write_text(intake.stdout)
    print('GDT824 exact composition overlay reproduced, no semantic proof')


if __name__=='__main__': main()
