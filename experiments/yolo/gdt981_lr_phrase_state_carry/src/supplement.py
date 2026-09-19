"""Post-result provenance diagnostics; never change fixed predictions."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

E=Path(__file__).resolve().parents[1]; R=E.parents[2]
sys.path.insert(0,str(R))
from tools.relation_edge_intake import EDGE_COLUMNS

def dump(n,x): (E/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')

chains=json.loads((E/'artifacts/CHAINS.json').read_text())
events={e['id']:e for e in json.loads((E/'artifacts/EVENTS.json').read_text())}
packet=[];seen=set()
for c in chains:
    a,b=events[c['previous']],events[c['next']]
    pair=(a['locus']+'@G'+str(a['word_index']+1),b['locus']+'@G'+str(b['word_index']+1))
    if pair in seen: continue
    seen.add(pair)
    row={k:'NONE' for k in EDGE_COLUMNS}
    row.update(edge_id='G981.'+str(len(packet)+1),batch_id='GDT981',page=a['page'],
        physical_folio='f'+str(a['leaf']),diagram_unit_id='paragraph',
        pivot_visual_id='text-source',target_visual_id='text-target',
        pivot_locus=pair[0],target_locus=pair[1],relation_type='ASSUMED_STATE_CARRY',
        direction_basis='TEXT_ORDER_ASSUMPTION',ownership_basis='PARAGRAPH_CHANNEL_ASSUMPTION',
        geometry_only_selection='FALSE',source_manifest_id='GDT981',
        source_aware_localizer='root',relation_reviewer='root',relation_confidence='HYPOTHETICAL',
        ambiguity_state='UNRESOLVED',formal_access_state='FORMAL_ACCESSED',fold_assignment='NONE',
        eligibility_status='INELIGIBLE_EXPLORATORY_TEXT_RELATION')
    packet.append(row)
with (E/'artifacts/RELATION_PACKET.tsv').open('w') as f:
    w=csv.DictWriter(f,EDGE_COLUMNS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(packet)
check=subprocess.run([str(R/'vmanus-exp'),'check-edge-packet',str(E/'artifacts/RELATION_PACKET.tsv')],cwd=R,text=True,capture_output=True)
dump('EDGE_GATE.json',dict(exit_code=check.returncode,result=json.loads(check.stdout),semantic_score_ready=False))

# These exact loci were chosen after the main result to explain reading coverage.
# This is not an enlarged or repaired fixed test.
wanted={'f17v.12','f17v.18','f42r.20','f42r.21','f75v.39'}
audit=[];inputs=[]
base=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts'
for ed in ['ZL3b','IT2a','RF1b']:
    for phase in ['DISCOVERY','EVALUATION']:
        p=base/f'SOURCE_{phase}_{ed}.json'
        inputs.append(dict(path=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),role='post_result_source_diagnostic'))
        data=json.loads(p.read_text())
        for row in data['lines']:
            if row['metadata']['locus'] not in wanted: continue
            gs=[dict(zip(data['group_columns'],g)) for g in row['groups']]
            audit.append(dict(metadata=row['metadata'],groups=gs))
dump('SOURCE_DIAGNOSTIC.json',dict(post_result=True,score_changes=False,lines=audit))
dump('SUPPLEMENT_INPUTS.json',inputs)
print(json.dumps(dict(edge_rows=len(packet),edge_gate_exit=check.returncode,source_diagnostic_lines=len(audit))))
