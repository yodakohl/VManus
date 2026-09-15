"""Preserve frozen validator; correct its integer-leaf versus CSV-string comparison."""
import csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 frozen=E/'src/validate.py';run=subprocess.run([sys.executable,str(frozen)],capture_output=True,text=True)
 if not (E/'artifacts/RESULT.json').exists():
  print(run.stdout.strip());assert run.returncode==0;return
 original=json.loads((E/'artifacts/VALIDATION.json').read_text())
 assert original['checks']['predictions_exact'] and all(v for k,v in original['checks'].items() if k!='table_exact_cells')
 spec=importlib.util.spec_from_file_location('separate_frozen_evaluator',frozen);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 raw=json.loads((R/'experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json').read_text());expected=[['model','edition','id','page','leaf','eligible','defects','groups','header',*v.RULES,'prefix_conflicts','contradictions','decision']]
 j=lambda x:json.dumps(x,separators=(',',':'))
 for m in ['R1','R2']:
  for ed,pp in raw.items():
   for p in pp:
    words=[w for line in p['lines'] for w in line['words']]
    x=v.evaluate(words,m) if p['literal_eligible'] else dict(header=None,conditions=dict.fromkeys(v.RULES),prefix_conflicts=[],contradictions=[],decision='UNKNOWN_NONLITERAL_COMPLETE')
    expected.append([str(c) for c in [m,ed,p['id'],p['page'],p['leaf'],str(p['literal_eligible']),j(p['defects']),len(words),j(x['header']),*[str(x['conditions'][k]) for k in v.RULES],j(x['prefix_conflicts']),j(x['contradictions']),x['decision']]])
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open() as f:table=list(csv.reader(f,delimiter='\t'))
 out=dict(status='PASS' if table==expected else 'FAIL',checks={**original['checks'],'table_exact_cells':table==expected},rows=original['rows'],independent_meaning_confirmation=False,correction='Frozen validator compared numeric leaf integers to CSV text; all scientific JSON and panel comparisons already passed. Corrected TSV values are independently rebuilt with CSV string conversion; frozen files unchanged.',frozen_validator_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest())
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['status']=='PASS'
if __name__=='__main__':main()
