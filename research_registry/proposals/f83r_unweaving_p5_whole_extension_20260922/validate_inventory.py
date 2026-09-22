#!/usr/bin/env python3
"""Static source and frozen-entry accounting only; no semantic evaluation."""
import hashlib
import json
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
P=ROOT/'research_registry/proposals'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(x,msg):
    if not x:raise ValueError(msg)
def main():
    a=read(HERE/'ACCOUNT.json');l=read(HERE/'LEXICON.json');s=read(HERE/'SOURCE.json');g=read(HERE/'GROUPS.json');d=read(HERE/'DECISION.json');receipt=read(HERE/'RECEIPT.json')
    old=read(P/'raw_f83r_unweaving_second_paragraph_frozen24_20260921.json')
    rota=read(P/'raw_f83r_rota_complete_persistent_voices_20260921.json')
    parent=read(P/'raw_f83r_rota_second_paragraph_frozen53_20260921.json')
    for name,value in receipt['files'].items():check(digest(HERE/name)==value,'Receipt hash '+name)
    fixed24=old['frozen_parent']['all_24_meanings_exact'];fixed40=old['new_40_lexicon']
    check(len(fixed24)==24 and len(fixed40)==40 and not set(fixed24)&set(fixed40),'64 original entries')
    for word,value in fixed24.items():check(l['values'][word]['value']==value,'Old value changed '+word)
    for word,value in fixed40.items():
        for key in ['tag','meaning']:check(l['values'][word][key]==value[key],'Old value changed '+word+' '+key)
    oldrows=old['target']['new_complete_record']['lines']+old['target']['old_complete_projection']
    check(a['old_scope']['records']==oldrows,'Old96 source rows changed')
    check(a['old_scope']['clauses']['P3_inherited_11']==old['new_complete_clauses'],'Old11 clauses changed')
    check(a['old_scope']['clauses']['P4_inherited_8']==old['frozen_parent']['all_eight_clauses'],'Old8 clauses changed')
    check(s['groups']==rota['target']['diplomatic_primary_ZL3b']['lines'],'P5 source changed')
    oldcount=sum(len(x['words']) if 'words' in x else len(x['raw'].split()) for x in oldrows)
    expected=[]
    for line,clause in zip(s['groups'],a['p5_rows']):
        check(clause['locus']==line['locus'] and clause['raw']==line['words'] and clause['source_ids']==line['source_ids'],'P5 row/source mismatch')
        check(len(clause['surface_values'])==len(line['words']),'Surface-value count')
        for i,(word,sid) in enumerate(zip(line['words'],line['source_ids']),1):expected.append((len(expected)+1,line['locus'],i,sid,word))
    check([(x['position'],x['locus'],x['line_group'],x['source_id'],x['raw']) for x in g['groups']]==expected,'GROUPS not exact')
    forms=Counter(x[4] for x in expected);fixed=set(fixed24)|set(fixed40);new=set(forms)-fixed
    check(len(expected)==62 and len(forms)==53 and oldcount==96 and oldcount+len(expected)==158,'Position/type counts')
    check(len(new)==38 and sum(forms[w] for w in new)==40,'New-form count')
    check(set(l['values'])==fixed|new and len(l['values'])==102,'Complete dictionary keys')
    for word in new:check(l['values'][word]['status']=='NEW_PROVISIONAL_WHOLE_VALUE','New status')
    it=s['reader_units']['IT2a_complete_enclosing']['record'];check(it==parent['target']['complete_IT_enclosing_block'],'Full IT record changed')
    itcount=sum(len(x['words']) for x in it['lines']);slice_count=sum(len(x['words']) for x in it['lines'] if int(x['locus'].split('.')[1])>=31)
    check(itcount==92 and slice_count==60 and it['lines'][0]['locus']=='f83r.25' and it['lines'][-1]['locus']=='f83r.44','IT unit/slice')
    out=dict(status='PASS_SOURCE_AND_LITERAL_DICTIONARY_ACCOUNT_ONLY',old_positions=oldcount,p5_positions=len(expected),joint_positions=158,old_values=64,new_values=38,new_positions=40,retained_old_clauses=19,p5_raw_rows=14,p5_types=53,p5_old_types=len(set(forms)&fixed),p5_old_positions=sum(forms[w] for w in forms if w in fixed),it_complete_groups=itcount,it_corresponding_subspan_groups=slice_count,source_anchor_lines=sum(x['anchor_eligible'] for x in s['groups']),claimed_production_names=len(a['productions']),claimed_binding_names=len(a['nondefault_bindings']),claim_ceiling='No type/valency, temporal, epistemic, predicate or production-cap validation; manual review identifies actual operational violations.',reviewed_hashes={name:digest(HERE/name) for name in receipt['files']},primary_hashes={p.name:digest(p) for p in [P/'raw_f83r_unweaving_second_paragraph_frozen24_20260921.json',P/'raw_f83r_rota_complete_persistent_voices_20260921.json',P/'raw_f83r_rota_second_paragraph_frozen53_20260921.json']})
    (HERE/'INDEPENDENT_COVERAGE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['status','joint_positions','old_values','new_values','it_complete_groups','it_corresponding_subspan_groups']},sort_keys=True))
if __name__=='__main__':main()
