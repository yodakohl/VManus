from pathlib import Path
from collections import deque
import csv,hashlib,importlib.util,json,sys
E=Path(__file__).resolve().parents[1];R=E.parents[2];P=R/'experiments/yolo/gdt952_wind_named_reference_network'
MODELS=['LM_ONLY','LR_PHRASE_ONLY','COMBINED']
def load(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parent():
 sys.path.insert(0,str(P/'src'));s=importlib.util.spec_from_file_location('wind_prior',P/'src/run_corrected.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def variants(words,model,lib):
 one={a:b for x in lib['LM'] for a,b in [tuple(x),tuple(reversed(x))]}
 pairs={tuple(a):tuple(b) for x in lib['LR_PHRASE'] for a,b in [(x[0],x[1]),(x[1],x[0])]}
 initial=tuple(words);todo=deque([initial]);seen={initial}
 while todo:
  row=todo.popleft();nexts=[]
  if model in ['LM_ONLY','COMBINED']:
   for j,w in enumerate(row):
    if w in one:nexts.append(row[:j]+(one[w],)+row[j+1:])
  if model in ['LR_PHRASE_ONLY','COMBINED']:
   for j in range(len(row)-1):
    if row[j:j+2] in pairs:nexts.append(row[:j]+pairs[row[j:j+2]]+row[j+2:])
  for v in nexts:
   if v not in seen:seen.add(v);todo.append(v)
  assert len(seen)<=32768,'capacity stop; no partial matching permitted'
 return [list(x) for x in sorted(seen)]
