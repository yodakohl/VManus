#!/usr/bin/env python3
"""Frozen-core argument calls under a newly explicit, bounded binding hypothesis."""
import collections
import hashlib
import importlib.util
import json
import re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
def load(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,data): (E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    lock=load(E/'src/PREREG_LOCK.json')
    for p,h in lock['hashes'].items(): assert sha(E/p)==h,p
    source=load(E/'src/SOURCE.json')
    for b in source['inputs']: assert sha(ROOT/b['path'])==b['sha256'],b['path']
    corepath=ROOT/'experiments/yolo/gdt1137_material_process_type_return/src/core.py'
    spec=importlib.util.spec_from_file_location('frozen1137',corepath);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    predictions=load(E/'src/PREDICTIONS.json')
    def evaluate(word,owner):
        recipe=core.lexical_nominal(word)
        try: product=core.qokedy(recipe,owner);return dict(outcome='ACCEPT',recipe=recipe,product=product,error=None)
        except ValueError as exc:return dict(outcome='REJECT',recipe=recipe,product=None,error=str(exc))
    # Verify the predeclared complete truth table before opening target snapshots.
    truth={w:evaluate(w,'PREDICTION_ONLY') for w in predictions}
    assert all(truth[w]['outcome']==predictions[w]['prediction'] and truth[w]['recipe']['stage']==predictions[w]['stage'] for w in predictions)
    write('PREDICTION_CHECK.json',truth)
    base=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';scope=load(base/'src/SPEC.json')
    assert not any(p.startswith('f84') or p=='f116v' for p in scope['allowed_selectors'])
    cases=[];occurrences=[];panels={};seen=set()
    for edition in ['ZL3b','IT2a','RF1b']:
        den=collections.Counter(); counts=collections.Counter(); leaves=set();badleaves=set()
        for phase in ['DISCOVERY','EVALUATION']:
            data=load(base/'artifacts'/f'SOURCE_{phase}_{edition}.json')
            for line in data['lines']:
                m=line['metadata'];page=m['page'];assert page in scope['partitions'][phase] and page in scope['allowed_selectors'] and not page.startswith('f84') and page!='f116v'
                leaf=int(re.match(r'f(\d+)',page)[1]);den['snapshot_lines']+=1
                if leaf==83:den['development_leaf_lines']+=1;continue
                if m['kind']!='P':den['nonprose_lines']+=1;continue
                den['prose_lines']+=1
                groups=[dict(zip(data['group_columns'],g)) for g in line['groups']]
                for i,left in enumerate(groups):
                    if left['ivtff_group_raw']!='qokedy':continue
                    key=left['source_group_id'];assert key not in seen;seen.add(key)
                    den['qokedy_occurrences']+=1;right=groups[i+1] if i+1<len(groups) else None
                    if right is None: reason='LINE_END'
                    elif int(right['source_group_index'])!=int(left['source_group_index'])+1: reason='INDEX_GAP'
                    elif left['right_separator']!='DEFINITE_SPACE' or right['left_separator']!='DEFINITE_SPACE':reason='UNCERTAIN_SEAM'
                    elif right['ivtff_group_raw'] not in predictions:reason='OUTSIDE_FOUR_LICENSE_DOMAIN'
                    else:reason='ELIGIBLE'
                    den[reason]+=1
                    row=dict(edition=edition,phase=phase,page=page,leaf=leaf,locus=m['locus'],left=left,right=right,classification=reason)
                    occurrences.append(row)
                    if reason!='ELIGIBLE':continue
                    result=evaluate(right['ivtff_group_raw'],key);assert result['outcome']==predictions[right['ivtff_group_raw']]['prediction']
                    case=dict(**row,**result,metadata=m,complete_line_groups=groups);cases.append(case)
                    counts[result['outcome']]+=1;counts[right['ivtff_group_raw']]+=1;leaves.add(leaf)
                    if result['outcome']=='REJECT':badleaves.add(leaf)
        decision='CONTRADICTED_TRANSFER_ASSUMPTION' if counts['REJECT'] else ('COMPATIBLE_IN_FIXED_DOMAIN' if counts['ACCEPT'] else 'NO_CAPACITY')
        panels[edition]=dict(denominators=dict(den),counts=dict(counts),decision=decision,eligible_leaves=sorted(leaves),reject_leaves=sorted(badleaves))
    decision='CONTRADICTED_TRANSFER_ASSUMPTION' if any(c['outcome']=='REJECT' for c in cases) else ('COMPATIBLE_IN_FIXED_DOMAIN' if cases else 'NO_CAPACITY')
    write('OCCURRENCES.json',occurrences);write('CASES.json',cases)
    result=dict(experiment='GDT1146',decision=decision,panels=panels,total_reader_cases=len(cases),unique_eligible_physical_leaves=sorted({c['leaf'] for c in cases}),unique_reject_physical_leaves=sorted({c['leaf'] for c in cases if c['outcome']=='REJECT'}),old1137='UNCHANGED_LOCAL_C0',full876_transfer='NOT_TESTED',confirmed_words=0,independent_meaning_confirmation_capacity=0,significance_claim=False,assumption='Every eligible exact pair binds its immediate right nominal as argument; scope generalization is new.')
    write('RESULT.json',result)
    table=['# All eligible frozen-core argument calls','','Conditional transfer cases, not translations. Entire lines are preserved in CASES.json.','','| Reading | Locus | Left group index | Right form | Core outcome |','|---|---|---:|---|---|']
    table += [f"| {c['edition']} | {c['locus']} | {c['left']['source_group_index']} | {c['right']['ivtff_group_raw']} | {c['outcome']} |" for c in cases]
    (E/'CANDIDATE_TABLE.md').write_text('\n'.join(table)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
