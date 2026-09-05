#!/usr/bin/env python3
"""Separate source reconstruction; same author, not independent semantic review."""
import argparse
import copy
import hashlib
import json
import runpy
from collections import defaultdict
from pathlib import Path

EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
PREV=ROOT/'experiments/yolo/gdt821_raiin_admitted_paragraph_transfer'
V=runpy.run_path(str(PREV/'src/validate.py'))
read,query,require,exact,enc,group_line=[V[k] for k in ['table','query','require','exact','enc','group_line']]
META,GCOLS,EDITIONS=V['META'],V['GCOLS'],V['EDITIONS']


def verify(packet,by,atlas,inherited,expected_loci,hits):
    contexts=packet['CONTEXTS.tsv']; groups=packet['SOURCE_GROUPS.tsv']; trials=packet['TRIALS.tsv']
    target={r['locus'] for r in hits}
    exact(packet['EXACT_HITS.tsv'],hits)
    exact(packet['CLEAN_ONLY_HITS.tsv'],[r for r in atlas if r['ivtff_group_raw']!='qokeey' and 'qokeey' in V['clean'](r['ivtff_group_raw'])])
    order=sorted(expected_loci,key=lambda l:(by[l]['page'],int(l.split('.')[1])))
    exact([r['locus'] for r in contexts],order)
    require(inherited<=expected_loci and len(contexts)==320,'Inherited coverage and selected loci')
    blocks=packet['BLOCKS.tsv']; mapping={}
    for block in blocks:
        locs=json.loads(block['loci_json']); first=by[locs[0]]; last=by[locs[-1]]
        require(block['first']==locs[0] and block['last']==locs[-1] and block['block_id']==locs[0]+'--'+locs[-1] and
                block['page']==first['page']==last['page'] and block['complete']=='1','Block identity')
        if block['kind']=='P':
            actual=[r['locus'] for r in by.values() if r['page']==first['page'] and
                    int(first['locus'].split('.')[1])<=int(r['locus'].split('.')[1])<=int(last['locus'].split('.')[1])]
            exact(locs,sorted(actual,key=lambda l:int(l.split('.')[1])))
            prose=[by[l] for l in locs if by[l]['kind']=='P']
            require(first['paragraph_start']==last['paragraph_end']=='1' and all(by[l]['kind'] in ['P','L'] for l in locs) and
                    all(r['paragraph_start']=='0' for r in prose[1:]) and all(r['paragraph_end']=='0' for r in prose[:-1]),'Full P boundary')
        else: require(len(locs)==1 and first['kind']==block['kind'],'Separate nonP')
        exact(json.loads(block['qokeey_targets_json']),[l for l in locs if l in target])
        for loc in locs:
            require(loc not in mapping,'Duplicate blocks');mapping[loc]=block['block_id']
    exact(set(mapping),expected_loci)
    for row in contexts:
        loc=row['locus'];r=by[loc]
        expected=dict(block_id=mapping[loc],**{k:r[k] for k in META if k!='eva_clean'},target=str(int(loc in target)),
            inherited821=str(int(loc in inherited)),readings_json=enc({v:r[v] for v in EDITIONS.values()}))
        exact(row,expected)
    exact(groups,[r for r in atlas if r['locus'] in expected_loci])
    grouped=defaultdict(list)
    for r in groups: grouped[r['locus'],r['edition']].append(r)
    require(len(groups)==8391 and len(grouped)==960,'Group coverage')
    expected_trials=[];comp=[];neighbors=[];doc=['# GDT822 complete source-group context reader','','Dots/commas are source separator states, not sentence punctuation. All variants remain.','']
    for loc in order:
        r=by[loc];native={}
        doc.append(f"{loc} {r['kind']} start={r['paragraph_start']} end={r['paragraph_end']} qokeey-target={int(loc in target)}")
        for edition,reader in EDITIONS.items():
            gs=sorted(grouped[loc,edition],key=lambda g:int(g['source_group_index']));raw,flat=group_line(gs);native[edition]=raw
            words=[g['ivtff_group_raw'] for g in gs]
            require(flat==r[reader].split(),'Flat source match')
            comp.append(dict(locus=loc,edition=edition,group_count=str(len(gs)),flat_matches='1',raw_grouped_line=raw))
            for i,g in enumerate(gs):
                if words[i]=='qokeey':
                    neighbors.append(dict(source_group_id=g['source_group_id'],locus=loc,edition=edition,left=words[i-1] if i else 'LINE_START',
                        right=words[i+1] if i+1<len(words) else 'LINE_END',left_separator=g['left_separator'],right_separator=g['right_separator']))
            for world,gloss in [('ASCENT','steigt?'),('LIGHTNESS','leicht?')]:
                meanings=V['BASE']|{'qokeey':'Feuer?','raiin':gloss}
                expected_trials.append(dict(world=world,locus=loc,edition=edition,source_group_ids_json=enc([g['source_group_id'] for g in gs]),
                    source_groups_json=enc(words),separators_json=enc([g['right_separator'] for g in gs[:-1]]),
                    literal_json=enc([meanings.get(w,'['+w+']') for w in words]),confidence='C0_CONCRETE_COMPLETION_TRIAL_NOT_WORD_IDENTIFICATION'))
            doc.append(edition+(': same as ZL3b' if edition!='ZL3b' and raw==native['ZL3b'] else ': `'+raw+'`'))
        doc.append('')
    exact(trials,expected_trials);exact(packet['COMPARISONS.tsv'],comp);exact(packet['NEIGHBOURS.tsv'],neighbors)
    exact(packet['FULL_READER.md'],'\n'.join(doc).rstrip()+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    require(spec['whole']=='qokeey' and spec['gloss_de']=='Feuer?' and spec['sense']=='PHYSICAL_FIRE_NOT_HEAT_HEATING_WARMTH_DRUG_AIR_OR_WATER'
        and spec['sealed_data']==['f84','f84r'] and not any(spec[k] for k in ['new_admissions','new_image_inspections','meanings_validated','dictionary_changed']),'Spec')
    pages=sorted({r['source_selector'] for name in V['ADMISSIONS'] for r in read(ROOT/name)})
    require(len(pages)==39 and not any(p.startswith('f84') for p in pages),'Admission')
    lines,g1=query('transcription/voynich_zl3b_lines.tsv',META,pages,1062)
    cross,g2=query('transcription/voynich_cross_transcription_lines.tsv',['page','locus',*EDITIONS.values()],pages,1062)
    atlas,g3=query(V['ATLAS'],GCOLS,pages,18981)
    by={r['locus']:dict(r) for r in lines}
    require(len(by)==len(cross)==len({r['locus'] for r in cross}),'Unique source join')
    for r in cross:
        require(r['page']==by[r['locus']]['page'] and r['zl3b_clean']==by[r['locus']]['eva_clean'],'Source agreement');by[r['locus']].update(r)
    hits=[r for r in atlas if r['ivtff_group_raw']=='qokeey'];targets={r['locus'] for r in hits}
    inherited={r['locus'] for r in read(PREV/'artifacts/CONTEXTS.tsv')};selected=set()
    # Different from the runner's partition: nearest actual P flags around each requested locus.
    for loc in targets|inherited:
        r=by[loc]
        if r['kind']!='P': selected.add(loc);continue
        stream=sorted([s for s in lines if s['page']==r['page']],key=lambda s:int(s['locus'].split('.')[1]))
        index=next(i for i,s in enumerate(stream) if s['locus']==loc)
        start=max(i for i in range(index+1) if stream[i]['kind']=='P' and stream[i]['paragraph_start']=='1')
        end=min(i for i in range(index,len(stream)) if stream[i]['kind']=='P' and stream[i]['paragraph_end']=='1')
        selected.update(s['locus'] for s in stream[start:end+1])
    names=['EXACT_HITS.tsv','CLEAN_ONLY_HITS.tsv','BLOCKS.tsv','CONTEXTS.tsv','SOURCE_GROUPS.tsv','NEIGHBOURS.tsv','COMPARISONS.tsv','TRIALS.tsv']
    packet={n:read(EXP/'artifacts'/n) for n in names};packet['FULL_READER.md']=(EXP/'artifacts/FULL_READER.md').read_text()
    verify(packet,by,atlas,inherited,selected,hits)
    result=json.loads((EXP/'artifacts/RESULT.json').read_text())
    checks={'exact_group_readings':153,'target_loci':50,'context_loci':320,'source_groups':8391,'reader_rows':960,'literal_rows':1920,
        'flat_matches':960,'complete_P_blocks':31,'blocks':33,'inherited821_loci':65,'new_context_loci':255,'admitted_selectors':39,
        'clean_only_group_readings':0,'inventory_loci':1062,'inventory_groups':18981,'new_admissions':0,'new_image_inspections':0,
        'confirmed_lexemes':0,'confirmed_clauses':0,'meanings_validated':False,'dictionary_changed':False}
    for k,v in checks.items(): exact(result[k],v)
    exact(result['incomplete_blocks'],[]);exact(result['guarded_queries'],[g1,g2,g3]);exact(result['sealed_data'],['f84','f84r'])
    exact(result['target_kinds'],{'P':50});exact(result['context_kinds'],{'P':309,'L':10,'C':1})
    exact(result['exact_by_edition'],{'ZL3b':52,'IT2a':54,'RF1b':47});exact(result['target_pages'],sorted({by[l]['page'] for l in targets}))
    mutations={}
    for mode in ['omit_inherited_label','omit_interleaved_label','translate_qokeedy','omit_second_fire','change_water_to_fire']:
        altered=copy.deepcopy(packet)
        if mode.startswith('omit_') and mode.endswith('label'):
            bad='f66r.12' if mode=='omit_inherited_label' else 'f76r.4'
            altered['CONTEXTS.tsv']=[r for r in altered['CONTEXTS.tsv'] if r['locus']!=bad]
        else:
            row=next(r for r in altered['TRIALS.tsv'] if r['locus']==('f75r.33' if mode=='change_water_to_fire' else 'f82r.24') and r['edition']=='IT2a')
            words=json.loads(row['source_groups_json']);lit=json.loads(row['literal_json'])
            if mode=='translate_qokeedy': lit[words.index('qokeedy')]='Feuer?'
            elif mode=='omit_second_fire': lit.pop([i for i,w in enumerate(words) if w=='qokeey'][-1])
            else: lit[words.index('qokain')]='Feuer?'
            row['literal_json']=enc(lit)
        try: verify(altered,by,atlas,inherited,selected,hits)
        except ValueError: mutations[mode]=True
        else: mutations[mode]=False
    require(all(mutations.values()),'Mutation detection')
    val=dict(experiment_id='GDT822',status='PASS_SEPARATE_SOURCE_RECONSTRUCTION_NOT_SEMANTICS',checks=checks,mutations_rejected=mutations,
        same_author=True,runner_imported_or_called=False,meanings_validated=False,
        artifact_sha256={n:hashlib.sha256((EXP/'artifacts'/n).read_bytes()).hexdigest() for n in [*names,'FULL_READER.md','RESULT.json']})
    out=json.dumps(val,indent=2,sort_keys=True)+'\n';path=EXP/'artifacts/VALIDATION.json'
    if args.check: exact(path.read_text(),out)
    else: path.write_text(out)
    print('PASS: separate source reconstruction and five mutations; meanings unvalidated')


if __name__=='__main__': main()
