#!/usr/bin/env python3
"""Independent GDT979 certificate checks; never imports or runs run.py."""
from __future__ import annotations
import argparse, gzip, hashlib, json, time
from pathlib import Path

HERE=Path(__file__).resolve(); EXP=HERE.parents[1]; ROOT=EXP.parents[2]
PARAGRAPHS=ROOT/"experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json"
CASES=EXP/"artifacts/CASES.json.gz"; PAIRS=EXP/"artifacts/PAIRS.json.gz"; ART=EXP/"artifacts"
ATOMS=("L","P","S","OA","OB","OC"); STATES=("A","B","C")
MODELS={"M":{"L":{"A":"B"},"P":{"B":"C"},"S":{"B":"A","C":"A"},"OA":{"A":"A"},"OB":{"B":"B"},"OC":{"C":"C"}},"D":{"L":{"A":"B"},"P":{"B":"A"},"S":{"B":"A","C":"A"},"OA":{"A":"A"},"OB":{"B":"B"},"OC":{"C":"C"}}}
UNKNOWN={"UNKNOWN"}

def load_json(p): return json.loads(p.read_text(encoding="utf-8"))
def load_gz(p):
    with gzip.open(p,"rt",encoding="utf-8") as f:return json.load(f)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def prefix_free(values):
    vals=[v for v in values if v is not None]
    return len(vals)==len(set(vals)) and all(a!=b and not a.startswith(b) and not b.startswith(a) for i,a in enumerate(vals) for b in vals[i+1:])

def transition(model,state,atom): return MODELS[model].get(atom,{}).get(state)

def replay_words(words,key,groups,model):
    """Validate a saved atom grouping, exact group spelling, and state trace."""
    errors=[]
    if not isinstance(words,list) or not isinstance(groups,list) or len(words)!=len(groups): return ["word_group_count"]
    if not isinstance(key,list) or len(key)!=6: return ["key_length"]
    if any(v is not None and (not isinstance(v,str) or not (1<=len(v)<=3) or any(not ('a'<=ch<='z') for ch in v)) for v in key): errors.append("key_value")
    if not prefix_free(key): errors.append("key_not_prefix_free")
    state="A"; seen=[]; atom_count=0
    for word,group in zip(words,groups):
        if not isinstance(word,str) or not isinstance(group,list): errors.append("group_shape"); continue
        if not 1<=len(group)<=3: errors.append("group_atom_limit")
        if len(word)>9: errors.append("group_char_limit")
        rendered=""
        for index in group:
            if not isinstance(index,int) or not 0<=index<6: errors.append("atom_index"); continue
            if key[index] is None: errors.append("null_used_atom"); continue
            rendered+=key[index]; seen.append(index); atom_count+=1
            nxt=transition(model,state,ATOMS[index])
            if nxt is None: errors.append("undefined_transition")
            else: state=nxt
        if rendered!=word: errors.append("group_render_mismatch")
    if not 1<=atom_count<=24: errors.append("account_atom_limit")
    if 0 not in seen: errors.append("missing_L")
    if not seen or seen[-1]!=3 or state!="A": errors.append("final_OA_state")
    return errors

def witness_errors(case,witness):
    if not isinstance(witness,dict): return ["witness_shape"]
    key=witness.get("key"); groups=witness.get("groups")
    words=case.get("words")
    errors=replay_words(words,key,groups,case.get("model"))
    if witness.get("has_p") != (isinstance(groups,list) and any(1 in g for g in groups if isinstance(g,list))): errors.append("has_p")
    return errors

