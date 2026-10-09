"""Replay the frozen trial in a temporary output directory; never overwrite originals.

The original runner's wall-clock work deadline is an operational guard. Freeze
only that clock for this deterministic verification, retaining its 6000-proposal
limit, all criteria, inputs, seeds and actual monotonic runtime measurement.
"""
from pathlib import Path
import importlib.util,json,tempfile,shutil,hashlib,os
from unittest.mock import patch
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('frozen_replay',D/'src/run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
def scientific(obj):
 obj=json.loads(json.dumps(obj))
 if obj.get('best'):
  search=obj['best']['search'];search.pop('seconds',None)
  for row in search.get('log',[]):row.pop('seconds',None)
 return obj
assert os.environ.get('PYTHONHASHSEED')=='0'
original=json.loads((A/'RESULT.json').read_text())
with tempfile.TemporaryDirectory(prefix='vmanus1195_replay_') as td:
 out=Path(td);shutil.copyfile(A/'REGISTRATION_LOCK.json',out/'REGISTRATION_LOCK.json');r.A=out
 with patch.object(r.time,'time',return_value=1791189600):r.main()
 replay=json.loads((out/'RESULT.json').read_text());assert scientific(replay)==scientific(original),'Frozen scientific decision or parameters differ'
 compared=[]
 for name in ['CAPACITY.json','b4.txt','w1.txt','bs1.txt','gr1.txt']:
  if (A/name).exists():assert (A/name).read_bytes()==(out/name).read_bytes(),name;compared.append(name)
result={'status':'PASS','frozen_scientific_result_exact':True,'byte_identical_artifacts':compared,'original_outputs_overwritten':False,'only_removed_comparison_fields':'elapsed seconds','numpy':r.x.np.__version__,'z3':r.x.z3.get_version_string(),'scope':'Deterministic verification of the recorded failed trial; no new model selection, data or research pass.'};(A/'REPLAY_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
