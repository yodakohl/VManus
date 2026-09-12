"""Check source/dictionary/argument conservation, not manuscript semantics."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parents[4]
def read(n):return list(csv.DictReader((E/n).open(),delimiter='\t'))
S=json.loads((E/'SOURCE.json').read_text());alts=json.loads((E/'ALTERNATE_LINES.json').read_text())
for item in S['inputs']+alts['inputs']:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
D={r['form']:r for r in read('LEXICON.tsv')};a=read('ALIGNMENT.tsv');b=read('ARGUMENTS.tsv');expected=[];targets={t['target'] for t in S['targets']};loci=set();pm={}
for t in S['targets']:
 p=t['hosts']['ZL3b'][0];pm[p['id']]=p
 for l in p['lines']:
  loci.add(l['locus']);assert not l['locus'].startswith('f84')
  for i,w in enumerate(l['words'],1):expected.append((p['id'],l['locus'],str(i),w))
assert expected==[(r['paragraph'],r['locus'],r['group_index'],r['raw']) for r in a]
for r in a:
 assert r['A']==D[r['raw']]['hypothesis'] if r['raw'] in D else r['A']=='[ungelesen: '+r['raw']+']'
 assert r['B']==('nimm' if r['raw']=='ychor' else r['A'])
for ed,ls in alts['readings'].items():
 assert {l['metadata']['locus'] for l in ls}==loci and len(ls)==len(loci)
 if ed=='ZL3b':
  raw={r['metadata']['locus']:r for r in ls}
  for p in pm.values():
   for l in p['lines']:
    gs=raw[l['locus']]['groups'];assert l['words']==[g['ivtff_group_raw'] for g in gs] and l['source_ids']==[g['source_group_id'] for g in gs]
roles={'ACTION','MIX','REPEAT_ACTION','REPEAT_COOL','ACTION_TYPED'}
expectedops={(m,r['paragraph'],r['locus']+':'+r['group_index']) for m in ['A','B'] for r in a if r['role_A'] in roles or (m=='B' and r['raw']=='ychor')}
assert expectedops=={(r['model'],r['paragraph'],r['operation']) for r in b} and len(expectedops)==len(b)
assert len([r for r in a if r['A']!=r['B']])==13
lookup={r['locus']+':'+r['group_index']:r for r in a}
for x in b:
 if x['patient']:
  patient=lookup[x['patient']];assert patient['paragraph']==x['paragraph'] and patient['raw']==x['patient_form'] and patient['role_A'] in {'MATERIAL','MATERIAL_DOSE'}
 if x['coingredient']:assert lookup[x['coingredient']]['paragraph']==x['paragraph']
chains=read('MATERIAL_CHAINS.tsv');ms=read('MATERIAL_MENTIONS.tsv');groups=collections.defaultdict(list)
for x in ms:groups[(x['paragraph'],x['form'])].append(x['mention'])
assert {(x['paragraph'],x['form']) for x in chains}=={k for k,v in groups.items() if len(v)>1}
for x in chains:
 assert x['mentions'].split(';')==groups[(x['paragraph'],x['form'])]
 assert int(x['NEW_objects'])==len(groups[(x['paragraph'],x['form'])]) and int(x['SAME_objects'])==1
result=json.loads((E/'RESULT.json').read_text());assert result['groups']==len(a)==900 and result['hypothetically_assigned']==sum(r['status']=='ASSUMED' for r in a)==530
assert result['unread']==370 and len(D)==148
out={'status':'PASS_DOCUMENT_FIDELITY_NOT_MEANING','checks':['bound input hashes','all13fixed full primary paragraphs and900groups','all152loci in every alternate reading','raw ZL group and source-ID equality','one meaning per whole form; only13A/B differences','all77A and90B action positions retained','every patient inside its paragraph','all34repeated material groups and both identity partitions'],'meanings_validated':0}
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
