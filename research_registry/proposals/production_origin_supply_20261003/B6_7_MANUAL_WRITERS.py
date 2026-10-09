#!/usr/bin/env python3
"""Mechanical typesetting/reading aid for a manual construction, not a target experiment.

No Voynich input, fitted key, hidden source-message decoder or corpus sampler.
The read() function depends only on the public lexicon and writer rules below.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GLYPHS = 'a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
# Name, arity, publicly supplied meaning/argument order. These are INVENTED codes.
ROWS = [
('IF_WANT',1,'Wenn du [1] willst; Bedingung für den folgenden Rezeptabsatz'),
('AND',1,'und [1]; Quellreihenfolge erhalten, keine zusätzlich behauptete zeitliche Relation'),
('SO',1,'so [1]; quellensprachliche Folge-/Anschlussverknüpfung'),
('DO',1,'Aufforderung an den Leser: [1]'),
('MAKE',2,'machen/herstellen: Erzeugnis [1], Herkunft/Zusatzbezug [2]'),
('GOOD',1,'gut: Eigenschaft von [1]'),
('FROM',1,'aus/von [1]'),
('WILPRATT',0,'Quellwort Wildbret; Ziel, Vergleich oder spätere Benennung ergeben sich aus dem Satz, kein neuer Referent'),
('BEEF',0,'Rindfleisch'),
('SMALL',1,'[1] klein ausführen; keine Zahl oder feste Stückgröße'),
('CHOP',1,'[1] hacken'),
('ES',0,'es; ursprünglicher, nicht aufgelöster Rückverweis'),
('TAKE',1,'[1] nehmen'),
('INDEF',1,'ein/eine/einem [1]; unbestimmte Einführung, keine zugesetzte Maßzahl'),
('ORIGIN',2,'[1] von/aus [2]'),
('BLOOD',0,'Blut; sweiß ist im vorhandenen XML als Kalbsblut annotiert'),
('CALF',0,'Kalb'),
('PUT',2,'[1] geben/legen, Zielbezug [2]'),
('DEN',0,'denn als den gelesen; Pronominal-Lesart gesetzt, Antezedent offen; zeitliches denn ist damit nicht mitcodiert'),
('IN',1,'in [1]'),
('POT',0,'Topf/Hafen'),
('SET',2,'[1] setzen, Ortsbezug [2]'),
('ON',1,'auf [1]'),
('COLLEN',0,'Quellwort collenn; Kohle/Glut, keine ergänzte Menge'),
('UNTIL',2,'Tätigkeit [1] bis zum Eintreten der Bedingung [2]'),
('STIR',1,'[1] rühren'),
('BECOME',1,'Eintreten/Werden von [1]'),
('BOIL',1,'[1] siedet'),
('THEN',1,'dann [1]'),
('POUR',2,'[1] gießen, Zielbezug [2]'),
('DEF',1,'das/die bestimmte [1]'),
('MEAT',0,'Fleisch; der ausgeschriebene Nomenbezug wird nicht als neue Portion eingeführt'),
('VECHT',2,'Quellprädikat vecht: [1], Ergänzung [2]; Lesart nimmt an ist plausibel, nicht still eingesetzt'),
('LIKE',2,'[1] wie [2]; Vergleich, keine Identitätsbehauptung; Vergleichsdimension bleibt offen'),
('FORM',0,'Gestalt'),
('CHOP_TO',2,'[1] hacken, mit dem geschriebenen Richtungs-/Mischbezug [2]'),
('JOIN',2,'[1] und [2] als koordinierte Bestandteile'),
('PLURAL',1,'mehrere [1], ohne bestimmte Anzahl'),
('EGG',0,'Ei'),
('HARD',1,'hartes [1]'),
('BREAD',0,'Brot'),
('DARUNTER',0,'darunter; nicht aufgelöster Rückverweis'),
('ABE',1,'[1] ab; Quellpartikel abe bleibt erhalten, keine zusätzliche Handlung erfunden'),
('WELL',1,'[1] gut ausführen'),
('SEASON',1,'[1] würzen'),
('BALL',0,'Ball/Ballen'),
('VEIST',0,'Quellwort veist; wahrscheinlich Faust, keine genaue Maßzahl angenommen'),
('DARAUS',0,'daraus; nicht aufgelöster Rückverweis'),
('BOIL_IN',2,'[1] sieden, Medium-/Ortsbezug [2]; ausdrücklich kein beliebiges Garen'),
('DIE',0,'die; ursprünglicher pluralischer Rückverweis, keine still zugewiesene Identität'),
('MEAT_BROTH',0,'Fleischbrühe'),
('CUT',1,'[1] schneiden'),
('PEFFER',0,'Quellwort peffer; im vorhandenen XML Gericht pfeffer, keine Gewürzmenge oder Zutatenliste'),
('DARZU',0,'dazu; nicht aufgelöster Rückverweis'),
('DAREIN',0,'darein; nicht aufgelöster Rückverweis'),
('NOT',1,'nicht [1]; Verneinung genau dieser Ergänzung'),
('EXCESS',1,'[1] im Übermaß; zusammen mit Salzen: versalzen'),
('SALT',1,'[1] salzen'),
('UNSAID',0,'Objekt in der Quelle nicht ausgesprochen; kein ergänzter Gegenstand'),
# Productive hierarchy and contrasting statements; no message lookup table.
('CATTLE',0,'Rind'), ('BROTH',0,'Brühe'), ('KIND',2,'Grundbegriff [1] mit Artbestimmung [2]'),
('WILD',0,'wild/Wild- als Artbestimmung'),
('AFTER',2,'Tätigkeit [1] nach Eintreten der Bedingung [2]'),
('IDENTITY',2,'[1] ist identisch mit [2]'),
]
HEADS = ['k','t','p','f','ch','sh','ckh','cth']
VOWELS = 'aoei'
TAILS = 'rlnm'
CODES = [h+v+t for h in HEADS for v in VOWELS for t in TAILS]
LEX = {name: {'code': CODES[i], 'arity': arity, 'meaning': meaning}
       for i,(name,arity,meaning) in enumerate(ROWS)}
INVERSE = {v['code']: k for k,v in LEX.items()}
FUSE = 'IF_WANT AND SO DO GOOD FROM SMALL INDEF IN ON THEN DEF PLURAL HARD ABE WELL NOT EXCESS'.split()
MARKS = {name:a+b for name,(a,b) in zip(FUSE,((a,b) for a in 'aoeid' for b in 'aoei'))}
UNMARK = {v:k for k,v in MARKS.items()}
SHORT = dict(zip('AND DO ES INDEF DEF WILPRATT WELL SO'.split(), ['a','o','e','i','l','r','n','m']))
UNSHORT = {v:k for k,v in SHORT.items()}
# Word references, not entity resolution: four independently visible registers.
CATS = {
 'a': {'WILPRATT','BEEF','BLOOD','CALF','POT','COLLEN','MEAT','FORM','EGG','BREAD','BALL','VEIST','MEAT_BROTH','PEFFER','CATTLE','BROTH','WILD'},
 'o': {'ES','DEN','DARUNTER','DARAUS','DIE','DARZU','DAREIN','UNSAID'},
 'e': {'MAKE','CHOP','TAKE','PUT','SET','STIR','BECOME','BOIL','POUR','VECHT','CHOP_TO','SEASON','BOIL_IN','CUT','SALT'},
 'i': set(),
}
CATS['i'] = set(LEX) - set.union(CATS['a'],CATS['o'],CATS['e'])
CATEGORY = {name:cat for cat,names in CATS.items() for name in names}

def N(name,*kids):
    return (name,tuple(kids))

def literal_code(name):
    value=name[4:]
    if not value or not all('a'<=c<='z' for c in value):
        raise ValueError('Open literal names use lower-case ASCII a-z only.')
    return 's'+''.join(VOWELS[(ord(c)-97)//16]+VOWELS[((ord(c)-97)//4)%4]+VOWELS[(ord(c)-97)%4] for c in value)+'d'

def code(name):
    return literal_code(name) if name.startswith('LIT:') else LEX[name]['code']

def uncode(word):
    if word in INVERSE: return INVERSE[word]
    if word.startswith('s') and word.endswith('d'):
        body=word[1:-1]
        if not body or len(body)%3: raise ValueError('Bad literal')
        nums=[16*VOWELS.index(body[i])+4*VOWELS.index(body[i+1])+VOWELS.index(body[i+2]) for i in range(0,len(body),3)]
        if any(n>25 for n in nums): raise ValueError('Bad literal letter')
        return 'LIT:'+''.join(chr(97+n) for n in nums)
    raise ValueError('Unknown root: '+word)

def arity(name): return 0 if name.startswith('LIT:') else LEX[name]['arity']
def check(t):
    name,kids=t
    assert len(kids)==arity(name),(name,len(kids))
    for k in kids: check(k)

def linear(t):
    return [t[0]]+[name for kid in t[1] for name in linear(kid)]

def parse_prefix(names):
    todo=iter(names)
    def one():
        name=next(todo)
        return N(name,*(one() for _ in range(arity(name))))
    tree=one()
    try: next(todo)
    except StopIteration: return tree
    raise ValueError('Extra words')

def num(n):
    if n==0: return 'a'
    out=''
    while n: n,r=divmod(n,4); out=VOWELS[r]+out
    return out

def unnum(s):
    out=0
    for c in s: out=4*out+VOWELS.index(c)
    return out

EXPANSIONS = {
 'BEEF': N('ORIGIN',N('MEAT'),N('CATTLE')),
 'MEAT_BROTH': N('ORIGIN',N('BROTH'),N('MEAT')),
 'WILPRATT': N('KIND',N('MEAT'),N('WILD')),
}

def expand(t):
    return EXPANSIONS.get(t[0],N(t[0],*(expand(k) for k in t[1])))

def fold(t):
    for name,pattern in EXPANSIONS.items():
        if t==pattern: return N(name)
    return N(t[0],*(fold(k) for k in t[1]))

# A public, compositional three-node phrase. Written out in every S10 text.
MACRO = N('WELL',N('SEASON',N('ES')))


def fused(t,inside=False):
    wrappers=[]
    while t[0] in MARKS:
        wrappers.append(MARKS[t[0]])
        t=t[1][0]
    base=code(t[0]); marks=''.join(wrappers)
    if marks:
        if inside:
            h=next(g for g in sorted(GLYPHS,key=len,reverse=True) if base.startswith(g))
            word=h+'q'+marks+'q'+base[len(h):]
        else: word=base+'q'+marks
    else: word=base
    return [word]+[w for kid in t[1] for w in fused(kid,inside)]


def unfused(words,inside=False):
    it=iter(words)
    def one():
        w=next(it); wrappers=[]
        if 'q' in w:
            if inside:
                h,marks,rest=w.split('q'); base=h+rest
            else: base,marks=w.split('q')
            if len(marks)%2: raise ValueError('Bad modifiers')
            wrappers=[UNMARK[marks[i:i+2]] for i in range(0,len(marks),2)]
        else: base=w
        name=uncode(base)
        t=N(name,*(one() for _ in range(arity(name))))
        for outer in reversed(wrappers): t=N(outer,t)
        return t
    tree=one()
    try: next(it)
    except StopIteration: return tree
    raise ValueError('Extra fused words')


def peel(t):
    if t[0]=='IF_WANT': return 'a',t[1][0]
    if t[0]=='AND' and t[1][0][0]=='DO': return 'o',t[1][0][1][0]
    if t[0]=='SO' and t[1][0][0]=='DO': return 'e',t[1][0][1][0]
    if t[0]=='SO': return 'i',t[1][0]
    return 'd',t

def unpeel(mode,t):
    if mode=='a': return N('IF_WANT',t)
    if mode=='o': return N('AND',N('DO',t))
    if mode=='e': return N('SO',N('DO',t))
    if mode=='i': return N('SO',t)
    if mode=='d': return t
    raise ValueError('Bad clause mode')

def postorder(t):
    return [name for k in t[1] for name in postorder(k)]+[t[0]]

def read_post(names):
    stack=[]
    for name in names:
        n=arity(name)
        if n>len(stack): raise ValueError('Stack underflow')
        kids=stack[-n:] if n else []
        if n: del stack[-n:]
        stack.append(N(name,*kids))
    if len(stack)!=1: raise ValueError('Extra operands')
    return stack[0]


def write(system,trees):
    rows=[]; register={}; previous=[]
    if system==10:
        rows.append(['may']+[code(n) for n in linear(MACRO)])
    for tree in trees:
        check(tree)
        if system in (2,3): words=fused(tree,system==3)
        elif system==4: words=[code(n) for n in linear(expand(tree))]
        elif system==5: words=[SHORT.get(n,code(n)) for n in linear(tree)]
        elif system==6:
            mode,body=peel(tree)
            words=[code(n) for n in linear(body)]
            words[0]+='q'+mode
        elif system==7:
            words=[]
            for name in linear(tree):
                cat=CATEGORY.get(name,'a')
                words.append('y'+cat if register.get(cat)==name else code(name))
                register[cat]=name
        elif system==8:
            current=[code(n) for n in linear(tree)]; keep=0
            while keep<min(len(previous),len(current)) and previous[keep]==current[keep]: keep+=1
            words=['r'+num(keep)+'y']+current[keep:]
            previous=current
        elif system==9:
            words=[code(n) for n in postorder(tree)]
        elif system==10:
            def emit(t):
                return ['ra'] if t==MACRO else [code(t[0])]+[w for k in t[1] for w in emit(k)]
            words=emit(tree)
        else: words=[code(n) for n in linear(tree)]
        if system==9: words[-1]+='y'
        elif system!=8: words[0]+='y'
        rows.append(words)
    return rows


def read(system,text):
    """Read public symbols and rules only; never looks at SOURCE.json or recipe."""
    words=text.split(); rows=[]
    # Initial/final y is an explicit sentence sign attached to a word, not a space.
    if system==9:
        row=[]
        for w in words:
            row.append(w[:-1] if w.endswith('y') else w)
            if w.endswith('y'): rows.append(row); row=[]
        if row: raise ValueError('Missing last sentence ending')
    else:
        for w in words:
            if w.endswith('y'): rows.append([w[:-1]])
            elif not rows: raise ValueError('Missing sentence start')
            else: rows[-1].append(w)
    out=[]; register={}; previous=[]; macros={}
    for row in rows:
        if system in (2,3): tree=unfused(row,system==3)
        elif system==4: tree=fold(parse_prefix([uncode(w) for w in row]))
        elif system==5: tree=parse_prefix([UNSHORT[w] if w in UNSHORT else uncode(w) for w in row])
        elif system==6:
            base,mode=row[0].split('q')
            tree=unpeel(mode,parse_prefix([uncode(base)]+[uncode(w) for w in row[1:]]))
        elif system==7:
            names=[]
            for w in row:
                if w.startswith('y'):
                    name=register[w[1:]]
                else: name=uncode(w)
                register[CATEGORY.get(name,'a')]=name;names.append(name)
            tree=parse_prefix(names)
        elif system==8:
            keep=unnum(row[0][1:])
            if keep>len(previous): raise ValueError('Reference beyond previous sentence')
            current=previous[:keep]+row[1:];previous=current
            tree=parse_prefix([uncode(w) for w in current])
        elif system==9: tree=read_post([uncode(w) for w in row])
        elif system==10:
            if row[0].startswith('m'):
                key='r'+row[0][1:]
                if key in macros: raise ValueError('Redefinition')
                macros[key]=parse_prefix([uncode(w) for w in row[1:]])
                continue
            it=iter(row)
            def one():
                w=next(it)
                if w in macros: return macros[w]
                name=uncode(w);return N(name,*(one() for _ in range(arity(name))))
            tree=one()
            try: next(it)
            except StopIteration: pass
            else: raise ValueError('Extra macro words')
        else: tree=parse_prefix([uncode(w) for w in row])
        check(tree);out.append(tree)
    return out


def glyphs(word):
    out=[]
    while word:
        g=next((g for g in sorted(GLYPHS,key=len,reverse=True) if word.startswith(g)),None)
        if g is None: raise ValueError('Unknown glyph in '+word)
        out.append(g);word=word[len(g):]
    return out


def notation(t):
    return t[0]+('('+', '.join(notation(k) for k in t[1])+')' if t[1] else '')


def from_json(t): return N(t[0],*(from_json(k) for k in t[1]))
def shas(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    src=json.loads((HERE/'B6_7_MANUAL_SOURCE.json').read_text())
    xml_path=ROOT/src['source_file']
    elem=next(e for e in ET.parse(xml_path).getroot().iter() if e.get('{http://www.w3.org/XML/1998/namespace}id')=='b6.7')
    original=' '.join(''.join(elem.itertext()).split())
    quotes=' '.join(c['source'] for c in src['clauses'])
    assert original==quotes, 'Manual source spans do not cover the exact normalized source'
    trees=[from_json(c['tree']) for c in src['clauses']]
    assert len(trees)==17
    packet={'status':'MANUAL_CONSTRUCTION_ONLY_NOT_STATISTICAL_FIT',
            'source_file':src['source_file'],'source_sha256':shas(xml_path),
            'source_unit':'b6.7','source_normalized':original,
            'code_sha256':shas(Path(__file__)), 'manual_source_sha256':shas(HERE/'B6_7_MANUAL_SOURCE.json'),
            'source_coverage':'All normalized source characters covered in order by17 manual spans; no claim of facsimile verification',
            'meaning_ceiling':'Roundtrip reproduces stipulated manual trees, not an independently verified historical reading or original spelling',
            'systems':[]}
    # Small discriminating meaning changes, fixed by hand before running.
    es=N('ES'); boil=N('BECOME',N('BOIL',es))
    contrasts=[
      (N('UNTIL',N('STIR',es),boil), N('AFTER',N('STIR',es),boil)),
      (N('LIKE',N('FORM'),N('WILPRATT')),N('IDENTITY',N('FORM'),N('WILPRATT'))),
      (N('NOT',N('EXCESS',N('SALT',N('UNSAID')))),N('NOT',N('SALT',N('UNSAID')))),
      (N('JOIN',N('PLURAL',N('EGG')),N('HARD',N('BREAD'))),N('JOIN',N('HARD',N('PLURAL',N('EGG'))),N('BREAD'))),
      (N('SEASON',es),N('SEASON',N('BEEF'))),
    ]
    for i in range(1,11):
        rows=write(i,trees); text='\n'.join(' '.join(r) for r in rows)
        assert read(i,text)==trees
        assert read(i,' '.join(text.split()))==trees # physical newlines not hidden syntax
        # Reverse direction for explicit contrasts, shared finite grammar only.
        for a,b in contrasts:
            sa=' '.join(w for r in write(i,[a]) for w in r)
            sb=' '.join(w for r in write(i,[b]) for w in r)
            assert sa!=sb and read(i,sa)==[a] and read(i,sb)==[b]
        unseen=N('TAKE',N('LIT:salbei'))
        unseen_text=' '.join(w for r in write(i,[unseen]) for w in r)
        assert read(i,unseen_text)==[unseen]
        toks=text.split();cnt=Counter(toks)
        packet['systems'].append({'number':i,'rows':rows,'text':text,
            'words':len(toks),'types':len(cnt),'glyphs':sum(len(glyphs(w)) for w in toks),
            'top10_count':sum(v for _,v in cnt.most_common(10)),
            'warning':'Single-recipe bookkeeping only; these counts are NOT comparable to a large Voynich sample',
            'recover_manual_trees':True,'five_content_contrasts_retained':True,'open_literal_salbei_retained':True})
    ranks=lambda n: sorted(Counter(packet['systems'][n-1]['text'].split()).values())
    assert ranks(1)==ranks(5)==ranks(9)
    assert ranks(2)==ranks(3)
    command_count=sum(linear(t).count('DO') for t in trees)
    assert command_count==15
    packet['grammar_consequences']={
        'frequency_partition_equalities':[[1,5,9],[2,3]],
        'clauses':len(trees),'commands':command_count,
        'fixed_control_occurrences':len(trees)+command_count,
        'bound_scope':'C+I control words in <=4 forms (<=6 in7), for1/4/5/7/9 and the selected macro10; conditional on this grammar and source proportions, not a universal manuscript claim',
        'old_GDT1174_largest_top10_ceiling':0.183125,
        'same_source_mood_proportions_min_mean_words_to_avoid_bound':(1+command_count/len(trees))/0.183125,
        'no_new_target_score':True,
        'macro_body_words':3,'macro_calls':2,'macro_definition_words':4,'macro_net_word_saving':0,
        'engineering_ceiling':'Same-author writer/reader; second reader checked source account only.'}
    (HERE/'B6_7_MANUAL_PACKET.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
    table=['# Vollständige künstliche Schreibproben zu b6.7','',
           '5. Oktober 2026. Manuelle Konstruktion, keine Voynich-Übersetzung und keine Statistikbestätigung.',
           'Schlüssel frei erfunden. Gleiche Zeichenfolgen im Manuskript erhalten dadurch keine Bedeutung.',
           'Quelle und Lesart: `B6_7_MANUAL_SOURCE.json`; Regeln und Grenzen: `B6_7_MANUAL_DESIGN.md`.',
           'Die Zeilen unten erleichtern die Kontrolle. Das angehängte `y` markiert den Satzanfang (bei9 das Ende); Umbruch ist frei.',
           '', '## Gemeinsame manuelle Rücklesung','']
    for j,c in enumerate(src['clauses'],1):
        table += [f'### {j:02d}', '', 'Quelle: '+c['source'], '', 'Lesart: '+c['reading'], '', '`'+notation(trees[j-1])+'`','']
    for s in packet['systems']:
        table += [f"## System {s['number']:02d}",'','```text',s['text'],'```','',
                  f"{s['words']} geschriebene Wörter, {s['glyphs']} Arbeitszeichen, {s['types']} Formen. Alle Definitionen mitgezählt.",'']
    table += ['## Vollständige gemeinsame Wurzeltafel','',
      'Keine Wurzel bedeutet einen ganzen Quellsatz. Stelligkeit und Argumentreihenfolge sind Teil des gelernten Schlüssels.',
      'Der Leser braucht diese65 Einträge, die Zusatzregeln seines Systems und für neue Namen die Buchstabentafel. Das ist Lernaufwand, kein kostenloses Wissen.','',
      '| Begriff | Künstliche Wurzel | Ergänzungen | Bedeutung |','|---|---|---:|---|']
    table += [f"| {name} | `{LEX[name]['code']}` | {arity} | {meaning} |" for name,arity,meaning in ROWS]
    table += ['', '## Gebundene Grammatikzeichen für2 und3','',
      'Die Folge läuft vom äußersten zum innersten Zusatz; gelesen wird durch Wiederanlegen in umgekehrter Reihenfolge.','',
      '| Zusatz | Zeichen |','|---|---|']
    table += [f'| {name} | `{marks}` |' for name,marks in MARKS.items()]
    table += ['', '## Kurzformen für5','', '| Begriff | Kurzform |','|---|---|']
    table += [f'| {name} | `{short}` |' for name,short in SHORT.items()]
    table += ['', '## Registerklassen für7','']
    for cat,names in CATS.items(): table += [f'- `{cat}`: '+', '.join(sorted(names))+'.']
    table += ['', '## Buchstabentafel für neue wörtliche Namen','',
      'Nur a–z in dieser Probe. Neues Wort = `s` + Dreiergruppen + `d`; null Ergänzungen.',
      'Das ist ein ausgeschriebener Name in der Beispielsprache, keine Erklärung seiner Eigenschaften.','',
      '| Buchstabe | Gruppe |','|---|---|']
    table += [f'| {chr(97+n)} | `{literal_code("LIT:"+chr(97+n))[1:-1]}` |' for n in range(26)]
    (HERE/'B6_7_MANUAL_TEXTS.md').write_text('\n'.join(table)+'\n')
    print(json.dumps({'clauses':len(trees),'dictionary_entries':len(LEX),'all_manual_trees_recovered':True,
                      'systems':[{'number':s['number'],'words':s['words'],'glyphs':s['glyphs'],'types':s['types']} for s in packet['systems']]},ensure_ascii=False))

if __name__=='__main__': main()
