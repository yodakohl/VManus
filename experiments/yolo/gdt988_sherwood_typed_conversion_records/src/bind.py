#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
P='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/'
INPUTS=[P+x for x in ('artifacts/PARAGRAPHS.json','PREREGISTRATION.md','REPORT.md')]+['research_registry/proposals/translation_programs_20260912/work/W91/REPORT.md','research_registry/work_batches/ten_hours_20260915/CONTEXTUAL_NOTATION_SOURCE_SUPPLY_20260920.md']
SCIENCE=['DECISION.md','METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/matcher.py','src/run.py','src/validate.py','src/fixtures.py','artifacts/PRE_RUN_FIXTURES.json','artifacts/PRE_RUN_SEMANTICS.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');a=p.parse_args();lock=E/'PREREG_LOCK.json'
 if a.register:
  assert not lock.exists();names=INPUTS+[str((E/x).relative_to(ROOT)) for x in SCIENCE]
  lock.write_text(json.dumps({'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{n:sha(ROOT/n) for n in names}},indent=2)+'\n')
 else:
  for n,h in json.loads(lock.read_text())['files'].items():assert sha(ROOT/n)==h,n
 m=json.loads((E/'experiment.json').read_text());m.update(title='Two complete typed proof-conversion records',question='Can full Fapesmo and Frisesomorum records share a typed code across exposed physical leaves?',status=a.status,dependencies=['GDT928','GDT882','GDT980'],claim_ceiling='Exact consequences of two fixed hypothetical proof serializers; no independently confirmed class names, words, or search significance.',inputs=[dict(path=n,role='fixed_input',sha256=sha(ROOT/n)) for n in INPUTS],outputs=[])
 for f in sorted(E.rglob('*')):
  if f.is_file() and f.name!='experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:m['outputs'].append(dict(path=str(f.relative_to(ROOT)),role='primary_report' if f.name=='REPORT.md' else 'source_or_artifact',sha256=sha(f)))
 v=E/'artifacts/VALIDATION.json'
 if v.exists():m['validation']=dict(artifact=str(v.relative_to(ROOT)),status=json.loads(v.read_text())['status'])
 (E/'experiment.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'status':m['status'],'inputs':len(m['inputs']),'outputs':len(m['outputs'])}))
if __name__=='__main__':main()
