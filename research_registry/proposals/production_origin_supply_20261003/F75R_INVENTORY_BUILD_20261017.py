#!/usr/bin/env python3
"""Unselected whole-paragraph requirement authoring; no decipherment or word values."""
from pathlib import Path
from collections import Counter
import hashlib,json
D=Path(__file__).resolve().parent
R=D.parents[2]
p=R/'experiments/yolo/gdt1386_r771_f75r_fixed_transfer/artifacts/SOURCE.json'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='76ff4e72025f7367d9ded9b408cf94d7f26957f3468da6495cca0d98f5c84915'
source=json.loads(p.read_text());readings=[]
for unit in source['units']:
    cols=unit['group_columns'];ri=cols.index('ivtff_group_raw');si=cols.index('source_group_id')
    slots=[];lines=[]
    for line in unit['lines']:
        m=line['metadata'];assert m['page']=='f75r' and 32<=int(m['locus'].split('.')[1])<=46
        assert len(line['groups'])==int(m['source_group_count'])
        groups=[dict(zip(cols,g)) for g in line['groups']]
        lines.append({'metadata':m,'groups':groups})
        for row in groups:slots.append({'source_group_id':row['source_group_id'],'raw':row['ivtff_group_raw'],'left_separator':row['left_separator'],'right_separator':row['right_separator'],'slot_variable':'x'+str(len(slots)+1),'predicate_meaning':'UNASSIGNED'})
    counts=Counter(s['raw'] for s in slots);assert len({s['source_group_id'] for s in slots})==len(slots)
    row38=next(x for x in lines if x['metadata']['locus']=='f75r.38');words=[x['ivtff_group_raw'] for x in row38['groups']]
    # A canonical item writer emits exactly one contiguous block per injective label.
    # This necessary failure is conditional on that writer, not all inventories.
    a,b=words[0],words[2];assert words[:5]==[a,a,b,b,a] and a!=b
    readings.append({'edition':unit['edition'],'boundary_status':unit['boundary_status'],'lines':lines,'slots':slots,'whole_groups':len(slots),'exact_raw_types':len(counts),'marginal_requirements':dict(sorted(counts.items())),'formula':'EXISTS x1..xN: ALL_DIFFERENT(x1..xN) AND ALL_i UNKNOWN_Q(raw_i)(x_i)','all_different':'AUTHORED_COUNTABLE_UNIT_ASSUMPTION_NOT_OBSERVED','source38':{'raw':words,'marginal_requirements':dict(Counter(words)),'first_five_slots':5,'canonical_one_block_injective_label_writer':'CONTRADICTED_BY_A_A_B_B_A_RETURN','limit':'Exact retained reader equality only; image gives coarse pairwise support, not mathematical signidentity'}})
result={'status':'UNSELECTED_CONDITIONAL_REQUIREMENT_ACCOUNT_NOT_A_WRITING_KEY','source':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'readings':readings,'synthetic_consequences':{'one_unit_satisfying_all_unknown_predicates':{'idempotent_shared_object_assertions':'SATISFIABLE','distinct_requirement_slots_for_N_gt_1':'UNSATISFIABLE'},'N_units_each_satisfying_all_predicates':'SATISFIABLE_FOR_THIS_REQUIREMENT_ACCOUNT','N_minus_one_units_each_satisfying_all_predicates':'UNSATISFIABLE_FOR_THIS_REQUIREMENT_ACCOUNT','local_AABBA_if_disjoint_A_B_categories':{'3A_2B_units':'SATISFIABLE','3A_1B_units':'UNSATISFIABLE'},'all_scope_permutations':'SAME_REQUIREMENT_FORMULA_UP_TO_VARIABLE_RENAMING','limits':'Mathematical consequences of authored semantics; no supplied native stock, membercount, operation, meaning or outcome. Marginals alone do not encode joint matching when categories overlap.'},'confirmed_words':0,'native_meanings_assigned':0,'independent_confirmation':False,'unpaid':['countable units and nonreusable positions','allgroups one semantic type','whole scope demand reading','all unknown predicates and their overlap/alias identities','physical order and productive spelling mechanism']}
(D/'F75R_INVENTORY_READING_20261017.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'readers':[{k:r[k] for k in ['edition','whole_groups','exact_raw_types']} for r in readings],'confirmed_words':0}))
