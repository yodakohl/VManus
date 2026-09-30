#!/usr/bin/env python3
import csv,io,json,hashlib,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
def rows(t): return list(csv.DictReader(io.StringIO(t),delimiter='\t'))
def q(path,cols,pages):
    a=[str(R/'vmanus-exp'),'query-tsv',str(R/path),'--selector','page']
    for p in pages:a+=['--allow',p]
    a+=['--columns',','.join(cols),'--forbid-prefix','f84','--forbid-prefix','f84r']
    return rows(subprocess.check_output(a,cwd=R,stderr=subprocess.PIPE,text=True))
m=json.loads((E/'src/MODEL.json').read_text())
for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
pages=[x['page'] for x in rows((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').read_text())]; assert len(set(pages))==179
b='experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts/'
blocks=q(b+'BLOCKS.tsv',['block_id','page','kind','complete','loci_json'],pages)
ctx=q(b+'CONTEXTS.tsv',['page','locus','kind','paragraph_start','paragraph_end'],pages); kinds={x['locus']:x for x in ctx}
g=q(b+'SOURCE_GROUPS.tsv',['page','source_group_id','edition','locus','source_group_index','source_group_count','left_separator','right_separator','ivtff_group_raw'],pages)
source={};seen=set()
for x in g:
    assert x['source_group_id'] not in seen;seen.add(x['source_group_id']);source.setdefault((x['edition'],x['locus']),[]).append(x)
for v in source.values():
    v.sort(key=lambda x:int(x['source_group_index'])); assert [int(x['source_group_index']) for x in v]==list(range(1,len(v)+1))
    assert all(int(x['source_group_count'])==len(v) for x in v)
    assert v[0]['left_separator']=='LINE_START' and v[-1]['right_separator']=='LINE_END'
    assert all(v[i]['right_separator']==v[i+1]['left_separator'] for i in range(len(v)-1))
cases=json.loads((E/'artifacts/CASES.json').read_text()); table=rows((E/'artifacts/CANDIDATE_TABLE.tsv').read_text());assert len(table)==len(cases)
complete=[x for x in blocks if x['kind']=='P' and x['complete']=='1'];expected={(b0['block_id'],ed,cid) for b0 in complete for ed in ['ZL3b','IT2a','RF1b'] for cid in m['candidates']}
assert expected=={(x['block_id'],x['edition'],x['candidate']) for x in cases} and len(cases)==len(expected)
index={x['block_id']:x for x in complete}; render=(E/'artifacts/FULL_READER.md').read_text()
for x,t in zip(cases,table):
    b0=index[x['block_id']]; locs=json.loads(b0['loci_json']); prose=[l for l in locs if kinds[l]['kind']=='P'];assert kinds[prose[0]]['paragraph_start']=='1' and kinds[prose[-1]]['paragraph_end']=='1'
    vector=[y for l in prose for y in source[x['edition'],l]];assert len(vector)==x['prose_groups']
    events=[];values=m['candidates'][x['candidate']]
    for offset,y in enumerate(vector,1):
        raw=y['ivtff_group_raw']
        if raw in values: events.append({'source_group_id':y['source_group_id'],'locus':y['locus'],'index':int(y['source_group_index']),'whole':raw,'phase':values[raw],'paragraph_offset':offset})
    assert events==x['events']
    i=next((e['paragraph_offset'] for e in events if e['phase']=='INTAKE_BY_PATIENT'),None);o=next((e['paragraph_offset'] for e in events if e['phase']=='DISCHARGE_BY_PATIENT'),None)
    assert i==x['first_intake'] and o==x['first_discharge']
    assert x['intake_count']==sum(e['phase']=='INTAKE_BY_PATIENT' for e in events) and x['discharge_count']==sum(e['phase']=='DISCHARGE_BY_PATIENT' for e in events)
    assert x['status']==('MISSING_PHASE' if i is None or o is None else ('INTAKE_FIRST' if i<o else 'DISCHARGE_FIRST'))
    assert x['independent_meaning_capacity']==0 and len(x['unbound_roles'])==5
    for k in t:assert t[k]==('' if x[k] is None else str(x[k]))
    # Exact whole row rendering; labels never join prose events.
    for l in locs:
        v=source[x['edition'],l]
        rendered=[{'raw':y['ivtff_group_raw'],'separator_after':y['right_separator'],'A':m['candidates']['A'].get(y['ivtff_group_raw'],'UNKNOWN'),'B':m['candidates']['B'].get(y['ivtff_group_raw'],'UNKNOWN')} for y in v]
        assert '- '+l+' '+kinds[l]['kind']+': '+json.dumps(rendered,ensure_ascii=False) in render
res=json.loads((E/'artifacts/RESULT.json').read_text());assert res['complete_P_blocks']==len(complete) and res['cases']==len(cases)
for cid in m['candidates']:
    counts={s:sum(x['candidate']==cid and x['status']==s for x in cases) for s in ['MISSING_PHASE','INTAKE_FIRST','DISCHARGE_FIRST']};counts={k:v for k,v in counts.items() if v}
    assert counts==res['candidates'][cid]['statuses'];assert res['candidates'][cid]['universal_bridge']==('REJECTED' if counts.get('DISCHARGE_FIRST') else 'NECESSARY_ORDER_ONLY_UNCONFIRMED')
assert res['confirmed_words']==res['independent_meaning_capacity']==res['source_role_bindings_found']==0 and res['significance']==False
v={'status':'PASS_INDEPENDENT_COMPLETE_CASE_ACCOUNTING','cases':len(cases),'complete_P_blocks':len(complete),'input_hashes_checked':True,'all_original_groups_separators_labels_retained':True,'semantic_validation':False}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
