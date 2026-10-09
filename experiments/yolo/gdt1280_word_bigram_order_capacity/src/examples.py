"""Post-result same-page illustrations; no new scoring or meaning."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 lock=json.loads((B/'artifacts/POSTRESULT_EXAMPLES_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 out={}
 for reader in ['ZL3b','IT2a','RF1b']:
  data=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_EVALUATION_{reader}.json').read_text());rows=[x for x in data['lines'] if x['metadata']['locus'] in ['f102v2.31','f102v2.39']];assert len(rows)==2
  for row in rows:
   target='chekeey' if row['metadata']['locus'].endswith('.31') else 'cheekey';found=[g for g in row['groups'] if g[2]==target];assert len(found)==1 and found[0][3:5]==['DEFINITE_SPACE','DEFINITE_SPACE']
  out[reader]=rows
 (B/'artifacts/POSTRESULT_RAW_EXAMPLES.json').write_text(json.dumps({'scope':'Post-result manual same-page illustrations selected from complete attestedfibre census;no newtestorwordmeaning','readings':out},indent=2)+'\n')
 print('PASS:6rawlines;6exacttargetgroupswithdefiniteouterseams')
if __name__=='__main__':main()
