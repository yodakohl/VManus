#!/usr/bin/env python3
"""Independent frozen-key mandatory wholeword-precedence audit.

Discovery gates use only candidate keys and their ciphertext. Ground truth
and held data are interpreted only after the 48 discovery decisions are
committed. This retrospective audit cannot change GDT834 selections/results.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

SRC=Path(__file__).resolve().parent
BASE=SRC.parent
ROOT=BASE.parents[2]
PREVIOUS=BASE.parent/'gdt834_role_blind_mixed_control'
ARMS=('BLIND','TYPED')


def check(ok,message):
    if not ok:
        raise ValueError(message)


def obj(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(expected,actual,where='artifact'):
    if isinstance(expected,dict):
        check(isinstance(actual,dict),where+': object required')
        for key,value in expected.items():
            check(key in actual,where+': missing '+key)
            compare(value,actual[key],where+'.'+key)
    elif isinstance(expected,list):
        check(isinstance(actual,list) and len(expected)==len(actual),where+': list size')
        for i,(a,b) in enumerate(zip(expected,actual)):
            compare(a,b,where+'['+str(i)+']')
    else:
        check(expected==actual,where+': value')


def wholeword_precedence(cipher,key):
    # Read only this candidate's own role/output assignments. In particular,
    # no planted word deck, active-role truth, alias map or gold text enters.
    whole={}
    for code,row in key.items():
        check(row['role'] in ('L','S','W') and isinstance(row['output'],str) and bool(row['output']),'Legal nonempty candidate output')
        if row['role']=='W':
            check(row['output'] not in whole,'W-output injection is a prerequisite')
            whole[row['output']]=code
    counts=Counter(tuple(word) for p in cipher['paragraphs'] for word in p['words'])
    check(bool(counts),'Nonempty corpus required for a precedence gate')
    violations=[]
    for atoms,n in sorted(counts.items()):
        check(bool(atoms) and all(code in key for code in atoms),'Complete nonempty source word')
        output=''.join(key[code]['output'] for code in atoms)
        expected=whole.get(output)
        if expected is not None and atoms!=(expected,):
            violations.append({'atoms':list(atoms),'decoded_output':output,'required_wholeword_code':expected,'occurrences':n})
    return {'word_types':len(counts),'word_occurrences':sum(counts.values()),
            'violating_word_types':len(violations),'violating_word_occurrences':sum(row['occurrences'] for row in violations),
            'pass':not violations,'violations':violations}


def canonical_audit(cipher,key):
    audit=wholeword_precedence(cipher,key)
    spellings=defaultdict(list)
    counts=Counter(tuple(word) for p in cipher['paragraphs'] for word in p['words'])
    for atoms,n in sorted(counts.items()):
        rendered=''.join(key[a]['output'] for a in atoms)
        spellings[rendered].append({'atoms':list(atoms),'occurrences':n})
    return {'words':audit['word_occurrences'],'word_types':audit['word_types'],
            'violating_words':audit['violating_word_occurrences'],'violating_types':audit['violating_word_types'],
            'passes_W_precedence':audit['pass'],
            'violations':[{'atoms':r['atoms'],'decoded':r['decoded_output'],'required_W':r['required_wholeword_code'],'occurrences':r['occurrences']} for r in audit['violations']],
            'alias_classes':[{'decoded':output,'spellings':rows} for output,rows in sorted(spellings.items()) if len(rows)>1]}


def load_fixed_discovery(previous=PREVIOUS):
    """The discovery-only stage deliberately has no held/truth path read."""
    lock=obj(previous/'artifacts/FIT_LOCK.json')
    check(sha(previous/'artifacts/FIT_LOCK.json')=='9e91fa0af401d4777e9af6cec9955957d438fc9ee0909b2e1e4785e385eec872','Unchanged GDT834 fit lock')
    expected={f'artifacts/fits/world_{w}_{a}_start{s}.json' for w in (83401,83402,83403) for a in ARMS for s in range(8)}
    check(set(lock['restarts'])==expected and len(lock['restarts'])==48,'Complete 48-restart discovery inventory')
    fits={}; ciphers={}
    for relative in sorted(expected):
        check(sha(previous/relative)==lock['sha256'][relative],'Frozen restart bytes')
        fit=obj(previous/relative)
        world,arm=fit['world_id'],fit['arm']
        check(relative==f'artifacts/fits/world_{world}_{arm}_start{fit["start"]}.json','Exact fit identity')
        check(fit['schema']=='GDT834_FIT_V1','Original fit schema')
        key=(world,arm)
        if key not in ciphers:
            path=previous/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}discovery.json'
            cipher=obj(path)
            check(cipher['split']=='discovery' and cipher['world_id']==world,'Discovery-only packet')
            ciphers[key]=cipher
        check(fit['input_hashes']['cipher_sha256']==sha(previous/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}discovery.json'),'Original fit input binding')
        fits[relative]=fit
    return fits,ciphers


def verify_registration(base,section):
    reg=obj(base/'src/PREREG_LOCK.json')
    for name,digest in reg['code_sha256'].items():
        path=(base/name).resolve()
        check(path.is_relative_to(base.resolve()) and sha(path)==digest,'Registered audit code')
    for name,digest in reg[section].items():
        path=(ROOT/name).resolve()
        check(path.is_relative_to(ROOT) and sha(path)==digest,'Registered stage-specific input')


def discovery_stage(base,previous):
    verify_registration(base,'discovery_input_sha256')
    spec=obj(base/'src/SPEC.json')
    check(spec['world_ids']==[83401,83402,83403] and spec['arms']==list(ARMS) and spec['starts']==list(range(8)),'Fixed complete candidate panel')
    fits,ciphers=load_fixed_discovery(previous)
    # Independently recreate every row using no ground-truth interpretation.
    rows=[]
    for relative,fit in fits.items():
        world,arm=fit['world_id'],fit['arm']
        path=previous/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}discovery.json'
        rows.append({'fit_path':relative,'world_id':world,'arm':arm,'start':fit['start'],
                     'key_sha256':sha(previous/relative),'discovery_cipher_sha256':sha(path),
                     'audit':canonical_audit(ciphers[world,arm],fit['key'])})
    expected={'schema':'GDT835_DISCOVERY_GATE_V1','status':'DISCOVERY_GATE_COMPLETE','rows':rows,'keys':len(rows),
              'compatible_keys':sum(row['audit']['passes_W_precedence'] for row in rows),
              'truth_labels_used':False,'held_payload_used':False,'language_model_used':False,'new_key_selection':False,
              'old_fit_lock_sha256':sha(previous/'artifacts/FIT_LOCK.json')}
    compare(expected,obj(base/'artifacts/GATE.json'),'Independent discovery gates')
    gate_lock={'schema':'GDT835_GATE_LOCK_V1','gate_sha256':sha(base/'artifacts/GATE.json'),
               'spec_sha256':sha(base/'src/SPEC.json'),'fit_paths':list(fits),
               'fit_sha256':{path:sha(previous/path) for path in fits}}
    check(gate_lock==obj(base/'artifacts/GATE_LOCK.json'),'Complete discovery-stage lock before confirmation')
    return fits,ciphers,rows


def recovery_counts(cipher,gold,key,true_key):
    check([p['paragraph_id'] for p in cipher['paragraphs']]==[p['paragraph_id'] for p in gold],'Original paragraph ordering')
    words=exact=paragraphs=0
    for cp,gp in zip(cipher['paragraphs'],gold):
        check(len(cp['words'])==len(gp['words']),'Original complete word inventory')
        flags=[]
        for atoms,word in zip(cp['words'],gp['words']):
            check(''.join(true_key[a]['output'] for a in atoms)==word,'Exact gold roundtrip')
            predicted=''.join(key[a]['output'] for a in atoms)
            good=predicted==word; flags.append(good); words+=1; exact+=good
        paragraphs+=all(flags)
    return {'words':words,'exact_words':exact,'exact_paragraphs':paragraphs,'paragraphs':len(gold)}


def derive_decision(rows):
    cross=Counter((r['observed_true_role_output_map'],r['discovery_passes_W_precedence']) for r in rows)
    groups=defaultdict(list)
    for row in rows:
        groups[row['world_id'],row['arm']].append(row)
    correct=[r for r in rows if r['observed_true_role_output_map']]
    invariant=bool(correct) and all(r['discovery_passes_W_precedence'] for r in correct)
    separation=all(r['observed_true_role_output_map']==r['discovery_passes_W_precedence'] for r in rows)
    coverage=len(groups)==6 and all(any(r['discovery_passes_W_precedence'] for r in group) for group in groups.values())
    compatible=[r for r in rows if r['discovery_passes_W_precedence']]
    confirmed=all(r['held_audit']['passes_W_precedence'] and r['recovery']['held']['exact_words']==r['recovery']['held']['words'] for r in compatible)
    status='INVARIANT_FAILURE' if not invariant else 'RETROSPECTIVE_PRECEDENCE_SEPARATION_PASS' if separation and coverage and confirmed else 'SEPARATION_NOT_CONFIRMED'
    return {'status':status,'cross_tab':[{'observed_true_map':truth,'discovery_compatible':passing,'keys':cross[truth,passing]} for truth in (False,True) for passing in (False,True)],
            'every_cell_has_compatible_key':coverage,'all_discovery_compatible_keys_confirm_on_held':confirmed}


def confirmation_stage(base,previous,fits,ciphers,gate_rows):
    # Called only after independent reconstruction and verification of the
    # entire GATE_LOCK. Confirmation inputs are deliberately deferred.
    verify_registration(base,'confirmation_input_sha256')
    source=obj(previous/'sealed/source_truth.json')
    prior_result=obj(previous/'artifacts/RESULT.json')
    check(prior_result['status']=='BASELINE_RECOVERY_FAIL','Original scientific outcome remains failed')
    gold={split:[p for p in source['paragraphs'] if p['split']==split] for split in ('discovery','held')}
    truths={world:obj(previous/f'sealed/world_{world}_truth.json') for world in (83401,83402,83403)}
    for truth in truths.values():
        check(truth['paragraphs']==source['paragraphs'],'Common committed original source')
    rows=[]
    for gate in gate_rows:
        relative=gate['fit_path']; fit=fits[relative]; world,arm=fit['world_id'],fit['arm']
        truth=truths[world]
        key=truth['decode_map'] if arm=='BLIND' else {a:{'role':a[0],'output':v} for a,v in truth['typed_decode_map'].items()}
        d=ciphers[world,arm]
        h=obj(previous/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}held.json')
        da={a for p in d['paragraphs'] for word in p['words'] for a in word}
        ha={a for p in h['paragraphs'] for word in p['words'] for a in word}
        check(ha<=da,'No held-only key parameter enters truth classification')
        active=da|ha
        rows.append({'fit_path':relative,'world_id':world,'arm':arm,'start':fit['start'],
                     'discovery_passes_W_precedence':gate['audit']['passes_W_precedence'],
                     'discovery_violating_words':gate['audit']['violating_words'],
                     'observed_true_role_output_map':all(fit['key'][a]==key[a] for a in active),
                     'observed_rules':len(active),'held_audit':canonical_audit(h,fit['key']),
                     'recovery':{split:recovery_counts(cipher,gold[split],fit['key'],key) for split,cipher in [('discovery',d),('held',h)]}})
    expected={'schema':'GDT835_RESULT_V1',**derive_decision(rows),
              'gate_lock_sha256':sha(base/'artifacts/GATE_LOCK.json'),'gate_sha256':sha(base/'artifacts/GATE.json'),
              'condition_rows':rows,'new_key_selection':False,'new_fit_or_language_score':False,
              'gdt834_primary_status':'BASELINE_RECOVERY_FAIL',
              'scope':'retrospective fixed-key panel; mandatory W precedence only, not full inverse or Voynich evidence'}
    compare(expected,obj(base/'artifacts/RESULT.json'),'Independent all-key confirmation and decision')
    return expected


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--previous-dir',type=Path,default=PREVIOUS)
    parser.add_argument('--gate-only',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    # Preserve every frozen candidate and the old primary decision/validation.
    protected=['artifacts/FIT_LOCK.json','artifacts/RESULT.json','artifacts/VALIDATION.json']
    original_hashes={name:sha(args.previous_dir/name) for name in protected}
    fits,ciphers,rows=discovery_stage(args.data_dir,args.previous_dir)
    result={'schema':'GDT835_VALIDATION_V1','status':'VALIDATION_PASS',
            'mode':'DISCOVERY_GATE_ONLY' if args.gate_only else 'DISCOVERY_AND_CONFIRMATION',
            'discovery_candidates_independently_replayed':len(rows),
            'discovery_word_occurrences_checked':sum(r['audit']['words'] for r in rows),
            'discovery_gate_sha256':sha(args.data_dir/'artifacts/GATE.json'),
            'gate_lock_sha256':sha(args.data_dir/'artifacts/GATE_LOCK.json'),
            'truth_or_held_interpreted':not args.gate_only,'new_key_selection':False,
            'language_model_used':False,'voynich_data_accessed':False}
    if not args.gate_only:
        confirmed=confirmation_stage(args.data_dir,args.previous_dir,fits,ciphers,rows)
        result.update(scientific_status=confirmed['status'],
                      held_word_occurrences_checked=sum(r['recovery']['held']['words'] for r in confirmed['condition_rows']),
                      confirmation_candidates_independently_replayed=len(confirmed['condition_rows']),
                      result_sha256=sha(args.data_dir/'artifacts/RESULT.json'))
    check(original_hashes=={name:sha(args.previous_dir/name) for name in protected},'Old primary files remain byte-unchanged')
    old_lock=obj(args.previous_dir/'artifacts/FIT_LOCK.json')
    check(all(sha(args.previous_dir/name)==digest for name,digest in old_lock['sha256'].items()),'All previous fit files remain unchanged')
    result['gdt834_primary_sha256_unchanged']=original_hashes
    target=args.data_dir/'artifacts'/('GATE_VALIDATION.json' if args.gate_only else 'VALIDATION.json')
    encoded=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.check:
        check(target.read_bytes()==encoded,'Independent validation artifact replay')
    else:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(encoded)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
