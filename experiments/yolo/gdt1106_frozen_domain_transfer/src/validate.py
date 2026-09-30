#!/usr/bin/env python3
"""Independent raw-neighbour owner/field reconstruction and conservation."""
import csv
import gzip
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
OLD=ROOT/'experiments/yolo/gdt1105_dual_temperature_scope'
sys.path.insert(0,str(ROOT))
from tools.word_profiles import COLUMNS, ensure_cache, receipt

def main():
    result=json.loads((BASE/'artifacts/RESULT.json').read_text())
    lock=json.loads((BASE/'PREREG_LOCK.json').read_text())
    for path,digest in (lock['sha256'] | result['input_hashes']).items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    rows=list(csv.DictReader(io.StringIO(gzip.decompress((BASE/'artifacts/SOURCE.tsv.gz').read_bytes()).decode()),delimiter='\t'))
    for r in rows:
        for col in ('source_group_index','source_group_count'):
            r[col]=int(r[col])
    conn=ensure_cache(ROOT)
    assert rows==[dict(r) for r in conn.execute('SELECT * FROM groups WHERE kind=? ORDER BY edition,page,locus,source_group_index',('P',))]
    saved=json.loads((BASE/'artifacts/SOURCE_RECEIPT.json').read_text())
    assert saved['cache_receipt']==receipt(conn)
    conn.close()
    allowed=set(saved['cache_receipt']['inputs']['selectors'])
    assert len(allowed)==179
    assert all(r['page'] in allowed and not r['page'].startswith('f84') and r['page']!='f116v' and r['kind']=='P' for r in rows)
    assert saved['groups']==len(rows)==result['source_groups']
    assert saved['source_gzip_sha256']==hashlib.sha256((BASE/'artifacts/SOURCE.tsv.gz').read_bytes()).hexdigest()
    lines=defaultdict(list)
    for r in rows:
        lines[(r['edition'],r['page'],r['locus'])].append(r)
    assert len(lines)==result['full_lines']
    for line in lines.values():
        assert [r['source_group_index'] for r in line]==list(range(1,len(line)+1))
        assert all(r['source_group_count']==len(line) for r in line)
    spec=json.loads((OLD/'src/MODEL.json').read_text())
    prior=json.loads((OLD/'artifacts/RESULT.json').read_text())
    detail=json.loads(gzip.decompress((BASE/'artifacts/DETAILS.json.gz').read_bytes()))
    models=detail['models']
    assert [m['id'] for m in models]==prior['survivors']
    vocab=set(spec['nominals'])|set(spec['fields'])|set(spec['compound'])
    field_refs={}
    run_count=0
    for line in lines.values():
        run_count+=sum(r['ivtff_group_raw'] in vocab and (i==0 or line[i-1]['ivtff_group_raw'] not in vocab) for i,r in enumerate(line))
        for i,r in enumerate(line):
            if r['ivtff_group_raw'] not in spec['fields']|spec['compound']:
                continue
            lo=hi=i
            while lo and line[lo-1]['ivtff_group_raw'] in vocab: lo-=1
            while hi+1<len(line) and line[hi+1]['ivtff_group_raw'] in vocab: hi+=1
            heads=[j for j in range(lo,hi+1) if line[j]['ivtff_group_raw'] in spec['nominals']]
            left=[j for j in heads if j<i];right=[j for j in heads if j>i]
            head=left[-1] if left else right[0] if right else None
            split=right[0] if left and right and right[0]-left[-1]==3 and i==right[0]-1 else head
            field_refs[r['source_group_id']]={'row':r,'LEFT_FLAT':line[head]['source_group_id'] if head is not None else None,
                'PAIR_SPLIT':line[split]['source_group_id'] if split is not None else None}
    assert run_count==result['retained_runs']
    def canon(items):return sorted(items,key=lambda c:(c['source'],c['kind']))
    by_id={r['source_group_id']:r for r in rows}
    old_models={m['id']:m for m in prior['models']}
    replay={r['source_group_id'] for r in rows if r['page'] in ('f9r','f9v','f50r','f50v')}
    cf=json.loads((ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/CF_FULL_LEAVES.json').read_text())
    assert {r['source_group_id'] for r in cf['rows']}==replay
    for r in cf['rows']:
        assert {k:r[k] for k in COLUMNS}==by_id[r['source_group_id']]
    clash_rows=[]
    for m,s in zip(models,result['models']):
        expected=[];unbound=[]
        policy,polarity,mask=m['id'].split(':');mask=int(mask[1:])
        for r in rows:
            raw=r['ivtff_group_raw']
            if raw in spec['nominals'] and spec['nominals'][raw]['natural']:
                expected.append({'edition':r['edition'],'owner':r['source_group_id'],'source':r['source_group_id'],'raw':raw,
                    'domain':'natural','thermal':spec['nominals'][raw]['natural'],'kind':'inherited_nominal_C0'})
            elif r['source_group_id'] in field_refs:
                ref=field_refs[r['source_group_id']];field=spec['fields'].get(raw) or spec['compound'][raw]
                domain=field.get('domain') or ('natural' if mask & (1<<(2*field['wrapped']+field['tail_value'])) else 'physical')
                c={'edition':r['edition'],'owner':ref[policy],'source':r['source_group_id'],'raw':raw,'domain':domain,
                    'thermal':'hot' if (field['polarity']=='k')==(polarity=='k_hot') else 'cold','kind':'whole_field_C0'}
                (expected if c['owner'] is not None else unbound).append(c)
        assert canon(expected)==canon(m['bound_claims'])
        assert canon(unbound)==canon(m['unbound_fields'])
        grouping=defaultdict(list)
        for c in expected: grouping[(c['edition'],c['owner'],c['domain'])].append(c)
        failed={k:canon(v) for k,v in grouping.items() if {c['thermal'] for c in v}=={'hot','cold'}}
        actual={(c['edition'],c['owner'],c['domain']):canon(c['claims']) for c in m['contradictions']}
        assert failed==actual
        assert m['survives_all_readers_conditionally']==(not failed)==s['survives_all_readers_conditionally']
        assert s['contradictory_owners']==len(failed)
        assert s['reader_contradictions']==dict(Counter(k[0] for k in failed))
        assert s['bound_claims']==len(expected) and s['unbound_fields']==len(unbound)
        assert canon(s['bare_bound_claims'])==canon([c for c in expected if c['raw'] in ('ky','ty')])
        assert s['bare_unbound_count']==sum(c['raw'] in ('ky','ty') for c in unbound)
        for key in ('bound_claims','unbound_fields'):
            assert canon([c for c in m[key] if c['source'] in replay])==canon(old_models[m['id']][key])
        for c in m['contradictions']:
            row=by_id[c['owner']]
            assert c['page']==row['page'] and c['locus']==row['locus'] and c['physical_leaf']==re.match(r'f\d+',row['page']).group()
            clash_rows.append(dict(model=m['id'], **{k:c[k] for k in ('edition','physical_leaf','page','locus','owner','domain')},claims=json.dumps(c['claims'],sort_keys=True)))
    tsv=list(csv.DictReader((BASE/'artifacts/CONTRADICTIONS.tsv').open(),delimiter='\t'))
    assert tsv==clash_rows
    bare=list(csv.DictReader((BASE/'artifacts/BARE_CONTEXTS.tsv').open(),delimiter='\t'))
    assert {r['source_group_id'] for r in bare}=={r['source_group_id'] for r in rows if r['ivtff_group_raw'] in ('ky','ty')}
    assert len(bare)==result['bare_count']
    assert dict(Counter(r['edition']+':'+r['raw'] for r in bare))==result['bare_counts']
    for r in bare:
        assert json.loads(r['complete_line_records'])==lines[(r['edition'],r['page'],r['locus'])]
    signatures=defaultdict(list)
    for m in models:signatures[json.dumps(canon(m['bound_claims']+m['unbound_fields']),sort_keys=True)].append(m['id'])
    assert list(signatures.values())==result['full_prediction_groups']
    assert result['survivors']==[m['id'] for m in models if not m['contradictions']]
    assert result['status']==('ALL_ORIGINAL_SURVIVORS_CONTRADICTED' if not result['survivors'] else 'CONDITIONAL_SURVIVORS_NO_MEANING_SELECTED')
    assert result['confirmed_words']==result['independent_meaning_confirmation_leaves']==0
    assert result['reserved_pages_opened']==[] and result['significance'] is None
    output={'status':'PASS_INDEPENDENT_COMPLETE_SOURCE_AND_FROZEN_CONSEQUENCES','models':len(models),'source_groups':len(rows),
        'all_fields_checked_per_model':len(field_refs),'original_replay_checked':True,'bare_contexts_checked':len(bare),
        'contradiction_rows_checked':len(clash_rows),'claim_ceiling':'Validator of conditional consequences, not independent meaning confirmation'}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output))

if __name__=='__main__':main()