def independent_search(case,node_cap=200000,witness_cap=20000,wall_seconds=5.0):
    """Fresh bounded parser for an EXHAUSTED case; never trusts producer traces."""
    words=case.get("words"); model=case.get("model")
    if not isinstance(words,list) or model not in MODELS: return "VALIDATOR_UNKNOWN_SCHEMA",[]
    started=time.monotonic(); nodes=0; found=[]; capped=False
    def legal_new(value,key,index):
        if not value or len(value)>3 or not value.isascii() or not value.islower(): return False
        vals=[v for i,v in enumerate(key) if v is not None and i!=index]
        return value not in vals and all(not value.startswith(v) and not v.startswith(value) for v in vals)
    def atom_options(word,offset,key,state,group):
        if offset>=len(word) or len(group)>=3: return
        for index,atom in enumerate(ATOMS):
            current=key[index]
            vals=[current] if current is not None else [word[offset:offset+n] for n in range(1,min(3,len(word)-offset)+1)]
            for value in vals:
                if not word.startswith(value,offset): continue
                if current is None and not legal_new(value,key,index): continue
                nxt=transition(model,state,atom)
                if nxt is None: continue
                newkey=list(key); newkey[index]=value
                yield offset+len(value),newkey,nxt,group+[index]
    def groups_at(gi,key,state,seq,total):
        nonlocal nodes,capped
        nodes+=1
        if nodes>node_cap or time.monotonic()-started>wall_seconds or len(found)>=witness_cap:
            capped=True; return
        if gi==len(words):
            flat=[i for group in seq for i in group]
            if total>=1 and total<=24 and 0 in flat and flat[-1]==3 and state=="A":
                item={"key":key,"groups":seq}
                if item not in found: found.append(item)
            return
        word=words[gi]
        if not isinstance(word,str) or not 1<=len(word)<=9: return
        def split(offset,k,s,g):
            nonlocal nodes,capped
            nodes+=1
            if nodes>node_cap or time.monotonic()-started>wall_seconds or len(found)>=witness_cap:
                capped=True; return
            if capped or total+len(g)>24: return
            if len(g)>3: return
            if offset==len(word):
                groups_at(gi+1,k,s,seq+[g],total+len(g)); return
            for no,nk,ns,ng in atom_options(word,offset,k,s,g):
                if capped: break
                split(no,nk,ns,ng)
        split(0,list(key),state,[])
    groups_at(0,[None]*6,"A",[],0)
    if capped: return "VALIDATOR_UNKNOWN_CAP",found
    return ("VALIDATOR_FOUND" if found else "VALIDATOR_EXHAUSTED"),found

def merge_key(a,b):
    if not isinstance(a,list) or not isinstance(b,list) or len(a)!=6 or len(b)!=6:return None
    out=[]
    for x,y in zip(a,b):
        if x is not None and y is not None and x!=y:return None
        out.append(x if x is not None else y)
    return out if prefix_free(out) else None

def source_only():
    key=list('abcdef'); rows=[]
    fixtures=[('valid_M',['ae','bf','cd'],key,[[0,4],[1,5],[2,3]],'M',None),
      ('valid_D',['a','b','d'],key,[[0],[1],[3]],'D',None),
      ('prefix_collision',['a','c','d'],['a','ab','c','d','e','f'],[[0],[2],[3]],'M','key_not_prefix_free'),
      ('undefined',['b','d'],key,[[1],[3]],'M','undefined_transition'),
      ('cross_space',['a','ecd'],key,[[0,4],[2,3]],'M','group_render_mismatch'),
      ('four_atom_group',['aecd'],key,[[0,4,2,3]],'M','group_atom_limit'),
      ('too_many_atoms',['a','c']+['d']*23,key,[[0],[2]]+[[3]]*23,'M','account_atom_limit')]
    for name,words,k,groups,model,want in fixtures:
        errors=replay_words(words,k,groups,model)
        rows.append({'name':name,'expected_error':want,'observed_errors':errors,'pass':not errors if want is None else want in errors})
    lock_errors=check_lock()
    ok=all(x['pass'] for x in rows) and not lock_errors
    return {'status':'PASS_REGISTRATION_ONLY' if ok else 'FAIL_REGISTRATION_ONLY','controls':rows,'lock_errors':lock_errors,'claim_ceiling':'syntactic/state certificate validation only; no target or semantic evidence'}

def check_lock():
    lock=EXP/'PREREG_LOCK.json'
    if not lock.exists():return []
    errors=[]
    for rel,expected in load_json(lock)['files'].items():
        p=ROOT/rel
        if not p.is_file() or digest(p)!=expected:errors.append('lock_hash:'+rel)
    return errors

def source_rows(data):
    out={}
    for reading,ps in data.items():
        for p in ps:out[reading,p['id']]=p
    return out

