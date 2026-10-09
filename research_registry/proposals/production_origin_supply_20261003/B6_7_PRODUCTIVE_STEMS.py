#!/usr/bin/env python3
"""One explicit artificial writing lesson. No Voynich input or statistical fit.
Readers use the public grammar only, not the17 source messages or normalization.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
GLYPHS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
# Two-sign roots; ordered by explicit meaning groups, not target frequencies.
ROWS=[
 ('MEAT',0,'Fleisch'),('CATTLE',0,'Rind'),('BLOOD',0,'Blut'),('BROTH',0,'Brühe'),
 ('WILD',0,'Wild- als Artbestimmung'),('POT',0,'Topf'),('COLLEN',0,'Kohle/Glut; Quellwort collenn'),
 ('FORM',0,'Gestalt'),('EGG',0,'Ei'),('BREAD',0,'Brot'),('BALL',0,'Ball/Ballen'),
 ('SPICE',0,'Gewürz'),('SALT_MATERIAL',0,'Salz'),('DISH',0,'Gericht'),
 ('MAKE',2,'machen: Erzeugnis, Herkunft/Zusatzbezug'),('CHOP',1,'hacken: Objekt'),
 ('TAKE',1,'nehmen: Objekt'),('PUT',2,'geben/legen: Objekt, Zielbezug'),
 ('SET',2,'setzen: Objekt, Ortsbezug'),('STIR',1,'rühren: Objekt'),
 ('BECOME',1,'Eintreten/Werden: Zustand'),('BOIL',1,'sieden: Träger'),
 ('POUR',2,'gießen: Objekt, Zielbezug'),('CUT',1,'schneiden: Objekt'),
 ('UNTIL',2,'Tätigkeit bis zum Eintritt einer Bedingung'),('LIKE',2,'Vergleich: Verglichenes, Vergleichsgegenstand'),
 ('JOIN',2,'Koordination von zwei Bestandteilen'),('AFTER',2,'Tätigkeit nach Eintritt einer Bedingung'),
 ('IDENTITY',2,'Identität zweier Angaben'),
]
ROOT_FORMS=[h+v for h in ['k','t','p','f','ch','sh','ckh','cth'] for v in 'aoei']
LEX={n:{'code':ROOT_FORMS[i],'arity':a,'meaning':d} for i,(n,a,d) in enumerate(ROWS)}
ROOT_BACK={v['code']:k for k,v in LEX.items()}
NOUNS={n for n,a,d in ROWS if a==0}
FUSE='IF_WANT AND SO DO GOOD FROM SMALL INDEF IN ON THEN DEF PLURAL HARD WELL NOT EXCESS'.split()
TAG=dict(zip(FUSE,'a o e i n d s r l m k t p f ch sh ckh'.split()))
TAG_BACK={v:k for k,v in TAG.items()}
REF={'ES':['a'],'DEN':['o'],'DIE':['e'],'UNSAID':['n'],
     'DARUNTER':['i','a'],'DARAUS':['i','o'],'DARZU':['i','e'],'DAREIN':['i','i']}
REF_BACK={tuple(v):k for k,v in REF.items()}
BUILD={'ORIGIN':'q','KIND':'r','YOUNG':'n','APPLY':'a','REL':'o'}
BUILD_BACK={v:k for k,v in BUILD.items()}
B_ARITY={'ORIGIN':2,'KIND':2,'YOUNG':1,'APPLY':2,'REL':2}
LETTERS={chr(97+i):[g] for i,g in enumerate('a o e i n d s l m k t p f ch sh ckh cth cph cfh'.split())}
LETTERS.update({chr(116+i):['q',g] for i,g in enumerate('a o e i n d s'.split())})
LETTER_BACK={tuple(v):k for k,v in LETTERS.items()}

def N(name,*kids): return name,tuple(kids)
def from_json(t): return N(t[0],*(from_json(k) for k in t[1]))
def show(t): return t[0]+('('+', '.join(show(k) for k in t[1])+')' if t[1] else '')
def lex(t): return t[0]
def arity(name):
 if name in LEX:return LEX[name]['arity']
 if name in FUSE:return 1
 if name in REF or name.startswith('LIT:'):return 0
 if name.startswith('QUOTE'):
  a=int(name[5:name.index(':')])
  if a not in (0,1,2,3):raise ValueError('Only0-3 arguments for written names')
  return a
 return B_ARITY[name]

def check(t):
 assert len(t[1])==arity(t[0]),t
 for k in t[1]:check(k)

def normalize(t):
 """Public lexical equations, never source-row-dependent choices."""
 name,original=t; kids=tuple(normalize(k) for k in original)
 aliases={
 'BEEF':N('ORIGIN',N('MEAT'),N('CATTLE')),
 'MEAT_BROTH':N('ORIGIN',N('BROTH'),N('MEAT')),
 'WILPRATT':N('KIND',N('MEAT'),N('WILD')),
 'CALF':N('YOUNG',N('CATTLE')),
 'VEIST':N('LIT:veist'),
 'PEFFER':N('KIND',N('DISH'),N('LIT:peffer'))}
 if name in aliases:
  assert not kids;return aliases[name]
 if name in ('SEASON','SALT'):
  return N('APPLY',N('SPICE' if name=='SEASON' else 'SALT_MATERIAL'),kids[0])
 if name in ('CHOP_TO','BOIL_IN'):
  return N('REL',N('CHOP' if name=='CHOP_TO' else 'BOIL',kids[0]),kids[1])
 if name=='VECHT':return N('QUOTE2:vecht',*kids)
 if name=='ABE':return N('QUOTE1:abe',*kids)
 return N(name,*kids)

def tokenize(word):
 out=[]
 while word:
  g=next((g for g in sorted(GLYPHS,key=len,reverse=True) if word.startswith(g)),None)
  if g is None:raise ValueError('Unknown sign')
  out.append(g);word=word[len(g):]
 return out

def literal(s):
 if not s or any(c not in LETTERS for c in s):raise ValueError('Names use a-z')
 return ['l']+[g for c in s for g in LETTERS[c]]+['r']

def noun(t):
 name,kids=t
 if name in NOUNS or name in REF or name.startswith('LIT:'):return not kids
 return name in ('ORIGIN','KIND','YOUNG') and all(noun(k) for k in kids)

def noun_core(t):
 name,kids=t
 if name in LEX:return tokenize(LEX[name]['code'])
 if name in REF:return ['i']+REF[name]
 if name.startswith('LIT:'):return literal(name[4:])
 return [BUILD[name]]+[g for k in kids for g in noun_core(k)]

def core(t):
 name,kids=t
 if noun(t):return noun_core(t),[]
 if name=='APPLY' and noun(kids[0]):return ['a']+noun_core(kids[0]),[kids[1]]
 if name=='REL' and kids[0][0] not in FUSE:
  inner,external=core(kids[0])
  if len(external)==1:return ['o']+inner,[external[0],kids[1]]
 if name in BUILD:return [BUILD[name]],list(kids)
 if name.startswith('QUOTE'):
  n=arity(name);s=name.split(':',1)[1]
  return ['e','aoei'[n]]+literal(s),list(kids)
 if name in LEX:return tokenize(LEX[name]['code']),list(kids)
 raise ValueError('No core rule: '+name)

def write_one(t):
 tags=[]
 while t[0] in TAG:
  tags.append(TAG[t[0]]);t=t[1][0]
 bits,args=core(t)
 word=''.join(bits+(['y']+tags if tags else []))
 return [word]+[w for a in args for w in write_one(a)]

def write(trees):
 rows=[]
 for t in trees:
  check(t);row=write_one(t);row[0]='m'+row[0];rows.append(row)
 return '\n'.join(' '.join(r) for r in rows)

def holes(t):
 return 1 if t is None else sum(holes(k) for k in t[1])

def read_core(gs,pos=0,allow_bare=True):
 """Return a semantic template containing only explicitly pending argument holes."""
 g=gs[pos];pos+=1
 if g=='l':
  letters=[]
  while pos<len(gs) and gs[pos]!='r':
   part=[gs[pos]];pos+=1
   if part[0]=='q':part.append(gs[pos]);pos+=1
   letters.append(LETTER_BACK[tuple(part)])
  if not letters or pos>=len(gs):raise ValueError('Unclosed written name')
  return N('LIT:'+''.join(letters)),pos+1
 if g=='e':
  n='aoei'.index(gs[pos]);pos+=1
  value,pos=read_core(gs,pos,False)
  if not value[0].startswith('LIT:'):raise ValueError('Predicate name must be written')
  return N('QUOTE'+str(n)+':'+value[0][4:],*([None]*n)),pos
 if g=='i':
  flags=[gs[pos]];pos+=1
  if flags[0]=='i':flags.append(gs[pos]);pos+=1
  return N(REF_BACK[tuple(flags)]),pos
 if g in BUILD_BACK:
  name=BUILD_BACK[g]
  if pos==len(gs) or gs[pos]=='y':
   if not allow_bare:raise ValueError('Incomplete inner stem')
   return N(name,*([None]*B_ARITY[name])),pos
  first,pos=read_core(gs,pos,False)
  if name=='REL':
   if holes(first)!=1:raise ValueError('Relation extension needs one argument')
   return N('REL',first,None),pos
  if holes(first) or not noun(first):raise ValueError('Stem component must be complete nominal')
  if name=='APPLY':return N('APPLY',first,None),pos
  if name=='YOUNG':return N('YOUNG',first),pos
  second,pos=read_core(gs,pos,False)
  if holes(second) or not noun(second):raise ValueError('Incomplete nominal compound')
  return N(name,first,second),pos
 code=g+gs[pos];pos+=1
 name=ROOT_BACK[code]
 return N(name,*([None]*arity(name))),pos

def read_word(w):
 gs=tokenize(w);t,pos=read_core(gs)
 if pos<len(gs):
  if gs[pos]!='y' or pos+1==len(gs):raise ValueError('Bad inflection boundary')
  for g in reversed(gs[pos+1:]):t=N(TAG_BACK[g],t)
 return t

def read(text):
 """Independent of input clauses, normalization, source quotes and example lists."""
 rows=[]
 for w in text.split():
  if w.startswith('m'):rows.append([w[1:]])
  elif rows:rows[-1].append(w)
  else:raise ValueError('Missing statement start')
 out=[]
 for row in rows:
  it=iter(row)
  def one():
   template=read_word(next(it))
   def fill(t):return one() if t is None else N(t[0],*(fill(k) for k in t[1]))
   return fill(template)
  t=one()
  try:next(it)
  except StopIteration:pass
  else:raise ValueError('Unused word in statement')
  check(t);out.append(t)
 return out

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 source=json.loads((HERE/'B6_7_MANUAL_SOURCE.json').read_text())
 before=json.loads((HERE/'B6_7_MANUAL_PACKET.json').read_text())
 assert sha(HERE/'B6_7_MANUAL_SOURCE.json')==before['manual_source_sha256']
 trees=[normalize(from_json(c['tree'])) for c in source['clauses']]
 text=write(trees)
 assert read(text)==trees and read(' '.join(text.split()))==trees
 x=N('ES');sied=N('BECOME',N('BOIL',x))
 pairs=[
 (N('UNTIL',N('STIR',x),sied),N('AFTER',N('STIR',x),sied)),
 (N('LIKE',N('FORM'),normalize(N('WILPRATT'))),N('IDENTITY',N('FORM'),normalize(N('WILPRATT')))),
 (normalize(N('NOT',N('EXCESS',N('SALT',N('UNSAID'))))),normalize(N('NOT',N('SALT',N('UNSAID'))))),
 (N('JOIN',N('PLURAL',N('EGG')),N('HARD',N('BREAD'))),N('JOIN',N('HARD',N('PLURAL',N('EGG'))),N('BREAD'))),
 (normalize(N('SEASON',x)),normalize(N('SEASON',N('BEEF')))),
 (normalize(N('NOT',N('EXCESS',N('SALT',x)))),normalize(N('EXCESS',N('NOT',N('SALT',x)))))
 ]
 contrasts=[]
 for a,b in pairs:
  aa,bb=write([a]),write([b])
  assert aa!=bb and read(aa)==[a] and read(bb)==[b]
  contrasts.append({'a':show(a),'b':show(b),'a_written':aa,'b_written':bb})
 calf_meat=N('ORIGIN',N('MEAT'),N('YOUNG',N('CATTLE')))
 examples=[
 ('Kalbsfleisch',calf_meat),('Rinderblut',N('ORIGIN',N('BLOOD'),N('CATTLE'))),
 ('Brühe aus Kalbsfleisch',N('ORIGIN',N('BROTH'),calf_meat)),
 ('Brühe aus Salbei',N('ORIGIN',N('BROTH'),N('LIT:salbei'))),
 ('Versehe Fleisch mit Blut',N('DO',N('APPLY',N('BLOOD'),N('MEAT')))),
 ('Versehe Fleisch nicht mit Blut',N('DO',N('NOT',N('APPLY',N('BLOOD'),N('MEAT')))))]
 ex=[]
 for label,t in examples:
  output=write([t]);assert read(output)==[t]
  ex.append({'meaning':label,'structure':show(t),'written':output})
 words=text.split();count=Counter(words);lengths=[len(tokenize(w)) for w in words]
 table_hash=hashlib.sha256(json.dumps([ROWS,TAG,REF,LETTERS],sort_keys=True).encode()).hexdigest()
 contract=(HERE/'B6_7_PRODUCTIVE_STEMS.md').read_text().split('## Ergebnis\n')[0]
 packet={'status':'PRODUCTIVE_MANUAL_WRITER_COMPLETE_NO_TARGET_FIT_TEST',
  'source_sha256':sha(HERE/'B6_7_MANUAL_SOURCE.json'),'old_packet_sha256':sha(HERE/'B6_7_MANUAL_PACKET.json'),
  'script_sha256':sha(Path(__file__)),'rules_prefix_sha256':hashlib.sha256(contract.encode()).hexdigest(),
  'public_tables_sha256':table_hash,'script_role':'Typesetting and correctness aid, no data-fitted key or new manuscript test',
  'root_count':len(LEX),'inflection_tags':len(TAG),'letter_codes':len(LETTERS),'reference_values':len(REF),
  'construction_heads':BUILD,'literal_heads':['l','e'],'words':len(words),'types':len(count),
  'glyphs':sum(lengths),'mean_glyphs':sum(lengths)/len(lengths),'max_glyphs':max(lengths),
  'length_counts':dict(sorted(Counter(lengths).items())),
  'most_common':count.most_common(10),'top10_count':sum(n for _,n in count.most_common(10)),
  'complete_text':text,'normalized_trees':trees,'normalized_readback':[show(t) for t in read(text)],
  'examples':ex,'contrasts':contrasts,
  'claim_ceiling':'Exact recovery of stipulated, normalized manual content; no independent historical interpretation, no Voynich meaning or statistical fit',
  'previous_s2_bookkeeping':{k:before['systems'][1][k] for k in ['words','types','glyphs']},
  'checks':{'all17_normalized_trees':True,'physical_linebreaks_irrelevant':True,'five_content_pairs_and_one_formal_scope_probe':True,'six_new_compositions_without_new_roots':True}}
 (HERE/'B6_7_PRODUCTIVE_PACKET.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
 doc=['# Vollständige Schreibprobe mit produktiven Stämmen','',
 '**Nur erfundene Codes. Keine Glossen für tatsächliche Voynichwörter.**',
 'Leserregeln und Grenzen: [Bauplan](B6_7_PRODUCTIVE_STEMS.md).',
 'Der Quelltext und seine17 gesetzten Lesarten bleiben in [der alten Quellenfassung](B6_7_MANUAL_SOURCE.json) unverändert.','',
 '## Das gesamte Rezept','', '```text',text,'```','',
 'Ein `m` am Anfang kennzeichnet eine Aussage. Der Umbruch ist zur Kontrolle; er wird nicht benötigt.','',
 '## Vollständige Rücklesung der sichtbaren Schrift','']
 for i,(c,t,line) in enumerate(zip(source['clauses'],read(text),text.splitlines()),1):
  doc += [f'### {i:02d}', '', 'Quelle: '+c['source'], '', '`'+line+'`','',c['reading'],'',
          'Rekonstruierte Struktur: `'+show(t)+'`','']
 doc+=['## Neue Bildungen ohne neue Stammeinträge','', '| Inhalt | Geschriebene Form |','|---|---|']
 doc += [f"| {e['meaning']} | `{e['written']}` |" for e in ex]
 doc+=['','## Vollständige Grundstammtafel','', '| Begriff | Code | Ergänzungen | Bedeutung |','|---|---|---:|---|']
 doc += [f"| {n} | `{LEX[n]['code']}` | {a} | {d} |" for n,a,d in ROWS]
 doc+=['','## Grammatische Zusätze nach y','', '| Aufgabe | Zeichen |','|---|---|']
 doc += [f'| {n} | `{g}` |' for n,g in TAG.items()]
 doc+=['','Die Folge bewahrt den Geltungsbereich außen→innen. DO ist Aufforderung; AND ist und, keine erfundene Zeitrelation. IF_WANT gilt für den folgenden Rezeptabsatz. Die übrigen Bedeutungen stehen in der unveränderten [vorherigen vollständigen Tafel](B6_7_MANUAL_TEXTS.md).',
 '', '## Offene Rückverweise','', '| Form | Schreibweise |','|---|---|']
 doc += [f"| {n} | `i{''.join(g)}` |" for n,g in REF.items()]
 doc+=['','## Buchstabiertafel für unbekannte Namen','', '| Buchstabe | Zeichenfolge |','|---|---|']
 doc += [f"| {n} | `{''.join(g)}` |" for n,g in LETTERS.items()]
 doc+=['','Unbekanntes = `l` + Buchstabierung + `r`. Ein unbekanntes Prädikat beginnt mit `e` und `a/o/e/i` für0/1/2/3 Ergänzungen, dann folgt sein ausgeschriebener Name. Kein verstecktes Wörterbuch ergänzt seine Bedeutung.','',
 '## Bedeutungsgegensätze und eine formale Reihenfolgeprobe','']
 for index,e in enumerate(contrasts):
  if index==5: doc += ['','Die letzte Paarung prüft nur die unterschiedliche Operatorreihenfolge; der Ausdruck Übermaß(Nicht(...)) ist damit nicht als natürliche Rezeptanweisung bestätigt.','']
  doc += ['- `'+e['a_written']+'` → `'+e['a']+'`; `'+e['b_written']+'` → `'+e['b']+'`.']
 (HERE/'B6_7_PRODUCTIVE_TEXT.md').write_text('\n'.join(doc)+'\n')
 print(json.dumps({k:packet[k] for k in ['status','root_count','inflection_tags','words','types','glyphs','mean_glyphs','max_glyphs','length_counts','previous_s2_bookkeeping','checks']},ensure_ascii=False))

if __name__=='__main__':main()
