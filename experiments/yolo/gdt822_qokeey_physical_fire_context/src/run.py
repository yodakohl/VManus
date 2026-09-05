#!/usr/bin/env python3
"""Exact physical-fire trial over complete admitted qokeey contexts."""
import argparse
import json
import runpy
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
PREV = ROOT / 'experiments/yolo/gdt821_raiin_admitted_paragraph_transfer'
B = runpy.run_path(str(PREV / 'src/run.py'))
query, read, table, enc, require = [B[k] for k in ['query','read_table','table','enc','require']]
META, GCOLS, MARKS = B['META'], B['GCOLS'], B['MARKS']


def build():
    spec = json.loads((EXP/'src/SPEC.json').read_text())
    require(spec['whole']=='qokeey' and spec['gloss_de']=='Feuer?' and
            spec['sense']=='PHYSICAL_FIRE_NOT_HEAT_HEATING_WARMTH_DRUG_AIR_OR_WATER' and
            spec['sealed_data']==['f84','f84r'], 'Fixed physical sense and seals')
    admission_spec=json.loads((PREV/'src/SPEC.json').read_text())
    pages=sorted({r['source_selector'] for p in admission_spec['admission_inputs'] for r in read(ROOT/p)})
    require(len(pages)==39 and not any(p.startswith('f84') for p in pages),'Admission union')
    lines,g1=query('transcription/voynich_zl3b_lines.tsv',META,pages)
    cross,g2=query('transcription/voynich_cross_transcription_lines.tsv',['page','locus',*spec['editions'].values()],pages)
    atlas,g3=query(admission_spec['source_atlas'],GCOLS,pages)
    by={r['locus']:dict(r) for r in lines}
    require(len(by)==len(lines)==len(cross)==len({r['locus'] for r in cross}),'Unique source rows')
    for r in cross:
        require(r['locus'] in by and r['page']==by[r['locus']]['page'] and r['zl3b_clean']==by[r['locus']]['eva_clean'],'Join')
        by[r['locus']].update(r)
    hits=[r for r in atlas if r['ivtff_group_raw']=='qokeey']
    clean_only=[r for r in atlas if r['ivtff_group_raw']!='qokeey' and 'qokeey' in r['clean_ascii_fragments'].split()]
    targets={r['locus'] for r in hits}; inherited={r['locus'] for r in read(PREV/'artifacts/CONTEXTS.tsv')}
    require(inherited<=set(by) and len(hits)==153 and len(targets)==50,'Precount and inherited coverage')
    requested=targets|inherited; blocks=[]; selected={}; mapping={}
    for page in pages:
        stream=sorted([r for r in lines if r['page']==page],key=lambda r:int(r['locus'].split('.')[1]))
        prose=[r for r in stream if r['kind']=='P']; partitions=[]; part=[]
        for r in prose:
            if part and (r['paragraph_start']=='1' or part[-1]['paragraph_end']=='1'):
                partitions.append(part); part=[]
            part.append(r)
        if part: partitions.append(part)
        chunks=[]
        for part in partitions:
            if not any(r['locus'] in requested for r in part): continue
            first,last=[int(r['locus'].split('.')[1]) for r in [part[0],part[-1]]]
            chunk=[r for r in stream if first<=int(r['locus'].split('.')[1])<=last]
            require(all(r['kind'] in ['P','L'] for r in chunk),'Foreign record inside prose')
            chunks.append(('P',chunk,part[0]['paragraph_start']=='1' and part[-1]['paragraph_end']=='1'))
        chunks += [(r['kind'],[r],True) for r in stream if r['locus'] in requested and r['kind']!='P' and
                   not any(r in ch for _,ch,_ in chunks)]
        for kind,chunk,complete in chunks:
            bid=chunk[0]['locus']+'--'+chunk[-1]['locus']
            blocks.append(dict(block_id=bid,page=page,kind=kind,complete=int(complete),first=chunk[0]['locus'],last=chunk[-1]['locus'],
                loci_json=enc([r['locus'] for r in chunk]),qokeey_targets_json=enc([r['locus'] for r in chunk if r['locus'] in targets])))
            for r in chunk:
                require(r['locus'] not in selected,'Overlapping context')
                selected[r['locus']]=by[r['locus']]; mapping[r['locus']]=bid
    require(requested<=set(selected),'Complete requested coverage')
    order=sorted(selected,key=lambda l:(by[l]['page'],int(l.split('.')[1])))
    groups=[r for r in atlas if r['locus'] in selected]; grouped=defaultdict(list)
    for r in groups: grouped[r['locus'],r['edition']].append(r)
    proposal=json.loads((ROOT/admission_spec['inherited_proposal']).read_text())
    base=proposal['base_exact_glosses']|{'qokeey':'Feuer?'}
    contexts=[]; trials=[]; comparisons=[]; neighbours=[]
    doc=['# GDT822 complete source-group context reader','','Dots/commas are source separator states, not sentence punctuation. All variants remain.','']
    for loc in order:
        r=selected[loc]; contexts.append(dict(block_id=mapping[loc],**{k:r[k] for k in META if k!='eva_clean'},
            target=int(loc in targets),inherited821=int(loc in inherited),readings_json=enc({v:r[v] for v in spec['editions'].values()})))
        doc.append(f"{loc} {r['kind']} start={r['paragraph_start']} end={r['paragraph_end']} qokeey-target={int(loc in targets)}")
        native={}
        for edition,reader in spec['editions'].items():
            gs=sorted(grouped[loc,edition],key=lambda g:int(g['source_group_index']))
            require(gs and [int(g['source_group_index']) for g in gs]==list(range(1,len(gs)+1)) and
                    all(int(g['source_group_count'])==len(gs) for g in gs),'Complete group vector')
            require(gs[0]['left_separator']=='LINE_START' and gs[-1]['right_separator']=='LINE_END' and
                    all(gs[i]['right_separator']==gs[i+1]['left_separator'] for i in range(len(gs)-1)),'Separators')
            words=[g['ivtff_group_raw'] for g in gs]
            raw=''.join((MARKS[g['left_separator']] if i else '')+g['ivtff_group_raw'] for i,g in enumerate(gs)); native[edition]=raw
            flat=[w for g in gs for w in g['clean_ascii_fragments'].split()]
            comparisons.append(dict(locus=loc,edition=edition,group_count=len(gs),flat_matches=int(flat==r[reader].split()),raw_grouped_line=raw))
            for i,g in enumerate(gs):
                if words[i]=='qokeey':
                    neighbours.append(dict(source_group_id=g['source_group_id'],locus=loc,edition=edition,
                        left=words[i-1] if i else 'LINE_START',right=words[i+1] if i+1<len(words) else 'LINE_END',
                        left_separator=g['left_separator'],right_separator=g['right_separator']))
            for world,sense in [('ASCENT','steigt?'),('LIGHTNESS','leicht?')]:
                glosses=base|{'raiin':sense}
                trials.append(dict(world=world,locus=loc,edition=edition,source_group_ids_json=enc([g['source_group_id'] for g in gs]),
                    source_groups_json=enc(words),separators_json=enc([g['right_separator'] for g in gs[:-1]]),
                    literal_json=enc([glosses.get(w,'['+w+']') for w in words]),confidence=spec['confidence']))
            doc.append(edition+(': same as ZL3b' if edition!='ZL3b' and raw==native['ZL3b'] else ': `'+raw+'`'))
        doc.append('')
    result=dict(experiment_id='GDT822',status='C0_PHYSICAL_FIRE_CONTEXT_TRIAL_NOT_TRANSLATION',admitted_selectors=39,
        inventory_loci=len(lines),inventory_groups=len(atlas),exact_group_readings=len(hits),target_loci=len(targets),target_pages=sorted({by[l]['page'] for l in targets}),
        target_kinds=dict(Counter(by[l]['kind'] for l in targets)),exact_by_edition=dict(Counter(g['edition'] for g in hits)),clean_only_group_readings=len(clean_only),
        context_loci=len(order),context_kinds=dict(Counter(by[l]['kind'] for l in order)),blocks=len(blocks),complete_P_blocks=sum(b['kind']=='P' and b['complete'] for b in blocks),
        incomplete_blocks=[b['block_id'] for b in blocks if not b['complete']],inherited821_loci=len(inherited),new_context_loci=len(set(selected)-inherited),
        source_groups=len(groups),reader_rows=len(comparisons),flat_matches=sum(r['flat_matches'] for r in comparisons),literal_rows=len(trials),
        new_admissions=0,new_image_inspections=0,dictionary_changed=False,meanings_validated=False,confirmed_lexemes=0,confirmed_clauses=0,
        sealed_data=['f84','f84r'],guarded_queries=[g1,g2,g3])
    return {'EXACT_HITS.tsv':table(hits,GCOLS),'CLEAN_ONLY_HITS.tsv':table(clean_only,GCOLS),'BLOCKS.tsv':table(blocks),'CONTEXTS.tsv':table(contexts),
        'SOURCE_GROUPS.tsv':table(groups,GCOLS),'NEIGHBOURS.tsv':table(neighbours),'COMPARISONS.tsv':table(comparisons),'TRIALS.tsv':table(trials),
        'FULL_READER.md':'\n'.join(doc).rstrip()+'\n','RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,content in build().items():
        path=EXP/'artifacts'/name
        if args.check: require(path.read_text()==content,'Replay differs: '+name)
        else: path.write_text(content)
    print('Physical-fire source and two-world trial reproduced; no meaning validation')


if __name__=='__main__': main()
