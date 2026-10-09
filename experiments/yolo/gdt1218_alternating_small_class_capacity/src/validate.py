#!/usr/bin/env python3
"""Separate certificate checker; does not import runner or its parser."""
from pathlib import Path
from collections import Counter
import csv, hashlib, io, json, re, subprocess
E=Path(__file__).resolve().parents[1]; R=E.parents[2]; A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def main():
    lock=read(A/'REGISTRATION_LOCK.json')
    for p,h in lock['files'].items(): assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    p=R/'experiments/yolo/gdt1170_repetition_context_neutral_copy'
    allow=read(p/'src/SPEC.json')['allowed']; assert len(allow)==179
    assert not any(x.startswith('f84') or x=='f116v' for x in allow)
    cmd=['./vmanus-exp','query-tsv',str((p/'artifacts/GUARDED.tsv').relative_to(R)),'--selector','page']
    for a in allow:cmd+=['--allow',a]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=R,capture_output=True,text=True,check=True)
    ids=read(R/'experiments/yolo/gdt1211_one_variant_per_line_capacity/artifacts/TARGET_SAMPLE_IDS.json')
    wanted=set(sum(ids.values(),[])); records={}
    for row in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        ident='{}|{}|G{:03d}'.format(row['edition'],row['locus'],int(row['source_group_index']))
        if ident in wanted:
            assert ident not in records
            assert row['kind']=='P' and row['left_separator'] in ['LINE_START','DEFINITE_SPACE'] and row['right_separator'] in ['LINE_END','DEFINITE_SPACE']
            assert re.fullmatch(r'(?:ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf])+',row['ivtff_group_raw'])
            records[ident]=row
    assert len(records)==24000 and set(records)==wanted
    target=read(R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json')['targets']
    result=read(A/'RESULT.json'); certificates=read(A/'CERTIFICATES.json'); checked={}
    assert set(ids)==set(certificates)==set(result['readers'])=={'ZL3b','IT2a','RF1b'}
    for edition,sequence in ids.items():
        assert len(sequence)==len(set(sequence))==8000
        rows=[records[k] for k in sequence]; freqs=Counter(x['ivtff_group_raw'] for x in rows)
        top=sum(n for _,n in freqs.most_common(10)); assert len(freqs)==target[edition]['types'] and top==round(8000*target[edition]['top10_share'])
        # Enumerate candidate pairs by source IDs, independently of runner's tuple index.
        pairs=[]
        for ident in sequence:
            x=records[ident]; j=int(x['source_group_index'])
            nxt=f"{edition}|{x['locus']}|G{j+1:03d}"
            if nxt not in wanted:continue
            y=records[nxt]
            assert y['edition']==edition and y['page']==x['page'] and y['locus']==x['locus']
            if (x['right_separator'],y['left_separator'])!=('DEFINITE_SPACE','DEFINITE_SPACE'):continue
            if x['ivtff_group_raw']==y['ivtff_group_raw']:continue
            pairs.append({'page':x['page'],'locus':x['locus'],'left_index':j,'right_index':j+1,'left':x['ivtff_group_raw'],'right':y['ivtff_group_raw']})
        expected=[]; seen=set()
        for pair in pairs:
            endpoints={pair['left'],pair['right']}
            if seen.isdisjoint(endpoints):expected.append(pair);seen|=endpoints
            if len(expected)==65:break
        assert expected==certificates[edition]
        flattened=[w for edge in expected for w in (edge['left'],edge['right'])]
        assert len(flattened)==len(set(flattened))==2*len(expected)
        expected_result={'selected_groups':8000,'types':len(freqs),'top10_count':top,'certificate_edges':len(expected),'distinct_endpoint_forms':len(flattened),'minimum_small_class_size_certified':len(expected),'status':'EXCLUDED_64_FORM_ALTERNATION' if len(expected)==65 else 'NOT_EXCLUDED_BY_THIS_CERTIFICATE'}
        assert result['readers'][edition]==expected_result
        checked[edition]=len(expected)
    assert result['status']==('EXCLUDED_64_FORM_ALTERNATION' if max(checked.values())==65 else 'NOT_EXCLUDED_BY_THIS_CERTIFICATE')
    receipt=read(A/'RUN_RECEIPT.json');assert receipt['projection_sha256']==hashlib.sha256(call.stdout.encode()).hexdigest()
    validation={'status':'PASS','checked_certificate_edges':checked,'sample_ids':24000,'meaning_claims':0,'independence':'Separate implementation by same author, not independent manuscript evidence.'}
    (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation))
if __name__=='__main__':main()
