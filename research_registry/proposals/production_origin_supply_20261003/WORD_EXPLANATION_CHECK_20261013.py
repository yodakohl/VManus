#!/usr/bin/env python3
"""Source-string integrity and a renaming witness, not a Voynich test."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
p=D/'WORD_EXPLANATION_SOURCE_20261013.json';s=json.loads(p.read_text())
x=s['primary_passage']['literal_expanded_operation'];a=x['source'];b=x['result'];i=x['one_based_position']-1
assert a=='precadium' and b=='precarium'
assert len(a)==len(b)==9 and [(j+1,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v]==[(6,'d','r')]
assert a[i]==x['replace'] and b[i]==x['with'] and a[:i]+x['with']+a[i+1:]==b
assert b[1]==b[5]=='r'
# A fixed injective synthetic renaming preserves the relation exactly.
letters=sorted(set(a+b));pi={c:chr(65+j) for j,c in enumerate(letters)}
encode=lambda w:''.join(pi[c] for c in w)
u,v=encode(a),encode(b)
assert u[:i]+pi[x['with']]+u[i+1:]==v
assert u[i]==pi[x['replace']] and v[1]==v[5]
assert 'R pro D littera commutata' in s['primary_passage']['complete_paragraph_transcription']
# Normalized Latin strings cannot silently stand in for different raw witness strings.
assert 'precadiu'!=a and 'prece adium'.replace(' ','')!=a
out={'status':'PASS_SOURCE_RELATION_AND_LIMITATION_ONLY','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'expanded_source':a,'expanded_result':b,'changed_position':6,'preexisting_result_letter_position':2,
 'renaming_witness':{'map':pi,'source':u,'result':v,'letter_replaced':pi['d'],'replacement':pi['r']},
 'proof':'Any bijection pi transports each letter occurrence and the named replacement consistently; hence position-specific substitution and renaming commute. Repeated headwords remain repeated. This does not identify the actual source alphabet.',
 'witness_versions_not_collapsed':True,'native_data_read':False,
 'scope':'The expanded online reading is checked; uncertain print abbreviation and the alternative prece adium are not repaired. Neither this equation nor synthetic renaming establishes any Voynich word or code.'}
(D/'WORD_EXPLANATION_VALIDATION_20261013.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
