import dataclasses,hashlib,json,re,typing,csv
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 s=json.loads((E/'src/SOURCE.json').read_text());ns={k:getattr(typing,k) for k in ['Dict','List','Tuple','Optional']};ns['dataclass']=dataclasses.dataclass
 for f in ['corpus.py','reference.py','coda_markers.py','corrected_coda.py']:
  exec(compile((E/'src/vendor'/f).read_text(),f,'exec'),ns)
 comp=ns['EVA_VISUAL_COMPONENTS'];lookup={k:','.join(v[x] for x in ['first_stroke','last_stroke','glyph_class']) for k,v in comp.items()}
 modifiers={k:comp[k]['last_stroke'] for k in s['modifiers']};conf={k:'MODIFIER' for k in modifiers}
 table=ns['CodaTable']('documented_fragment',s['coda'],modifiers,conf,15,0,[])
 def decode(x):
  z=ns['decode_token_cvc_v2'](x['token'],s['assignment'],lookup,table)
  parts=[]
  for ch,role in zip(z.eva_chars,z.char_roles):
   value=s['assignment'].get(lookup.get(ch),'?') if role=='SYLLABIC' else s['coda'][modifiers[ch]]
   parts.append(dict(eva=ch,role=role,value=value))
  pattern=''.join('.*' if p['value']=='?' else re.escape(p['value']) for p in parts)
  compatible=re.fullmatch(pattern,x['claimed']) is not None
  return dict(**x,components=parts,decoded=z.decoded_cvc,unknown_count=z.decoded_cvc.count('?'),decision=('COMPATIBLE_UNRESOLVED' if '?' in z.decoded_cvc else 'MATCH') if compatible else 'CONTRADICTION',immutable_prefix=z.decoded_cvc.split('?')[0])
 rows=[decode(x) for x in s['examples']];repro=[decode(x) for x in s['reproduction_cases']]
 baseline=[x['decoded'] for x in rows+repro]
 table.modifier_confidence['e']='AMBIGUOUS';table.eva_modifiers['e']=comp['e']['last_stroke']
 ambiguous=[decode(x)['decoded'] for x in s['examples']+s['reproduction_cases']]
 result=dict(status='PUBLISHED_EXAMPLES_INCONSISTENT' if any(x['decision']=='CONTRADICTION' for x in rows) else 'NO_EXAMPLE_CONTRADICTION',rows=rows,reproduction=repro,contradictions=sum(x['decision']=='CONTRADICTION' for x in rows),matches=sum(x['decision']=='MATCH' for x in rows),all_printed_pairs=len(rows),e_ambiguous_branch_identical=baseline==ambiguous,full_table_available=False,full_passage_tested=False,prior_source_exposure=True,manuscript_corpus_read=False,reserve_access=False,translated_words=0,independent_confirmation_capacity=0)
 (E/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id','paper_folio','eva','paper_output','components','fixed_fragment_output','unknowns','decision'])
  for x in rows:w.writerow([x['id'],x['paper_folio'],x['token'],x['claimed'],' + '.join(p['value'] or 'EMPTY' for p in x['components']),x['decoded'],x['unknown_count'],x['decision']])
 print(json.dumps({k:v for k,v in result.items() if k not in ['rows','reproduction']}))
if __name__=='__main__':main()
