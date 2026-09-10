#!/usr/bin/env python3
"""Independent mechanical collision certificate; manual Latin audit is separate."""
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
LINES = [
 'vir-tus est il-li sic-cans et fri-gi-da val-de',
 'ter-ti-us a me-di-cis da-tus est gra-dus huic in u-tro-que',
 'hac fu-git ap-po-si-ta sa-cer ig-nis et her-pe-ta mor-dax',
 'et tu-mor ex o-cu-lis tri-tae ca-ta-plas-ma-te ce-dit',
 'ul-ce-ra quae ser-punt co-hi-bet com-bus-ta-que cu-rat',
 'et mul-tum ca-li-dae di-cunt pro-des-se po-da-grae',
]
FEET = [
 'vir-tus|est-il|li-sic|cans-et|fri-gi-da|val-de',
 'ter-ti-us|a-me-di|cis-da-tus|est-gra-dus|huic-in-u|tro-que',
 'hac-fu-git|ap-po-si|ta-sa-cer|ig-nis-et|her-pe-ta|mor-dax',
 'et-tu-mor|ex-o-cu|lis-tri|tae-ca-ta|plas-ma-te|ce-dit',
 'ul-ce-ra|quae-ser|punt-co-hi|bet-com|bus-ta-que|cu-rat',
 'et-mul|tum-ca-li|dae-di|cunt-pro|des-se-po|da-grae',
]
def flat(rows):
 return [x for row in rows for x in row]
def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
def equivalent(a,b):
 return len(a)==len(b) and all((a[i]==a[j])==(b[i]==b[j]) for i in range(len(a)) for j in range(i,len(a)))
def check_key(key,cipher,words):
 return (set(key)==set(flat(cipher)) and len(set(key.values()))==len(key)
         and [[key[c] for c in w] for w in cipher]==words)
def main():
 s=json.loads((E/'src/SPEC.json').read_text())
 r=json.loads((E/'artifacts/RESULT.json').read_text())
 assert [v['syllabified'] for v in s['verses']]==LINES
 assert [v['verse'] for v in s['verses']]==list(range(716,722))
 assert s['channel']==dict(max_symbols=98,injective=True,unit='orthographic syllable',word_boundaries='preserved',verse_boundaries='erased',nulls=False)
 assert s['alternative']['from']==['fri','gi','da'] and s['alternative']['to']==['fer','vi','da']
 assert s['alternative']['word']=='fervida' and s['alternative']['status']=='constructed_not_attested'
 a=[w.split('-') for line in LINES for w in line.split()]
 b=[['fer','vi','da'] if w==['fri','gi','da'] else w[:] for w in a]
 c=r['ciphertext_words']
 assert [len(w) for w in a]==[len(w) for w in b]==[len(w) for w in c]
 assert len(a)==r['words']==43 and len(flat(a))==r['syllables']==92
 assert len(set(flat(a)))==len(set(flat(b)))==len(set(flat(c)))==r['symbol_types']==74
 assert equivalent(flat(a),flat(b)) and equivalent(flat(a),flat(c)) and equivalent(flat(b),flat(c))
 assert check_key(r['key_A'],c,a) and check_key(r['key_B'],c,b)
 assert r['plaintext_A']==' '.join(map(''.join,a)) and r['plaintext_B']==' '.join(map(''.join,b))
 assert [(i,''.join(x),''.join(y)) for i,(x,y) in enumerate(zip(a,b)) if x!=y]==[(5,'frigida','fervida')]
 changes={k:dict(A=v,B=r['key_B'][k]) for k,v in r['key_A'].items() if v!=r['key_B'][k]}
 assert changes==r['changed_entries'] and len(changes)==2
 assert r['verse_end_word_offsets']==[7,16,24,31,37,43]
 assert len(r['scans'])==6
 for n,(line,expected,scan) in enumerate(zip(LINES,FEET,r['scans'])):
  expected=[f.split('-') for f in expected.split('|')]
  assert scan['verse']==716+n
  assert flat(expected)==flat([w.split('-') for w in line.split()])
  for label in ['A','B']:
   feet=scan[label]
   want=[[{'fri':'fer','gi':'vi'}.get(x,x) for x in f] for f in expected] if label=='B' else expected
   assert len(feet)==6 and [f['syllables'] for f in feet]==want
   assert [f['weights'] for f in feet]==[('LSS' if len(f)==3 else 'LL') for f in expected[:5]]+['LX']
   assert feet[4]['weights']=='LSS'
  assert s['verses'][n]['first_five_feet']==''.join('D' if len(f)==3 else 'S' for f in expected[:5])
  assert scan['quantity_notes']==s['verses'][n]['quantity_notes']
 assert 'fourth declension' not in s['verses'][0]['quantity_notes']
 for name in ['same_ciphertext','injective_A','injective_B']:
  assert r[name] is True
 for name in ['all_possible_readings_enumerated','blind_recovery_test_performed','general_verse_boundary_inference_performed','voynich_access','complete_historical_prescription']:
  assert r[name] is False
 assert r['new_voynich_lexemes']==0 and r['distinct_readings_proved_at_least']==2
 assert 'exposed' in s['selection'] and 'not blinded' in s['selection']
 assert 'incomplete historical prescription' in s['edge_limit']
 assert 'not a grammar solver' in r['grammatical_quantity_basis']
 assert r['binding_spec_sha256']==sha(E/'src/SPEC.json')
 # Break one occurrence of a repeated symbol; equality and backdecode must fail.
 bad=[w[:] for w in c]; bad[24][0]=c[0][0]
 assert not equivalent(flat(a),flat(bad)) and not check_key(r['key_A'],bad,a)
 badkey=dict(r['key_A']); badkey[c[0][0]]=r['key_A'][c[0][1]]
 assert not check_key(badkey,c,a)
 paths=['src/SPEC.json','artifacts/RESULT.json','src/INDEPENDENT_AUDIT.md','src/validate.py']
 out=dict(status='PASS',certificate='mechanical_certificate_PASS',latin_basis='manual quantity and grammar audit; not a full Latin constraint solver',words=43,syllables=92,symbol_types=74,unordered_position_pairs_with_diagonal_per_comparison=4278,equality_comparisons=3,complete_key_checks=2,scans_checked=12,negative_checks=2,source_scope='exposed printed six-verse excerpt; no independent PDF reacquisition in this executable',limitations=['constructed B not historical witness','historical prescription continues beyond excerpt','no blind recovery','no Voynich access or identified meaning'],sha256={p:sha(E/p) for p in paths})
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':
 main()
