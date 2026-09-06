#!/usr/bin/env python3
"""Retrospective mandatory-W precedence gate on a frozen candidate panel.

--gate classifies discovery ciphertext using each candidate's own W dictionary.
--evaluate requires its full lock before interpreting held material or truth.
No language score, new key, optimization, or replacement selection is produced.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
OLD=E.parent/'gdt834_role_blind_mixed_control'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,obj,check=False):
    raw=(json.dumps(obj,indent=2,sort_keys=True)+'\n').encode()
    if check:
        if Path(p).read_bytes()!=raw:raise ValueError('artifact replay mismatch '+Path(p).name)
    else:Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_bytes(raw)

def audit_words(paragraphs,key):
    if not key:raise ValueError('empty key')
    wholes={}
    for atom,row in key.items():
        if row['role'] not in ('L','S','W') or not isinstance(row['output'],str) or not row['output']:raise ValueError('invalid key package')
        if row['role']=='W':
            if row['output'] in wholes:raise ValueError('duplicate W output')
            wholes[row['output']]=atom
    counts=Counter()
    for p in paragraphs:
        for word in p['words']:
            if not word:raise ValueError('empty cipher word')
            if any(a not in key for a in word):raise ValueError('unknown cipher atom')
            counts[tuple(word)]+=1
    if not counts:raise ValueError('empty cipher corpus')
    aliases=defaultdict(list);violations=[]
    for atoms,n in sorted(counts.items()):
        decoded=''.join(key[a]['output'] for a in atoms)
        aliases[decoded].append({'atoms':list(atoms),'occurrences':n})
        required=wholes.get(decoded)
        if required is not None and atoms!=(required,):
            violations.append({'atoms':list(atoms),'decoded':decoded,'required_W':required,'occurrences':n})
    return {'words':sum(counts.values()),'word_types':len(counts),'violating_words':sum(r['occurrences'] for r in violations),'violating_types':len(violations),'violations':violations,'alias_classes':[{'decoded':w,'spellings':rows} for w,rows in sorted(aliases.items()) if len(rows)>1],'passes_W_precedence':not violations}

def verify_registration(section):
    reg=read(E/'src/PREREG_LOCK.json')
    for rel,h in reg['code_sha256'].items():
        if sha(E/rel)!=h:raise ValueError('registered code changed '+rel)
    for rel,h in reg[section].items():
        if sha(ROOT/rel)!=h:raise ValueError('registered input changed '+rel)

def fit_paths():
    lock=read(OLD/'artifacts/FIT_LOCK.json')
    spec=read(E/'src/SPEC.json')
    expected={f'artifacts/fits/world_{w}_{a}_start{s}.json' for w in spec['world_ids'] for a in spec['arms'] for s in spec['starts']}
    if set(lock['restarts'])!=expected or len(lock['restarts'])!=48:raise ValueError('frozen panel incomplete')
    for rel in expected:
        if sha(OLD/rel)!=lock['sha256'][rel]:raise ValueError('old fit changed')
    return sorted(expected)

def cipher_path(world,arm,split):return OLD/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}{split}.json'

def gate(check=False):
    verify_registration('discovery_input_sha256');rows=[]
    for rel in fit_paths():
        fit=read(OLD/rel);path=cipher_path(fit['world_id'],fit['arm'],'discovery')
        if not path.name.endswith('_discovery.json'):raise ValueError('discovery path required')
        cipher=read(path)
        if cipher['split']!='discovery':raise ValueError('discovery split required')
        rows.append({'fit_path':rel,'world_id':fit['world_id'],'arm':fit['arm'],'start':fit['start'],'key_sha256':sha(OLD/rel),'discovery_cipher_sha256':sha(path),'audit':audit_words(cipher['paragraphs'],fit['key'])})
    result={'schema':'GDT835_DISCOVERY_GATE_V1','status':'DISCOVERY_GATE_COMPLETE','rows':rows,'keys':len(rows),'compatible_keys':sum(r['audit']['passes_W_precedence'] for r in rows),'truth_labels_used':False,'held_payload_used':False,'language_model_used':False,'new_key_selection':False,'old_fit_lock_sha256':sha(OLD/'artifacts/FIT_LOCK.json')}
    save(E/'artifacts/GATE.json',result,check)
    lock={'schema':'GDT835_GATE_LOCK_V1','gate_sha256':sha(E/'artifacts/GATE.json'),'spec_sha256':sha(E/'src/SPEC.json'),'fit_paths':[r['fit_path'] for r in rows],'fit_sha256':{r['fit_path']:r['key_sha256'] for r in rows}}
    save(E/'artifacts/GATE_LOCK.json',lock,check)
    return result

def evaluate(check=False):
    lock=read(E/'artifacts/GATE_LOCK.json')
    if sha(E/'artifacts/GATE.json')!=lock['gate_sha256'] or sha(E/'src/SPEC.json')!=lock['spec_sha256']:raise ValueError('gate lock changed')
    paths=fit_paths()
    if lock['fit_paths']!=paths:raise ValueError('incomplete gate lock')
    for rel,h in lock['fit_sha256'].items():
        if sha(OLD/rel)!=h:raise ValueError('fit changed after gate')
    verify_registration('confirmation_input_sha256')
    source=read(OLD/'sealed/source_truth.json');gold={split:[p for p in source['paragraphs'] if p['split']==split] for split in ('discovery','held')}
    rows=[];cross=Counter();cells=defaultdict(list)
    for g in read(E/'artifacts/GATE.json')['rows']:
        fit=read(OLD/g['fit_path']);world,arm=fit['world_id'],fit['arm'];truth=read(OLD/f'sealed/world_{world}_truth.json')
        truekey=truth['decode_map'] if arm=='BLIND' else {a:{'role':a[0],'output':v} for a,v in truth['typed_decode_map'].items()}
        d=read(cipher_path(world,arm,'discovery'));h=read(cipher_path(world,arm,'held'))
        active={a for payload in (d,h) for p in payload['paragraphs'] for word in p['words'] for a in word}
        correct=all(fit['key'][a]==truekey[a] for a in active)
        errors={}
        for split,payload in [('discovery',d),('held',h)]:
            if [p['paragraph_id'] for p in payload['paragraphs']]!=[p['paragraph_id'] for p in gold[split]]:raise ValueError('source alignment')
            exact=words=paragraphs=0
            for cipher,p in zip(payload['paragraphs'],gold[split]):
                pred=[''.join(fit['key'][a]['output'] for a in word) for word in cipher['words']]
                if len(pred)!=len(p['words']):raise ValueError('word alignment')
                exact+=sum(a==b for a,b in zip(pred,p['words']));words+=len(pred);paragraphs+=pred==p['words']
            errors[split]={'words':words,'exact_words':exact,'exact_paragraphs':paragraphs,'paragraphs':len(gold[split])}
        held=audit_words(h['paragraphs'],fit['key']);passes=g['audit']['passes_W_precedence']
        row={'fit_path':g['fit_path'],'world_id':world,'arm':arm,'start':fit['start'],'discovery_passes_W_precedence':passes,'discovery_violating_words':g['audit']['violating_words'],'observed_true_role_output_map':correct,'observed_rules':len(active),'held_audit':held,'recovery':errors}
        rows.append(row);cross[(correct,passes)]+=1;cells[(world,arm)].append(row)
    invariant_ok=all(r['discovery_passes_W_precedence'] for r in rows if r['observed_true_role_output_map']) and any(r['observed_true_role_output_map'] for r in rows)
    separation=all(r['discovery_passes_W_precedence']==r['observed_true_role_output_map'] for r in rows)
    cell_coverage=all(any(r['discovery_passes_W_precedence'] for r in rs) for rs in cells.values()) and len(cells)==6
    confirmation=all(r['held_audit']['passes_W_precedence'] and r['recovery']['held']['exact_words']==r['recovery']['held']['words'] for r in rows if r['discovery_passes_W_precedence'])
    status='INVARIANT_FAILURE' if not invariant_ok else 'RETROSPECTIVE_PRECEDENCE_SEPARATION_PASS' if separation and cell_coverage and confirmation else 'SEPARATION_NOT_CONFIRMED'
    out={'schema':'GDT835_RESULT_V1','status':status,'gate_lock_sha256':sha(E/'artifacts/GATE_LOCK.json'),'gate_sha256':sha(E/'artifacts/GATE.json'),'cross_tab':[{'observed_true_map':t,'discovery_compatible':p,'keys':cross[t,p]} for t in (False,True) for p in (False,True)],'every_cell_has_compatible_key':cell_coverage,'all_discovery_compatible_keys_confirm_on_held':confirmation,'condition_rows':rows,'new_key_selection':False,'new_fit_or_language_score':False,'gdt834_primary_status':'BASELINE_RECOVERY_FAIL','scope':'retrospective fixed-key panel; mandatory W precedence only, not full inverse or Voynich evidence'}
    save(E/'artifacts/RESULT.json',out,check);return out

def main():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--gate',action='store_true');mode.add_argument('--evaluate',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
    if args.gate and not args.check and (E/'artifacts/GATE_LOCK.json').exists():raise RuntimeError('refuse overwrite locked classifications')
    out=gate(args.check) if args.gate else evaluate(args.check)
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','condition_rows')},sort_keys=True))
if __name__=='__main__':main()
