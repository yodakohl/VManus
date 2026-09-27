#!/usr/bin/env python3
"""Fixed post hoc re-score of GDT623 against GDT1057."""
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
ART=HERE/'artifacts'
SOURCE=ROOT/'experiments/yolo/gdt1057_quality_full_source_orientation/artifacts/RESULT.json'
TARGET=ROOT/'experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/ORIENTATION_FREQUENCY_COMPARISON.tsv'
Q=('hot_dry','hot_moist','cold_dry','cold_moist')

def prob(d):
    total=sum(int(d[k]) for k in Q)+2
    return [(int(d[k])+.5)/total for k in Q]

def main():
    source=json.loads(SOURCE.read_text())
    with TARGET.open(newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
    assert len(rows)==72
    ps=prob(source['source_counts'])
    groups={}
    for row in rows:
        key=(row['scope'],row['mode'])
        tv=sum(abs(a-b) for a,b in zip(ps,prob(row)))/2
        groups.setdefault(key,[]).append(dict(scope=key[0],mode=key[1],assignment_id=row['assignment_id'],target_n=sum(int(row[k]) for k in Q),tv=f'{tv:.6f}'))
    ranked=[]; summary=[]
    for key in sorted(groups):
        group=sorted(groups[key],key=lambda r:(float(r['tv']),r['assignment_id']))
        assert len(group)==8
        for rank,row in enumerate(group,1):row['rank']=rank;ranked.append(row)
        thermal=[r for r in group if r['assignment_id'] in ('KT_THERMAL__K_HOT__CH_DRY','KT_THERMAL__K_COLD__CH_DRY')]
        assert len(thermal)==2
        thermal.sort(key=lambda r:(float(r['tv']),r['assignment_id']))
        summary.append(dict(scope=key[0],mode=key[1],overall_winner=group[0]['assignment_id'],thermal_winner=thermal[0]['assignment_id'],thermal_winner_rank=thermal[0]['rank'],thermal_margin=f'{float(thermal[1]["tv"])-float(thermal[0]["tv"]):.6f}',k_hot_tv=next(r['tv'] for r in thermal if '__K_HOT__' in r['assignment_id']),t_hot_tv=next(r['tv'] for r in thermal if '__K_COLD__' in r['assignment_id'])))
    def write(name,items,fields):
        with (ART/name).open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(items)
    write('ALL_72_RESCORINGS.tsv',ranked,['scope','mode','assignment_id','target_n','tv','rank'])
    write('NINE_CELL_DECISIONS.tsv',summary,list(summary[0]))
    result=dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),target_sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),source_counts=source['source_counts'],cells=summary,status='POSTHOC_SCOPE_DIAGNOSTIC_ZERO_LEXEMES')
    (ART/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cells':len(summary),'thermal_winners':[s['thermal_winner'] for s in summary]}))
if __name__=='__main__':main()
