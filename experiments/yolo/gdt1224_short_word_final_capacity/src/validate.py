#!/usr/bin/env python3
"""Independent regex and selected-ID reconstruction; no runner imports."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import csv,hashlib,io,json,re,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
    s=json.loads((D/'src/SPEC.json').read_text());expected=json.loads((A/'RESULT.json').read_text())
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    signs='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
    pattern=re.compile('|'.join(re.escape(g) for g in sorted(signs,key=lambda x:(-len(x),x))))
    ids=json.loads((ROOT/s['anchor_ids']).read_text());wanted={k:(ed,i) for ed,keys in ids.items() for i,k in enumerate(keys)}
    assert len(wanted)==24000
    allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed'];assert len(allowed)==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',s['source'],'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    seen=set();selected=defaultdict(list)
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        k=r['edition']+'|'+r['locus']+'|G'+str(int(r['source_group_index'])).zfill(3)
        if k not in wanted:continue
        assert k not in seen;seen.add(k);ed,rank=wanted[k]
        tokens=pattern.findall(r['ivtff_group_raw'])
        assert ''.join(tokens)==r['ivtff_group_raw'] and tokens
        assert r['kind']=='P' and r['edition']==ed
        assert r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END')
        selected[ed].append((rank,k,r,tokens))
    assert seen==set(wanted)
    reconstructed={}
    for ed,items in sorted(selected.items()):
        words=defaultdict(int);ends=defaultdict(int);witness={};all_short=0
        for rank,k,r,tokens in sorted(items):
            if len(tokens)==2:
                all_short+=1
                if (r['left_separator'],r['right_separator'])!=('DEFINITE_SPACE','DEFINITE_SPACE'):continue
                words[r['ivtff_group_raw']]+=1;ends[tokens[1]]+=1
                if tokens[1] not in witness:witness[tokens[1]]={'id':k,'word':r['ivtff_group_raw'],'glyphs':tokens,'page':r['page'],'locus':r['locus'],'source_group_index':int(r['source_group_index']),'left_separator':r['left_separator'],'right_separator':r['right_separator']}
        reconstructed[ed]={'sample_groups':8000,'all_two_glyph_groups':all_short,'internal_two_glyph_groups':sum(words.values()),'internal_two_glyph_types':len(words),'final_glyph_types':len(ends),'final_counts':dict(sorted(ends.items())),'word_counts':dict(sorted(words.items())),'witnesses':dict(sorted(witness.items())),'exceeds_bound':len(ends)>6}
    assert reconstructed==expected['readings']
    count=sum(r['exceeds_bound'] for r in reconstructed.values())
    status='SIX_FINAL_SHORT_GROUP_ARCHITECTURE_EXCLUDED' if count==3 else 'SIX_FINAL_BOUND_EXCEEDED_SOME_READINGS' if count else 'NO_SHORT_FINAL_CONTRADICTION_IN_FIXED_SAMPLE'
    assert status==expected['status'] and expected['model_final_capacity']==6
    p=json.loads((ROOT/s['params_source']).read_text())['best']['params']
    outputs=[[p['initial'][i]]+(['o'] if p['initial'][i]=='q' else [])+[p['final'][0][f]] for i in range(21) for f in range(6)]
    two=[o for o in outputs if len(o)==2]
    assert len(two)==120 and len({o[-1] for o in two})==6
    fixture=json.loads((A/'PRE_OUTPUT_FIXTURES.json').read_text())
    assert fixture['two_glyph_rows']==120 and fixture['two_glyph_final_types']==6 and fixture['mask_body_cases']==61952
    result={'status':'PASS','finished_utc':datetime.now(timezone.utc).isoformat(),'selected_ids':len(seen),'readings':3,'independent_regex_counts_and_every_certificate':True,'empty_body_direct_rows':len(outputs),'two_glyph_final_types':6,'scientific_status':status,'scope':'Same-author independent code; no independent palaeography or semantic confirmation.','guard_output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()}
    (A/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
