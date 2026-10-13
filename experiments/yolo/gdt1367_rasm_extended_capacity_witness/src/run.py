from pathlib import Path
from itertools import product
import hashlib,importlib,io,json,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
OLD=R/'experiments/yolo/gdt1365_rasm_nonfinal_capacity'
REPS=dict(zip('ABCDEFGHKLMORSTW','ابصدعفجهكلمھرسطو'));REPS.update(Q='ق',N='ن')
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 old=json.loads((OLD/'artifacts/RESULT.json').read_text());premises={}
 for reader in ['IT2a','RF1b','ZL3b']:
  p=old['panels'][reader+'_GE2'];alphabet=p['alphabet'];nonfinal=sorted(x['char'] for x in p['characters'] if x['nonfinal_count'])
  assert len(alphabet)==18 and len(nonfinal)==16 and sorted(set(alphabet)-set(nonfinal))==['m','n']
  premises[reader]={'groups':p['groups'],'types':p['types'],'alphabet':alphabet,'nonfinal':nonfinal,'terminal_only':['m','n']}
 assert all(x['nonfinal']==nonfinal and x['alphabet']==alphabet for x in premises.values())
 classes=sorted(set(REPS)-set('QN'));assert len(classes)==16
 mapping=dict(zip(classes,nonfinal));mapping.update(Q='m',N='n',Y='n',J=nonfinal[0]);inverse={mapping[c]:REPS[c] for c in classes};inverse.update(m=REPS['Q'],n=REPS['N'])
 cache=R/'.cache/rasm_arch_source_20261013';checks=json.loads((OLD/'artifacts/SOURCE_CHECK.json').read_text())['source_hashes']
 for f,h in checks.items():assert hashlib.sha256((cache/'rasm_arch'/f).read_bytes()).hexdigest()==h
 sys.path.insert(0,str(cache));mod=importlib.import_module('rasm_arch.rasm_arch');assert Path(mod.__file__).resolve()==(cache/'rasm_arch/rasm_arch.py').resolve()
 def forbidden(*a,**k):raise AssertionError('No resource access')
 mod.files=forbidden
 def convert(s):
  rows=list(mod.rasm_arch(io.StringIO(s)));assert len(rows)==1;return rows[0][1]
 controls=[]
 for c in classes:
  rep=REPS[c]
  for source,expected in [(rep,c),(rep+'ب',c+'B'),('ب'+rep,'B'+c)]:
   rasm=convert(source);assert rasm==expected,(c,source,rasm,expected);controls.append({'class':c,'source':source,'rasm':rasm})
 digest=hashlib.sha256();count=0
 for n in range(1,4):
  for prefix in product(nonfinal,repeat=n-1):
   for last in alphabet:
    target=''.join(prefix)+last;source=''.join(inverse[c] for c in target);rasm=convert(source);assert ''.join(mapping[c] for c in rasm)==target
    digest.update((json.dumps([target,source,rasm],ensure_ascii=False,separators=(',',':'))+'\n').encode());count+=1
 assert count==4914
 out={'status':'EXTENDED_RASM_CONSTRUCTIVE_CAPACITY','mapping':mapping,'representatives':REPS,'premises':premises,'synthetic_cases':count,'roundtrip_sha256':digest.hexdigest(),'representative_controls':controls,'effective_used_classes':18,'retained_extension_classes':19,'declared_full_classes':20}
 (B/'artifacts/RESULT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(count,digest.hexdigest())
if __name__=='__main__':main()