def source_prediction(p):
    words=[w for line in p['lines'] for w in line['words']]
    ids=[s for line in p['lines'] for s in line['source_ids']]
    unknown=any(not line['anchor_eligible'] and not (len(line['words'])==1 and bool(line['words'][0]) and all('a'<=c<='z' for c in line['words'][0])) for line in p['lines'])
    if unknown:return words,ids,'SOURCE_UNKNOWN',['source_not_fully_literal_with_certain_inner_boundaries']
    predicates=[(len(words)>24,'more_than_24_groups'),(sum(map(len,words))>72,'more_than_72_characters'),(any(len(w)>9 for w in words),'group_longer_than_9'),(len(set(w[0] for w in words))>6,'more_than_6_initial_characters'),(len(set(w[-1] for w in words))>6,'more_than_6_final_characters')]
    reasons=[r for yes,r in predicates if yes]
    return words,ids,'CAPACITY_CONTRADICTION' if reasons else 'SEARCH',reasons

def witness_set(rows):
    return sorted(json.dumps({'key':w['key'],'groups':w['groups']},sort_keys=True,separators=(',',':')) for w in rows)

def full():
    if not (PARAGRAPHS.exists() and CASES.exists() and PAIRS.exists()):return {'status':'PRIMARY_RESULT_MISSING','errors':['required_artifact_missing']}
    import collections,csv
    data=load_json(PARAGRAPHS); pmap=source_rows(data);cases=load_gz(CASES);pairs=load_gz(PAIRS);result=load_json(ART/'RESULT.json');errors=check_lock();limits=[]
    allowed=set(load_json(ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json')['allowed_selectors'])
    keys=[];independent=collections.Counter()
    for c in cases:
        ident=(c['reading'],c['id'],c['model']);keys.append(ident);p=pmap.get(ident[:2])
        if p is None or c['model'] not in MODELS:errors.append(str(ident)+':source_coverage');continue
        if p['page'] not in allowed or p['page'].startswith('f84') or p['page']=='f116v':errors.append(str(ident)+':scope')
        words,ids,expected,reasons=source_prediction(p)
        if len(words)!=p['groups'] or len(words)!=len(ids):errors.append(str(ident)+':source_counts')
        if c['words']!=words or c['source_ids']!=ids or c['page']!=p['page'] or c['leaf']!=p['leaf']:errors.append(str(ident)+':source_bytes')
        if expected!='SEARCH':
            if c['status']!=expected or c['reasons']!=reasons or c['witnesses']:errors.append(str(ident)+':source_capacity_classification')
            continue
        if c['status'] not in ('SAT_COMPLETE','EXHAUSTED','UNKNOWN'):errors.append(str(ident)+':search_status')
        if c['status']=='EXHAUSTED' and c['witnesses']:errors.append(str(ident)+':exhausted_with_witness')
        if c['status']=='SAT_COMPLETE' and not c['witnesses']:errors.append(str(ident)+':sat_without_witness')
        for i,w in enumerate(c['witnesses']):errors.extend(str(ident)+':'+str(i)+':'+e for e in witness_errors(c,w))
        if c['status'] in ('SAT_COMPLETE','EXHAUSTED'):
            status,found=independent_search(c);independent[status]+=1
            if status=='VALIDATOR_UNKNOWN_CAP':limits.append(str(ident)+':independent_search_cap')
            elif witness_set(found)!=witness_set(c['witnesses']):errors.append(str(ident)+':independent_witness_set')
    expected={(r,pid,m) for r,pid in pmap for m in MODELS}
    if len(keys)!=len(set(keys)) or set(keys)!=expected:errors.append('complete_case_coverage')
    panels={};calculated_pairs=[]
    for reading in ['ZL3b','IT2a','RF1b']:
      for model in MODELS:
        rows=[c for c in cases if c['reading']==reading and c['model']==model];name=reading+'/'+model
        panels[name]={'cases':len(rows),'statuses':dict(collections.Counter(c['status'] for c in rows)),'witnesses':sum(len(c['witnesses']) for c in rows)}
        yes=[(c,i,w) for c in rows for i,w in enumerate(c['witnesses']) if w['has_p']]
        no=[(c,i,w) for c in rows for i,w in enumerate(c['witnesses']) if not w['has_p']]
        coverage=result['pair_coverage'][name];total=len(yes)*len(no);n=coverage['comparisons']
        if not 0<=n<=min(total,2000000):errors.append(name+':pair_comparison_count')
        if not coverage.get('wall_capped',False) and n!=min(total,2000000):errors.append(name+':pair_count_without_cap')
        count=0;hits=0
        for a,wi,wa in yes:
          for b,wj,wb in no:
            if count>=n:break
            count+=1
            if a['leaf']==b['leaf']:continue
            key=merge_key(wa['key'],wb['key'])
            if key is None:continue
            completed=list(key)
            for i,v in enumerate(completed):
                if v is None:completed[i]=next(ch for ch in 'abcdefghijklmnopqrstuvwxyz' if all(z is None or z[0]!=ch for z in completed))
            for c,w in [(a,wa),(b,wb)]:
                errors.extend(name+':completion:'+e for e in replay_words(c['words'],completed,w['groups'],model))
            calculated_pairs.append(dict(reading=reading,model=model,a=a['id'],b=b['id'],wi=wi,wj=wj,key=key,completed_key=completed));hits+=1
          if count>=n:break
        expected_cov={'p_paragraph_witnesses':len(yes),'no_p_paragraph_witnesses':len(no),'total_saved_witness_pairs':total,'comparisons':n,'joint_witness_pairs':hits,'wall_capped':coverage.get('wall_capped',False),'status':'NO_PARAGRAPH_CAPACITY' if not rows else 'UNKNOWN_PAIR_CAP' if n<total else 'COMPLETE_SAVED_WITNESSES','case_enumeration_complete':all(c['status']!='UNKNOWN' for c in rows)}
        if coverage!=expected_cov:errors.append(name+':pair_coverage')
    if calculated_pairs!=pairs:errors.append('saved_pair_enumeration')
    if result['panels']!=panels:errors.append('panel_totals')
    if result['source_denominators']!={ed:len(ps) for ed,ps in data.items()}:errors.append('source_denominators')
    unresolved=any(c['status']=='UNKNOWN' for c in cases) or any(v['status']=='UNKNOWN_PAIR_CAP' for v in result['pair_coverage'].values())
    expected_status='HYPOTHETICAL_JOINT_FITS_FOUND' if pairs else 'BOUNDED_SEARCH_UNRESOLVED' if unresolved else 'NO_LITERAL_JOINT_FIT_SOURCE_UNCERTAINTY_RETAINED'
    if result['status']!=expected_status or result['joint_witness_pairs']!=len(pairs):errors.append('result_decision')
    if result['confirmed_words']!=0 or result['independent_confirmation_leaves']!=0 or result['reserve_access'] is not False:errors.append('claim_ceiling')
    table=list(csv.reader((ART/'CASE_TABLE.tsv').open(),delimiter='\t'))
    expected_table=[['reading','paragraph','leaf','model','groups','characters','status','reasons','nodes','witnesses']]
    expected_table += [[str(v) for v in [c['reading'],c['id'],c['leaf'],c['model'],len(c['words']),sum(map(len,c['words'])),c['status'],';'.join(c['reasons']),c['nodes'],len(c['witnesses'])]] for c in cases]
    if table!=expected_table:errors.append('complete_case_table')
    return {'status':'FAIL' if errors else 'LIMITED_INDEPENDENT_ENUMERATION' if limits else 'PASS','case_count':len(cases),'pair_count':len(pairs),'independent_enumerations':dict(independent),'independent_limits':limits,'errors':errors,'claim_ceiling':'Source/capacity, complete saved traces and independent bounded enumeration; no manuscript meaning validation'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-only',action='store_true');ap.add_argument('--full',action='store_true');args=ap.parse_args()
    if args.source_only or not args.full:
        out=source_only();name='SOURCE_VALIDATION.json'
    else:out=full();name='VALIDATION.json'
    ART.mkdir(parents=True,exist_ok=True);(ART/name).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
    return 0 if out['status'] in ('PASS','PASS_REGISTRATION_ONLY') else 1
if __name__=='__main__':raise SystemExit(main())
