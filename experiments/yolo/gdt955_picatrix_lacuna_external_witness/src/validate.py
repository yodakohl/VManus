from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
s=json.loads((P/'src/PREDICTION.json').read_text())
checks={r['path']:hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in s['inputs']}
lock=json.loads((P/'PREREG_LOCK.json').read_text())
checks.update({r['path']:hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in lock})
e=P/'src/EVIDENCE.json';r=P/'artifacts/RESULT.json'
if e.exists() and r.exists():
 rows=json.loads(e.read_text())['witnesses'];out=json.loads(r.read_text())
 cs=sorted(set(x['classification'] for x in rows if x['classification']!='UNRESOLVED'))
 checks['recorded_classification']=out['status']==('UNRESOLVED' if not cs else cs[0] if len(cs)==1 else 'WITNESS_DISAGREEMENT')
 checks['all_witnesses']=out['witnesses_consulted']==len(rows) and out['assessable_witnesses']==sum(x['classification']!='UNRESOLVED' for x in rows)
 checks['no_word_claim']=out['confirmed_words']==out['independent_voynich_confirmation_leaves']==0
 checks['source_receipts']=all(x.get('source_url') and x.get('location') and x.get('reason') for x in rows)
 status='PASS' if all(checks.values()) else 'FAIL'
else:status='NOT_RUN'
result={'status':status,'checks':checks,'scope':'Input immutability and recorded-outcome consistency only; does not independently adjudicate source translations.'}
(P/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
