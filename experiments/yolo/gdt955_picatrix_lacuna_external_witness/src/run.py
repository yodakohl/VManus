from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
def main():
 spec=json.loads((P/'src/PREDICTION.json').read_text())
 for r in spec['inputs']:
  assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
 epath=P/'src/EVIDENCE.json'
 if not epath.exists(): raise SystemExit('NO_EVIDENCE_RECORDED')
 evidence=json.loads(epath.read_text())
 rows=evidence['witnesses']
 assert rows and all(r['classification'] in spec['classification'] for r in rows)
 usable=[r for r in rows if r['classification']!='UNRESOLVED']
 classes=sorted({r['classification'] for r in usable})
 status='UNRESOLVED' if not classes else classes[0] if len(classes)==1 else 'WITNESS_DISAGREEMENT'
 out={'status':status,'witnesses_consulted':len(rows),'assessable_witnesses':len(usable),'classifications':classes,'confirmed_words':0,'independent_voynich_confirmation_leaves':0,'original_GDT953_unchanged':True,'interpretation_limit':spec['interpretation']}
 (P/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
