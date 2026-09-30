#!/usr/bin/env python3
"""Follow-up evaluation of immutable GDT1105 survivors; no decoder."""
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
OLD = ROOT / 'experiments/yolo/gdt1105_dual_temperature_scope'

def read_source():
    rows = list(csv.DictReader(io.StringIO(gzip.decompress((BASE/'artifacts/SOURCE.tsv.gz').read_bytes()).decode()), delimiter='\t'))
    lines = defaultdict(list)
    for r in rows:
        for col in ('source_group_index', 'source_group_count'):
            r[col] = int(r[col])
        lines[(r['edition'], r['page'], r['locus'])].append(r)
    return {'rows': rows, 'lines': [dict(zip(('edition','page','locus'), key), groups=value) for key,value in lines.items()]}

def main():
    lock = json.loads((BASE/'PREREG_LOCK.json').read_text())
    for path,digest in lock['sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
    imported = importlib.util.spec_from_file_location('immutable_scope', OLD/'src/scope_models.py')
    module = importlib.util.module_from_spec(imported)
    imported.loader.exec_module(module)
    spec = json.loads((OLD/'src/MODEL.json').read_text())
    previous = json.loads((OLD/'artifacts/RESULT.json').read_text())
    source = read_source()
    retained = module.runs(source, spec)
    model_ids = previous['survivors']
    models = []
    row_by_id = {r['source_group_id']: r for r in source['rows']}
    for identity in model_ids:
        policy,polarity,mask = identity.split(':')
        model = module.evaluate(retained,spec,int(mask[1:]),polarity,policy)
        for clash in model['contradictions']:
            r = row_by_id[clash['owner']]
            clash.update(page=r['page'], locus=r['locus'], physical_leaf=re.match(r'f\d+',r['page']).group())
        models.append(model)
    (BASE/'artifacts/DETAILS.json.gz').write_bytes(gzip.compress(json.dumps({'models':models}, sort_keys=True).encode(),mtime=0))
    old_models = {m['id']:m for m in previous['models']}
    replay_ids = {r['source_group_id'] for r in source['rows'] if r['page'] in ('f9r','f9v','f50r','f50v')}
    def canonical(claims):
        return sorted(claims,key=lambda c:(c['source'], c['kind']))
    for m in models:
        for key in ('bound_claims','unbound_fields'):
            assert canonical([c for c in m[key] if c['source'] in replay_ids]) == canonical(old_models[m['id']][key])
    bare = []
    for line in source['lines']:
        for i,r in enumerate(line['groups']):
            if r['ivtff_group_raw'] not in ('ky','ty'):
                continue
            bare.append({'source_group_id':r['source_group_id'], 'edition':r['edition'], 'page':r['page'], 'locus':r['locus'],
                'raw':r['ivtff_group_raw'], 'previous':line['groups'][i-1]['ivtff_group_raw'] if i else '',
                'next':line['groups'][i+1]['ivtff_group_raw'] if i+1<len(line['groups']) else '',
                'complete_line_records':json.dumps(line['groups'],sort_keys=True)})
    with (BASE/'artifacts/BARE_CONTEXTS.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(bare[0]),delimiter='\t',lineterminator='\n'); w.writeheader();w.writerows(bare)
    with (BASE/'artifacts/CONTRADICTIONS.tsv').open('w',newline='') as f:
        names=['model','edition','physical_leaf','page','locus','owner','domain','claims']
        w=csv.DictWriter(f,fieldnames=names,delimiter='\t',lineterminator='\n');w.writeheader()
        for m in models:
            for c in m['contradictions']:
                w.writerow(dict(model=m['id'], **{k:c[k] for k in names[1:-1]}, claims=json.dumps(c['claims'],sort_keys=True)))
    summaries=[]
    for m in models:
        bare_bound=[c for c in m['bound_claims'] if c['raw'] in ('ky','ty')]
        bare_unbound=[c for c in m['unbound_fields'] if c['raw'] in ('ky','ty')]
        summaries.append({k:m[k] for k in ('id','ownership','polarity','mask','domains','feature_family','reader_contradictions','survives_all_readers_conditionally')} | {
            'contradictory_owners':len(m['contradictions']), 'contradiction_leaves':sorted({c['physical_leaf'] for c in m['contradictions']}),
            'bound_claims':len(m['bound_claims']), 'unbound_fields':len(m['unbound_fields']),
            'bare_bound_claims':bare_bound, 'bare_unbound_count':len(bare_unbound), 'independent_meaning_confirmation_leaves':0})
    groups=defaultdict(list)
    for m in models:
        signature=json.dumps(canonical(m['bound_claims']+m['unbound_fields']),sort_keys=True)
        groups[signature].append(m['id'])
    result={'status':'ALL_ORIGINAL_SURVIVORS_CONTRADICTED' if all(m['contradictions'] for m in models) else 'CONDITIONAL_SURVIVORS_NO_MEANING_SELECTED',
        'candidate_count':len(models), 'survivors':[m['id'] for m in models if not m['contradictions']], 'models':summaries,
        'full_prediction_groups':list(groups.values()), 'source_groups':len(source['rows']), 'full_lines':len(source['lines']),
        'retained_runs':len(retained), 'bare_counts':dict(Counter(r['edition']+':'+r['raw'] for r in bare)),
        'bare_count':len(bare), 'original_fitting_replay_matches':True, 'confirmed_words':0,
        'independent_meaning_confirmation_leaves':0,'reserved_pages_opened':[], 'semantic_score':None,'significance':None,
        'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'artifacts/SOURCE.tsv.gz',BASE/'artifacts/SOURCE_RECEIPT.json',OLD/'src/MODEL.json',OLD/'src/scope_models.py',OLD/'artifacts/RESULT.json']}}
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    table=['# All sixteen unchanged candidate predictions and observed consequences','',
        'All domains/poles are C0 hypotheses. No independently confirmed meanings. Domains below: bare-y / bare-aiin / wrapped-y / wrapped-aiin. All contradictions and unbound fields are retained in DETAILS.json.gz and CONTRADICTIONS.tsv.','',
        '| Candidate | Predicted ky | Predicted ty | Domains | Clashes (ZL/IT/RF) | Bound bare fields | Unbound fields | Outcome | Independent meaning leaves |',
        '|---|---|---|---|---|---:|---:|---|---:|']
    for m in summaries:
        k='hot' if m['polarity']=='k_hot' else 'cold';t='cold' if k=='hot' else 'hot'
        readers='/'.join(str(m['reader_contradictions'].get(e,0)) for e in ('ZL3b','IT2a','RF1b'))
        table.append('| '+' | '.join([m['id'],m['domains'][0]+' '+k,m['domains'][0]+' '+t,','.join(m['domains']),readers,
            str(len(m['bare_bound_claims'])),str(m['unbound_fields']),'conditional compatible' if m['survives_all_readers_conditionally'] else 'contradicted','0'])+' |')
    table += ['', 'Full claim-equivalence groups (including unbound predictions):', '', *['- '+', '.join(g) for g in result['full_prediction_groups']]]
    (BASE/'artifacts/MODEL_TABLE.md').write_text('\n'.join(table)+'\n')
    print(json.dumps({k:result[k] for k in ('status','source_groups','full_lines','candidate_count','survivors','bare_count','bare_counts')},indent=2))

if __name__=='__main__':
    main()
