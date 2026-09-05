#!/usr/bin/env python3
"""Test inherited quality arity against adjacent written value-run length."""
import csv, hashlib, io, json, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
BASE=Path(__file__).resolve().parent.parent
ART=BASE/'artifacts'

def read(path):
    with path.open(encoding='utf-8',newline='') as h: return list(csv.DictReader(h,delimiter='\t'))
def write(name,rows,fields):
    with (ART/name).open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def query(source,pages,columns):
    cmd=[str(ROOT/'vmanus-exp'),'query-tsv',source,'--selector','page']
    for page in pages: cmd+=['--allow',page]
    cmd+=['--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
    done=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    stats=[json.loads(s[12:]) for s in done.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    assert len(stats)==1
    return list(csv.DictReader(io.StringIO(done.stdout),delimiter='\t')),dict(source=source,allow_count=len(pages),columns=columns,stats=stats[0])
def following(words,i,values):
    end=i+1
    while end<len(words) and words[end] in values: end+=1
    return words[i+1:end],words[end] if end<len(words) else 'LINE_END'
def main():
    manifest=json.loads((BASE/'experiment.json').read_text())
    for item in manifest['inputs']:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
    spec=json.loads((BASE/'src/SPEC.json').read_text()); heads={r['surface']:r for r in spec['heads']};values=set(spec['value_forms'])
    pages=[r['page'] for r in read(ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')]
    assert len(pages)==179 and not any(p.startswith('f84') for p in pages)
    lines,ls=query('transcription/voynich_zl3b_lines.tsv',pages,['page','locus','eva_clean'])
    cross,cs=query('transcription/voynich_cross_transcription_lines.tsv',pages,['page','locus','zl3b_clean','it2a_clean','rf1b_clean'])
    cross={(r['page'],r['locus']):r for r in cross};events=[]
    for line in lines:
        words=line['eva_clean'].split();readers=cross[line['page'],line['locus']]
        assert readers['zl3b_clean']==line['eva_clean']
        for i,word in enumerate(words):
            if word not in heads: continue
            head=heads[word];run,right=following(words,i,values);rank=words[:i+1].count(word)-1;support=1
            for column in ['it2a_clean','rf1b_clean']:
                other=readers[column].split();positions=[j for j,t in enumerate(other) if t==word]
                if len(positions)==words.count(word) and following(other,positions[rank],values)==(run,right): support+=1
            events.append(dict(event_id=f'AR{len(events)+1:04d}',page=line['page'],locus=line['locus'],token_index=i+1,head=word,
                arity=head['arity'],ending=head['ending'],quality_core=head['quality_core'],wrapper=head['wrapper'],
                value_run_length=len(run),value_run=' '.join(run),value_equal=int(len(run)>=2 and len(set(run))==1),
                right_stop=right,right_censored=int(right=='LINE_END'),reader_support=support,source_line=line['eva_clean']))
    fields=['event_id','page','locus','token_index','head','arity','ending','quality_core','wrapper','value_run_length','value_run','value_equal','right_stop','right_censored','reader_support','source_line']
    write('HEAD_VALUE_RUNS.tsv',events,fields); summaries=[]
    for population in ['ALL','EXCLUDE_DISCOVERY_LOCUS','EXCLUDE_DISCOVERY_PAGE']:
        for ending in ['OL','OR']:
            for arity in range(3):
                g=[r for r in events if r['ending']==ending and r['arity']==arity and r['reader_support']==3 and not r['right_censored']
                    and r['value_run_length']>=1 and (population!='EXCLUDE_DISCOVERY_LOCUS' or r['locus']!=spec['discovery_locus'])
                    and (population!='EXCLUDE_DISCOVERY_PAGE' or r['page']!=spec['discovery_page'])]
                multi=[r for r in g if r['value_run_length']>=2]
                summaries.append(dict(population=population,ending=ending,arity=arity,eligible=len(g),value_single=len(g)-len(multi),
                    value_multiple=len(multi),multiple_pages=len({r['page'] for r in multi}),identical_multiple=sum(r['value_equal'] for r in multi),
                    mixed_multiple=sum(not r['value_equal'] for r in multi)))
    write('SUMMARY.tsv',summaries,['population','ending','arity','eligible','value_single','value_multiple','multiple_pages','identical_multiple','mixed_multiple'])
    (ART/'GUARDED_QUERY_STATS.json').write_text(json.dumps([ls,cs],indent=2,sort_keys=True)+'\n')
    fields=['edge_id','batch_id','page','physical_folio','diagram_unit_id','pivot_visual_id','pivot_locus','target_visual_id','target_locus','relation_type',
        'direction_basis','ownership_basis','geometry_only_selection','source_manifest_id','page_crop_sha256','pivot_crop_sha256','target_crop_sha256',
        'source_aware_localizer','relation_reviewer','relation_confidence','ambiguity_state','formal_access_state','fold_assignment','eligibility_status']
    packet=[]
    for r in events:
        if r['arity']!=2 or r['ending']!='OL' or r['value_run_length']<2 or r['reader_support']!=3: continue
        packet.append(dict(zip(fields,[r['event_id'],'GDT810_TEXT_ARITY',r['page'],re.match(r'f\d+',r['page'])[0],r['event_id'],'TEXT_HEAD',
            f"{r['locus']}@{r['token_index']}",'TEXT_VALUE',f"{r['locus']}@{r['token_index']+r['value_run_length']}",
            'FORMAL_HEAD_THEN_MULTIPLE_VALUES','WRITTEN_ADJACENCY','TEXT_ONLY_NO_VISUAL_OWNER','FALSE','GDT810','NONE','NONE','NONE',
            'cached_reader','source_sequence_audit','LOW','TEXT_RELATION_ONLY','UNSEALED_ALREADY_INSPECTED','EXPLORATORY','INELIGIBLE_TEXT_ONLY'])))
    write('GDT388_RELATION_PACKET.tsv',packet,fields)
    intake=subprocess.run([str(ROOT/'vmanus-exp'),'check-edge-packet',str((ART/'GDT388_RELATION_PACKET.tsv').relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
    gate=json.loads(intake.stdout)
    assert not gate['score_ready'] and not gate['eligible_edges'] and gate['packet_rows']==len(packet)
    assert intake.returncode==(1 if packet else 0) and gate['errors']==[f'edge row {i}: formal access is not sealed' for i in range(2,len(packet)+2)]
    (ART/'GDT388_EDGE_INTAKE.json').write_text(json.dumps(gate,indent=2,sort_keys=True)+'\n')
    ext=[r for r in summaries if r['population']=='EXCLUDE_DISCOVERY_PAGE']
    q1=next(r for r in ext if r['ending']=='OL' and r['arity']==1);q2=next(r for r in ext if r['ending']=='OL' and r['arity']==2)
    rate=lambda r:r['value_multiple']/r['eligible'] if r['eligible'] else None
    if q2['value_multiple']==0: status='NO_EXTERNAL_PAIRED_QUALITY_MULTIPLE_VALUE_SUPPORT'
    elif q2['multiple_pages']<2 or not q1['eligible'] or rate(q2)<=rate(q1): status='EXTERNAL_EXAMPLES_WITHOUT_CLEAR_ARITY_PREFERENCE'
    else: status='PROVISIONAL_PAIRED_QUALITY_MULTIPLE_VALUE_LEAD'
    result=dict(experiment_id='GDT810',status=status,selectors=len(pages),source_lines=len(lines),head_types=len(heads),head_occurrences=len(events),
        summaries=summaries,discovery_locus=spec['discovery_locus'],confirmed_lexemes=0,component_exports=0,new_pages=0,semantic_identity_selected=False,
        edge_score_ready=gate['score_ready'],sealed_data={'f84':'FORBIDDEN','f84r':'FORBIDDEN'},
        artifact_sha256={name:hashlib.sha256((ART/name).read_bytes()).hexdigest() for name in ['HEAD_VALUE_RUNS.tsv','SUMMARY.tsv','GUARDED_QUERY_STATS.json','GDT388_RELATION_PACKET.tsv','GDT388_EDGE_INTAKE.json']})
    (ART/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ['status','head_occurrences','head_types','summaries']},sort_keys=True))
if __name__=='__main__':main()
