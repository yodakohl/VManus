import hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=B/'artifacts'
CODE={'A':'0','B':'01','C':'1'}
def encode(source):
 if not source or any(c not in CODE for c in source) or 'AC' in source:raise ValueError('outside the declared source grammar')
 return ''.join(CODE[c] for c in source)
def decode(written):
 if not written or set(written)-set('01'):raise ValueError('outside output alphabet')
 out=[];i=0
 while i<len(written):
  if written[i:i+2]=='01':out.append('B');i+=2
  else:out.append('A' if written[i]=='0' else 'C');i+=1
 return ''.join(out)
def main():
 s=json.loads((B/'src/SPEC.json').read_text());assert hashlib.sha256((R/s['predecessor']).read_bytes()).hexdigest()==s['predecessor_sha256']
 outputs=[];sources=[];rejected=0
 for n in range(1,s['finite_check_output_max_length']+1):
  for bits in itertools.product('01',repeat=n):
   w=''.join(bits);p=decode(w);assert encode(p)==w and 'AC' not in p
   outputs.append({'output':w,'source':p})
 for n in range(1,s['finite_check_source_max_length']+1):
  for letters in itertools.product('ABC',repeat=n):
   p=''.join(letters)
   if 'AC' in p:
    try:encode(p)
    except ValueError:rejected+=1
    else:raise AssertionError('illegal input accepted')
   else:
    w=encode(p);assert decode(w)==p;sources.append({'source':p,'output':w})
 result={'status':'UNIVERSAL_GRAMMAR_RESTRICTED_COVER_CONSTRUCTED','free_collision':{'source1':'B','source2':'AC','output':'01','source2_grammar_legal':False},'finite_output_words':len(outputs),'finite_legal_source_words':len(sources),'finite_illegal_source_words_rejected':rejected,'general_n_entries':'n+1','conditional_22_unit_minimum_entries':23,'native_words_scored':0,'source_corpus_scored':0,'meanings_assigned':0,'ceiling':'Formal coverage and exact inverse on a declared artificial source grammar only. No independent language, natural text or native key recovered.'}
 for name,v in [('OUTPUT_FIXTURES',outputs),('SOURCE_FIXTURES',sources),('RESULT',result)]: (A/(name+'.json')).write_text(json.dumps(v,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
