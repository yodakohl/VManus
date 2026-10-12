"""Post-result teaching example, not an independently selected test."""
from pathlib import Path
from fractions import Fraction
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
p=R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='c99fb051dbdd5a2c557f86c0e6eefca7446d467cea48bcab3f4769bda04b2c2e'
source=json.loads(p.read_text());word='machen';inner=word[1:-1];cases=[]
for ref in ['aeiou','aceiou','aeh iou'.replace(' ','')]:
    bits=[c in ref for c in inner];cross=sum(a!=b for a,b in zip(bits,bits[1:]));v=sum(bits);expected=Fraction(2*v*(len(bits)-v),len(bits))
    cases.append({'reference':''.join(sorted(set(ref))),'bits':[int(x) for x in bits],'crossings':cross,'bag_expectation':[expected.numerator,expected.denominator],'excess':[ (Fraction(cross)-expected).numerator,(Fraction(cross)-expected).denominator]})
assert [x['excess'] for x in cases]==[[0,1],[1,2],[1,2]]
counts={}
for book,rows in source.items():
    matches=[{'recipe':r['id'],'count':r['words'].count(word)} for r in rows if word in r['words']]
    counts[book]={'occurrences':sum(x['count'] for x in matches),'first_recipe':matches[0]['recipe'] if matches else None}
out={'selection':'Chosen after results to explain the score, not a prediction or cause estimate.','source_word':word,'trimmed':inner,'scores':cases,'existing_source_counts':counts,'point':'Crossings stay2; moving c or h lowers the same-word bag expectation from2to1.5. No sound value is assigned.'}
(B/'artifacts/POSTRESULT_EXAMPLE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out))
