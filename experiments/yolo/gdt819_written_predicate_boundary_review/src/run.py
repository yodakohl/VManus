#!/usr/bin/env python3
"""Source-group aware boundary packet; no glyph expansion or meaning decoder."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
META=['page','locus','kind','paragraph_start','paragraph_end','eva_clean','ivtff_raw']
GROUP_COLS=['source_group_id','edition','locus','page','source_group_index','source_group_count',
 'paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw',
 'clean_ascii_fragments','clean_ascii_fragment_count','legacy_surface_positions_1based','legacy_mapping_status']


def require(ok,message):
    if not ok:
        raise ValueError(message)


def enc(x):
    return json.dumps(x,ensure_ascii=False)


def table(rows):
    out=io.StringIO()
    w=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()


def query(path,columns,pages):
    command=['./vmanus-exp','query-tsv',path,'--selector','page']
    for page in pages:
        command+=['--allow',page]
    command+=['--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=True)
    stats=[json.loads(s[12:]) for s in p.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    parser=csv.DictReader(io.StringIO(p.stdout),delimiter='\t')
    require(parser.fieldnames==columns and len(stats)==1,'Guard schema')
    rows=list(parser)
    require(len(rows)==stats[0]['selected'] and {r['page'] for r in rows}==set(pages),'Guard coverage')
    return rows,dict(command=command,stats=stats[0],projection_sha256=hashlib.sha256(p.stdout.encode()).hexdigest())


def build():
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    pages=spec['pages']; editions=spec['editions']; targets=spec['targets']
    require(pages==['f76r','f77r','f81r'] and spec['sealed_data']==['f84','f84r'],'Scope')
    source,g1=query('transcription/voynich_zl3b_lines.tsv',META,pages)
    cross,g2=query('transcription/voynich_cross_transcription_lines.tsv',['page','locus',*editions.values()],pages)
    atlas,g3=query(spec['source_atlas'],GROUP_COLS,pages)
    by={r['locus']:r for r in source}
    require(len(by)==len(source)==137 and set(by)=={r['locus'] for r in cross},'Source locus coverage')
    for r in cross:
        require(by[r['locus']]['page']==r['page'] and by[r['locus']]['eva_clean']==r['zl3b_clean'],'Source join')
        by[r['locus']].update(r)
    def record(r):
        return {k:r[k] for k in META if k!='eva_clean'} | {'readings_json':enc({rd:r[rd] for rd in editions.values()})}
    blocks,prose,labels,neighbors=[],[],[],[]
    doc=['# GDT819 target paragraphs and separate interleaved labels','',
         'Legacy clean readings below are for locus registration, NOT diplomatic group boundaries.',
         'GROUP_COMPARISON.tsv / SOURCE_GROUPS.tsv govern the five target source-group claims.','']
    for page,start,end in spec['paragraphs']:
        block=[by[f'{page}.{n}'] for n in range(start,end+1)]
        p=[r for r in block if r['kind']=='P']; lab=[r for r in block if r['kind']!='P']
        require(p[0]['paragraph_start']==p[-1]['paragraph_end']=='1' and
            all(r['paragraph_start']=='0' for r in p[1:]) and all(r['paragraph_end']=='0' for r in p[:-1]),'Whole P flags')
        bid=f'{page}.{start}--{page}.{end}'
        blocks.append(dict(block_id=bid,page=page,first=p[0]['locus'],last=p[-1]['locus'],prose_loci=len(p),
            interleaved_label_loci=enc([r['locus'] for r in lab])))
        prose += [dict(block_id=bid,**record(r)) for r in p]
        labels += [dict(block_id=bid,**record(r)) for r in lab]
        doc+=['## '+bid,'']
        for r in block:
            doc+=[f"{r['locus']} [{r['kind']}] ZL clean: `{r['zl3b_clean']}`"]
            doc += [rd+': `'+r[rd]+'`' for rd in list(editions.values())[1:] if r[rd]!=r['zl3b_clean']]
            doc+=['']
        for i,r in enumerate(p):
            if r['locus'] in targets:
                n=int(r['locus'].split('.')[1]); prev=by.get(f'{page}.{n-1}'); nex=by.get(f'{page}.{n+1}')
                neighbors.append(dict(page=page,locus=r['locus'],block_id=bid,prev_prose=p[i-1]['locus'] if i else '',
                    next_prose=p[i+1]['locus'] if i+1<len(p) else '',prev_record=prev['locus'] if prev else '',
                    prev_record_kind=prev['kind'] if prev else '',next_record=nex['locus'] if nex else ''))
    groups=[r for r in atlas if r['locus'] in targets]
    comparisons=[]
    for locus in targets:
        for edition,reader in editions.items():
            group=sorted([r for r in groups if r['locus']==locus and r['edition']==edition],key=lambda r:int(r['source_group_index']))
            require(group and [int(r['source_group_index']) for r in group]==list(range(1,len(group)+1)) and
                all(int(r['source_group_count'])==len(group) for r in group),'Complete source groups')
            fragments=[w for r in group for w in r['clean_ascii_fragments'].split()]
            boundaries=[r['right_separator'] for r in group[:-1]]
            require(all(group[i]['right_separator']==group[i+1]['left_separator'] for i in range(len(group)-1)),'Separator adjacency')
            comparisons.append(dict(page=by[locus]['page'],locus=locus,edition=edition,source_group_count=len(group),
                source_groups_json=enc([r['ivtff_group_raw'] for r in group]),separators_json=enc(boundaries),
                atlas_ascii_fragments_json=enc(fragments),current_clean=by[locus][reader],
                current_clean_token_count=len(by[locus][reader].split()),
                atlas_flat_equals_current=int(fragments==by[locus][reader].split())))
    issues=[r for r in groups if int(r['clean_ascii_fragment_count'])!=1 or '@' in r['ivtff_group_raw'] or
            'UNCERTAIN_SMALL_SPACE' in (r['left_separator'],r['right_separator'])]
    result=dict(experiment_id='GDT819',status='SOURCE_GROUP_AND_VISUAL_BOUNDARIES_NOT_MEANINGS',
        pages=pages,targets=targets,source_loci=len(source),atlas_projected_groups=len(atlas),
        target_rows=len(targets),paragraph_blocks=len(blocks),prose_loci=len(prose),interleaved_labels=len(labels),
        target_source_groups=len(groups),comparisons=len(comparisons),issue_groups=len(issues),
        atlas_flat_current_matches=sum(r['atlas_flat_equals_current'] for r in comparisons),guarded_queries=[g1,g2,g3],
        source_group_not_authorial_word=True,extended_glyph_expansion=False,historical_sources_modified=False,
        new_admissions=0,dictionary_changed=False,confirmed_lexemes=0,confirmed_plaintext_clauses=0,meanings_validated=False,
        sealed_data=['f84','f84r'])
    return {'TARGETS.tsv':table([record(by[t]) for t in targets]),'BLOCKS.tsv':table(blocks),
        'PARAGRAPHS.tsv':table(prose),'INTERLEAVED_LABELS.tsv':table(labels),'NEIGHBORS.tsv':table(neighbors),
        'SOURCE_GROUPS.tsv':table(groups),'GROUP_COMPARISON.tsv':table(comparisons),'ISSUE_GROUPS.tsv':table(issues),
        'FULL_READER.md':'\n'.join(doc).rstrip()+'\n','RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    outputs=build()
    for name,content in outputs.items():
        path=EXP/'artifacts'/name
        if args.check:
            require(path.read_text()==content,'Replay differs '+name)
        else:
            path.write_text(content)
    r=json.loads(outputs['RESULT.json'])
    print(enc({k:r[k] for k in ['status','prose_loci','interleaved_labels','target_source_groups','comparisons','atlas_flat_current_matches']}))


if __name__=='__main__':
    main()
