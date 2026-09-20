"""Post-run ground explanation of registered quantity-namespace contradictions.
No new rule or target search; all six numeric-compatible cases are retained.
"""
import collections,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];A=E/'artifacts'
rows=json.loads((A/'PARAGRAPH_CASES.json').read_text());source=json.loads((E/'src/SOURCE.json').read_text());ds=json.loads((A/'JOINT_CASES.json').read_text());proofs=[]
for d in ds:
    a=rows[d['iv15_index']];pred=collections.Counter(source['recipes']['IV15']['atoms']);seen=collections.Counter(a['words']);branches=[]
    for option in d['numeric_options']:
        conflicts=[]
        for role,word in option['values'].items():
            if seen[word]!=pred[role]:conflicts.append(dict(role=role,word=word,predicted_occurrences=pred[role],observed_occurrences=seen[word],word_indices=[i for i,w in enumerate(a['words']) if w==word]))
        assert conflicts
        branches.append(dict(values=option['values'],conflicts=conflicts))
    proofs.append(dict(iv15_index=d['iv15_index'],v19_index=d['v19_index'],iv15_paragraph=a['paragraph'],every_numeric_branch_contradicted=True,branches=branches))
coverage={}
for ed in ['ZL3b','IT2a','RF1b']:
    r=[x for x in rows if x['edition']==ed and x['writer']=='FORWARD' and x['recipe']=='IV15'];literal=[x for x in r if x['status']!='UNKNOWN_SOURCE'];allpairs=sum(a['leaf']!=b['leaf'] for a in literal for b in literal)
    coverage[ed]=dict(paragraphs=len(r),literal_paragraphs=len(literal),source_unknown_paragraphs=len(r)-len(literal),literal_leaves=len({x['leaf'] for x in literal}),literal_different_leaf_ordered_pairs_per_writer=allpairs)
out=dict(status='PASS',kind='post_run_exact_logical_explanation_not_new_test',fixed_rule='Quantity words are distinct reserved whole words; their whole-word multiplicity must equal source quantity-role multiplicity.',complete_joint_cases_explained=len(proofs),cases=proofs,coverage=coverage,no_new_target_access=True,no_rule_changes=True,semantic_confirmation=False)
(A/'SHORT_CONTRADICTIONS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(coverage=coverage,complete_joint_cases_explained=len(proofs)),indent=2))
