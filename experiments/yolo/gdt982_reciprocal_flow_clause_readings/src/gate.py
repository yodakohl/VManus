"""Expose the derived relation's ineligibility; this is not a semantic score."""
import csv,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
sys.path.insert(0,str(R))
from tools.relation_edge_intake import EDGE_COLUMNS
frames=json.loads((E/'artifacts/FRAMES.json').read_text());rows=[]
for frame in frames:
    row={k:'NONE' for k in EDGE_COLUMNS}
    row.update(edge_id='G982.'+frame['id'],batch_id='GDT982',page=frame['locus'].split('.')[0],
        physical_folio='f'+str(frame['leaf']),diagram_unit_id='hypothetical-clause',
        pivot_visual_id='written-left-pair',target_visual_id='written-right-pair',
        pivot_locus=frame['locus']+'@G'+str(frame['index']-1),
        target_locus=frame['locus']+'@G'+str(frame['index']+2),
        relation_type='TEXT_SELECTED_ROUTE_PAIR',direction_basis='TEXT_ORDER_ASSUMPTION',
        ownership_basis='SAME_PORTION_HYPOTHESIS',geometry_only_selection='FALSE',
        source_manifest_id='GDT982',source_aware_localizer='root',relation_reviewer='root',
        relation_confidence='HYPOTHETICAL',ambiguity_state='UNRESOLVED',
        formal_access_state='FORMAL_ACCESSED',fold_assignment='NONE',
        eligibility_status='INELIGIBLE_EXPLORATORY_TEXT_RELATION')
    rows.append(row)
with (E/'artifacts/RELATION_PACKET.tsv').open('w') as f:
    w=csv.DictWriter(f,EDGE_COLUMNS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
result=subprocess.run([str(R/'vmanus-exp'),'check-edge-packet',str(E/'artifacts/RELATION_PACKET.tsv')],cwd=R,text=True,capture_output=True)
out=dict(exit_code=result.returncode,result=json.loads(result.stdout),independent_semantic_capacity=0)
(E/'artifacts/EDGE_GATE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
