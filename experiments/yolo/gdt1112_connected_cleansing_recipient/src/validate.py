"""Separate source/accounting reconstruction; no independence of meaning."""
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parents[1]

def main():
    m=json.loads((H/'src/MODEL.json').read_text());s=json.loads((H/'src/SOURCE.json').read_text());r=json.loads((H/'artifacts/RESULT.json').read_text())
    for p,digest in m['input_hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest
    for p,digest in json.loads((H/'MODEL_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest
    b=json.loads((ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/BT_SOURCE.json').read_text())
    pars=json.loads((ROOT/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text())
    expected={}
    for u in b['units']:
        seq=tuple((g['source_group_id'],g['ivtff_group_raw'],g['locus']) for line in u['lines'] for g in line)
        expected[tuple(v[0] for v in seq)]=(u['native'],seq)
    for ed in ('ZL3b','IT2a'):
        for p in pars[ed]:
            seq=tuple((gid,w,line['locus']) for line in p['lines'] for gid,w in zip(line['source_ids'],line['words']))
            if any(v[1]=='lkchey' for v in seq):expected[tuple(v[0] for v in seq)]=(True,seq)
    got={tuple(g['id'] for line in u['lines'] for g in line['groups']):(u['native'],tuple((g['id'],g['raw'],line['locus']) for line in u['lines'] for g in line['groups'])) for u in s['units']}
    assert got==expected
    ids=[g['id'] for u in s['units'] for line in u['lines'] for g in line['groups']];assert len(ids)==len(set(ids))==r['unique_source_groups']
    with (H/'artifacts/ALIGNMENT.tsv').open() as f:a=list(csv.DictReader(f,delimiter='\t'))
    with (H/'artifacts/CANDIDATE_TABLE.tsv').open() as f:cases=list(csv.DictReader(f,delimiter='\t'))
    assert len(a)==r['alignment_rows']==3*len(ids)
    actual={(x['candidate'],x['id']):x for x in a};assert len(actual)==len(a)
    expectedcases={}
    reader=(H/'artifacts/FULL_READER.md').read_text()
    graphs=json.loads((H/'artifacts/GRAPHS.json').read_text());graphmap={(g['candidate'],g['marker_id']):g for g in graphs}
    for u in s['units']:
        assert not u['page'].startswith('f84') and u['page']!='f116v'
        flat=[g for line in u['lines'] for g in line['groups']]
        for line in u['lines']:
            assert '- '+line['locus']+': '+' | '.join(g['raw'] for g in line['groups']) in reader
            for c,config in m['candidates'].items():
                vs=[]
                for j,g in enumerate(line['groups']):
                    item=actual[c,g['id']];value=config['lexicon'].get(g['raw'])
                    gloss=value['gloss'] if value else 'UNKNOWN';typ=value['type'] if value else 'UNBOUND'
                    if g['raw']=='s' and j+1<len(line['groups']) and line['groups'][j+1]['raw']=='chol':gloss='Teil/Posten von (nur s chol)';typ='PORTION_PREFIX_SCOPED'
                    assert item['raw']==g['raw'] and item['gloss']==gloss and item['type']==typ and item['unit']==u['id']
                    vs.append(gloss)
                assert '  - '+c+': '+' | '.join(vs) in reader
        for n,g in enumerate(flat):
            if g['raw']!='lkchey':continue
            positions={'Q':n-1,'P':n+1,'U':n+2}
            for c,config in m['candidates'].items():
                missing=[];wrong=[];unknown=[];raws={}
                for name,index in positions.items():
                    if index<0 or index>=len(flat):missing.append(name);raws[name]='';continue
                    raw=flat[index]['raw'];raws[name]=raw
                    val=config['lexicon'].get(raw)
                    if val is None:unknown.append(name)
                    elif val['type'] not in config['slot_types'][name]:wrong.append(name)
                status='ARITY_CONTRADICTION' if missing else 'TYPE_CONTRADICTION' if wrong else 'UNBOUND_SLOT_MEANINGS' if unknown else 'C0_TYPED_GRAPH_ONLY'
                expectedcases[c,g['id']]={'status':status,'missing':','.join(missing),'incompatible':','.join(wrong),'unbound':','.join(unknown),**{k+'_raw':v for k,v in raws.items()}}
                graph=graphmap[c,g['id']];assert graph['status']==status and graph['semantic_binding_independent'] is False
                for name,index in positions.items():
                    slot=graph['slots'][name]
                    if index<0 or index>=len(flat):assert slot is None
                    else:assert slot['id']==flat[index]['id'] and slot['raw']==flat[index]['raw']
                attach=n>=3 and [x['raw'] for x in flat[n-3:n]]==['qotchy','chody','qotain']
                assert bool(graph['attachment'])==attach
    assert len(expectedcases)==len(cases)==len(graphs)==r['case_rows']
    for row in cases:
        for key,val in expectedcases[row['candidate'],row['marker_id']].items():assert row[key]==val
    for c,summary in r['candidate_summaries'].items():
        native=[x for x in cases if x['candidate']==c and x['native']=='True'];assert len(native)==16
        assert dict(Counter(x['status'] for x in native))==summary['native_statuses']
        assert Counter(x['locus'].split('.')[0] for x in native)==Counter({'f115v':4,'f113r':8,'f113v':2,'f77v':2})
        aa=[x for x in a if x['candidate']==c];assert sum(x['type']=='UNBOUND' for x in aa)==summary['unread_positions']
        assert summary['conditional_construction_decision']=='STRICT_CONJUNCTION_CONTRADICTED'
        bad=[x for x in native if x['status']=='TYPE_CONTRADICTION'];assert len(bad)==1 and bad[0]['locus']=='f113r.14' and bad[0]['U_raw']=='chol'
    assert r['physical_leaves']==sorted({re.match(r'f(\d+)',u['page'])[1] for u in s['units']},key=int)
    initial=json.loads((H/'artifacts/INITIAL_ACCOUNTING_RESULT.json').read_text());assert {k:v for k,v in initial.items() if k!='physical_leaves'}=={k:v for k,v in r.items() if k!='physical_leaves'}
    assert not r['source_specific_803_package_tested'] and r['confirmed_words']==0 and r['independent_confirmation_capacity']==0 and not r['significance']
    result={'status':'PASS','coverage':['frozen primary bytes and model','complete source selection and deduplication','all4986word alignments','all51candidate cases and graph slots','raw ZLchol type counter retained','metadata-only physical-leaf correction'],'meaning_validation':False,'independent_reviewer':False,'limitations':'Same root/data; no native syntax, lexical meaning or GDT388 scored relation validation'}
    (H/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
