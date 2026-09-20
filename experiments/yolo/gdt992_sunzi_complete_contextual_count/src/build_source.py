#!/usr/bin/env python3
"""Source-only complete conceptual serialization; no target access."""
import collections,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]

def num(n):
    digits=['DIGIT_'+d for d in str(n)]
    value=digits[0]
    for d in digits[1:]:value=['DECIMAL_APPEND',value,d]
    return value

def grouping(m,r):return ['LEAVES',['GROUP','REF',num(m)],num(r)]
def serial(tree,order):
    if isinstance(tree,str):return [tree]
    children=[a for t in tree[1:] for a in serial(t,order)]
    return [tree[0]]+children if order=='PREFIX' else children+[tree[0]]

raw=[
('S01','今有物',['PRESENT','OBJECTS'],'Introduce objects in the problem situation.'),
('S02','不知其數',['UNKNOWN',['COUNT','REF']],'Their number is unknown; no named knower.'),
('S03','三三數之賸二',grouping(3,2),'Grouping those objects by three leaves two.'),
('S04','五五數之賸三',grouping(5,3),'Grouping the same objects by five leaves three.'),
('S05','七七數之賸二',grouping(7,2),'Grouping the same objects by seven leaves two.'),
('S06','問物幾何',['ASK',['COUNT','OBJECTS']],'Ask how many objects there are.'),
('S07','答曰、二十三',['ANSWER',num(23)],'The answer states twenty-three; no least qualifier.'),
('S08','術曰','METHOD_BEGIN','Introduce the worked method.'),
('S09','三三數之賸二、置一百四十',['WHEN',grouping(3,2),['PLACE',num(140)]],'In the three/remainder-two case, place140.'),
('S10','五五數之賸三、置六十三',['WHEN',grouping(5,3),['PLACE',num(63)]],'In the five/remainder-three case, place63.'),
('S11','七七數之賸二、置三十',['WHEN',grouping(7,2),['PLACE',num(30)]],'In the seven/remainder-two case, place30.'),
('S12','并之、得二百三十三',['RESULT',['COMBINE','REF'],num(233)],'Combine the placed values and obtain233.'),
('S13','以二百一十減之、即得',['DONE',['SUBTRACT',num(210),'REF']],'Subtract210 from the current sum and obtain the answer.'),
('S14','凡','GENERAL_BEGIN','Begin generic rules; do not retain the special object count23.'),
('S15','三三數之賸一、則置七十',['WHEN',grouping(3,1),['PLACE',num(70)]],'In a generic three/remainder-one case, place70.'),
('S16','五五數之賸一、則置二十一',['WHEN',grouping(5,1),['PLACE',num(21)]],'In a generic five/remainder-one case, place21.'),
('S17','七七數之賸一、則置十五',['WHEN',grouping(7,1),['PLACE',num(15)]],'In a generic seven/remainder-one case, place15.'),
('S18','一百六以上、以一百五減之、即得',['WHEN',['AT_LEAST',num(106)],['DONE',['SUBTRACT',num(105),'REF']]],'If the contextually applicable current value is at least106, subtract105 once and obtain a result.')]
clauses=[dict(id=i,source_text=c,tree=t,meaning=g,scope='specific' if j<13 else 'general') for j,(i,c,t,g) in enumerate(raw)]
arities={}
def walk(t):
    a=t if isinstance(t,str) else t[0];arity=0 if isinstance(t,str) else len(t)-1
    assert a not in arities or arities[a]==arity
    arities[a]=arity
    if isinstance(t,list):
        for child in t[1:]:walk(child)
for c in clauses:walk(c['tree'])
streams={}
for order in ['PREFIX','POSTFIX']:
    a=[x for c in clauses for x in serial(c['tree'],order)]
    streams[order]=dict(atoms=a,atom_count=len(a),types=len(set(a)),frequencies=dict(sorted(collections.Counter(a).items())))
source=dict(experiment='GDT992',source_hypothesis='Complete Sunzi unknown-count problem, not identified as a Voynich quotation',
  source_urls=['https://yawnoc.github.io/sun-tzu/iii/26','https://archive.org/download/02094034.cn/02094034.cn.pdf'],
  source_pdf_sha256='a377aadf78f8e61f4dffbe84fb115913dfee8ff229be8a841491791457976e8e',
  owned_edition_html_sha256='53467207d549a770d50a58403cabd702fb590b3809190024d95e07fc808c4910',
  source_policy='Owned modern Chinese edition; source-only native numerical/content check, not a diplomatic character transcription or dated pre1450 witness.',
  clauses=clauses,arities=arities,streams=streams,
  references={'GROUP/COUNT:REF':'problem objects in specific scope; a generic object collection parameter in general scope',
    'COMBINE:REF':'the three placed specific computational terms, as an ordered bundle with order not fixing summation association',
    'SUBTRACT:REF':'specific computed233 in S13; unspecified current numeric quantity x in generic S18',
    'AT_LEAST':'unary condition on the current numeric quantity x; implicit subject is a declared contextual choice'},
  writing_assumptions=['Each primitive has one nonempty globally injective prefix-free code per complete case.',
   'Root codes may pack inside a target group; no code crosses a word seam; every target character is consumed.',
   'Prefix and postfix traversal retain the same frozen child order; clause order is source order.',
   'Canonical modern positional decimal uses digit terminals and binary DECIMAL_APPEND(a,d)=10*a+d. Zero is not a Chinese-written glyph here.',
   'No new actor, smallest-answer clause, hidden product, loop, extra sum or general algorithm is inserted.',
   'METHOD_BEGIN and GENERAL_BEGIN preserve the discourse shifts. Generic conditional clauses are rule templates, not one execution on the specific23.',
   'REF is one shared written atom whose antecedent follows the declared typed operator and section context; not nearest preceding surface word.'],
  remaining_ambiguity=['Object identity and material are unspecified.',
   'Remainder facts alone permit23+105k; explicit answer chooses23 without claiming uniqueness.',
   'A generic current x at least106 maps to x-105 once; no automatic repetition or special23 result.',
   'Semantic renamings preserving this typed arithmetic can share all written predictions.',
   'Decimal rather than Chinese additive numerals and both tree writers are modern hypotheses, not attested Voynich mechanisms.'])
(E/'src/SOURCE.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:{'atoms':v['atom_count'],'types':v['types']} for k,v in streams.items()}))
