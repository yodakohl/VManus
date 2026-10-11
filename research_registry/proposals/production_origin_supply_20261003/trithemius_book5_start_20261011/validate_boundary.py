from pathlib import Path
import json
B=Path(__file__).resolve().parent
x=json.loads((B/'BOUNDARY_NOTE.json').read_text());n=sum(len(w) for w in x['source_words_before_boundary']);m=sum(x['cipher_lengths_before_boundary']);assert n==m==24
assert x['next_source_word'][0]==x['aversa_first_column_literal_pair']['source']=='e';pred=x['aversa_first_column_literal_pair']['written'];actual=x['next_cipher_token'][0];assert pred=='u' and actual=='e' and pred!=actual
r={'status':'CANDIDATE_FIRST_BOUNDARY_MISMATCH_RETAINED','source_letters_before_boundary':n,'cipher_letters_before_boundary':m,'position':25,'source':'e','candidate_written':pred,'printed_cipher':actual,'scope':'Informedcount/literal-paircheckonly; neithercompletephaseaccountnorcauseidentified.'};(B/'BOUNDARY_VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
