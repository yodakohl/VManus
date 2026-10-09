"""Ten finite, reversible constructed writing systems. No Voynich word key.

Each message is (operation, plant, part, condition, medium, amount, duration).
Separate records prescribe separate portions; a repeated plant name is not a
claim that the physical portion is unchanged. German labels explain our own
artificial message inventory, not manuscript words or historical prescriptions.
"""
import itertools
import random

SIGNS = ('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f',
         'ch','sh','ckh','cth','cph','cfh')
PLANTS = ('Minze Salbei Thymian Rosmarin Melisse Lavendel Fenchel Anis Kuemmel '
          'Koriander Dill Petersilie Sellerie Liebstoeckel Kamille Schafgarbe '
          'Ringelblume Malve Eibisch Rose Veilchen Schluesselblume Wegerich '
          'Brennnessel Loewenzahn Beifuss Wermut Rainfarn Johanniskraut Baldrian '
          'Hopfen Holunder Linde Birke Weide Eiche Buche Hasel Walnuss Wacholder '
          'Kiefer Fichte Efeu Brombeere Himbeere Erdbeere Heidelbeere Weinrebe '
          'Apfel Birne Pflaume Kirsche Quitte Feige Granatapfel Olive Lorbeer '
          'Myrte Zypresse Aloe Safran Ingwer Pfeffer Zimt').split()
PARTS = ['Blatt','Wurzel','Blüte','Frucht','Samen','Stängel','Rinde','Saft']
STATES = ['frisch','getrocknet','zerkleinert','gemahlen','eingeweicht','ausgepresst','geröstet','gesiebt']
OPS = ['betrachten','zerkleinern','trocknen','einweichen','vermischen','erwärmen','abseihen','aufbewahren']
MEDIA = ['ohne Zusatz','Wasser','Wein','Essig','Öl','Honig','Salzwasser','Quellwasser']
AMOUNTS = ['eine Portion','zwei Portionen','drei Portionen','vier Portionen']
TIMES = ['kurz','bis zum Abend','eine Nacht','mehrere Tage']
FIELD = ['Tätigkeit','Material','Zusatz','Menge','Dauer']
# No target spelling/frequency list enters these definitions.
HEAD = ['d','ch','k','t','sh','s','r','l']
VOWEL = ['a','e','o','ee']
TAIL = ['y','in','l','r']
PREFIX = ['', 'o', 'qo', 'ok', 'ot', 'ol', 'or', 'al',
          'ar', 'ya', 'ye', 'yo', 'da', 'de', 'do', 'sa',
          'se', 'so', 'ra', 're', 'ro', 'la', 'le', 'lo',
          'ka', 'ke', 'ko', 'ta', 'te', 'to', 'sha', 'she']
# 4096 algorithmic head/vowel/tail addresses, not a fitted word dictionary.
ROOTS = list(dict.fromkeys(p+h+v+t for p in PREFIX for h in HEAD for v in VOWEL for t in TAIL))
ROOT_INV = {w:i for i,w in enumerate(ROOTS)}
assert len(ROOTS) == 4096
ROLE = ['qo','d','s','r','l']
END = ['y','dy','in','ol','or']
TAGS = ['q','d','s','r','l']
# Header/control words reserved from each encoder's other branches.
RESET='p'; CLOSE='dy'; DEFINE='ol'; CALL='or'; SAME='y'

def pack(record):
    op, plant, part, state, medium, amount, duration = record
    return (op, plant*64+part*8+state, medium, amount, duration)

def unpack(values):
    op, material, medium, amount, duration = values
    return (op, material//64, (material//8)%8, material%8, medium, amount, duration)

def explanation(r):
    op, plant, part, state, medium, amount, duration = r
    return dict(Tätigkeit=OPS[op], Pflanze=PLANTS[plant], Teil=PARTS[part],
                Zustand=STATES[state], Zusatz=MEDIA[medium],
                Menge=AMOUNTS[amount], Dauer=TIMES[duration])

def source(seed=1174, pages=256, per_page=20):
    """A fixed topical workshop inventory; not a historical control corpus.

    This is a list of hypothetical labelled specimens and tasks on them, not
    a pharmacopoeia or a claim about the contents of the Voynich manuscript.
    """
    rng=random.Random(seed); out=[]
    for p in range(pages):
        plant=p%64; records=[]
        for j in range(per_page):
            # Repeated tasks/parts arise from the same subject of a page.
            weights=[5,4,3,2,2,1,1,1]
            if plant not in {3,5,19,*range(32,59),62,63}:weights[6]=0
            if plant in (39,40,41,58):weights[2]=weights[3]=0
            part=rng.choices(range(8),weights)[0]
            state=rng.choices(range(8),[5,4,3,2,2,1,1,1])[0]
            op=rng.choices(range(8),[2,5,3,3,4,3,2,2])[0]
            medium=0 if op in (0,1,2,7) else rng.choices(range(1,8),[9,3,2,2,1,1,1])[0]
            amount=rng.choices(range(4),[10,4,2,1])[0]
            duration=0 if op in (0,1) else rng.choices(range(4),[5,3,2,1])[0]
            records.append((op,plant,part,state,medium,amount,duration))
        out.append(records)
    return out

def syllables(n):
    """Bijective base 16, one made-up open syllable per digit."""
    digit=[h+v for h in ('d','ch','k','t') for v in ('a','e','o','ee')]
    n+=1; output=[]
    while n:
        n,k=divmod(n-1,16);output.append(digit[k])
    return ''.join(reversed(output))+'y'

SYL=[syllables(n) for n in range(4136)]
SYL_INV={w:i for i,w in enumerate(SYL)}
OFFSETS=[0,8,4104,4112,4116]
CAPS=[8,4096,8,4,4]
assert len(SYL_INV)==len(SYL)

def tagged(field,value): return ROLE[field]+ROOTS[value]+END[field]
TAG_INVERSE={tagged(f,v):(f,v) for f in range(5) for v in range(CAPS[f])}
assert len(TAG_INVERSE)==sum(CAPS)

def infixed(field,value):
    # A template, with one written class infix; no omitted vowels to guess.
    root=ROOTS[value]
    cut=2 if root.startswith(('ch','sh')) else 1
    return root[:cut]+['e','a','o','ee','ii'][field]+root[cut:]+'n'
INF_INVERSE={infixed(f,v):(f,v) for f in range(5) for v in range(CAPS[f])}
assert len(INF_INVERSE)==sum(CAPS)

def field_decode(tokens, inv):
    assert len(tokens)==5
    slots={}
    for token in tokens:
        f,v=inv[token]; assert f not in slots;slots[f]=v
    assert set(slots)==set(range(5))
    return unpack([slots[f] for f in range(5)])

def check_record(r):
    assert len(r)==7 and all(isinstance(x,int) for x in r)
    assert all(0<=x<n for x,n in zip(r,[8,64,8,8,8,4,4]))

def encode(model, records):
    rows=[]
    if model==10:
        # Define a material once on first mention; subsequent calls fill the
        # four remaining arguments. Definitions are included in all statistics.
        templates={}
    previous=None; registers=[None]*5
    for r in records:
        check_record(r); values=pack(r)
        if model==1: # memorised pronounceable lexical roots; dictionary order
            words=[SYL[OFFSETS[f]+v] for f,v in enumerate(values)]
        elif model==2: # transparent case/role endings, productive material stem
            words=[tagged(f,v) for f,v in enumerate(values)]
        elif model==3: # nonconcatenative role marking, same complete stem
            words=[infixed(f,v) for f,v in enumerate(values)]
        elif model==4: # explicit hierarchical classification of specimen
            op,plant,part,state,med,amount,duration=r
            words=[tagged(0,op), 'qo'+ROOTS[plant], 'ch'+ROOTS[part]+'y',
                   'sh'+ROOTS[state]+'y',tagged(2,med),tagged(3,amount),tagged(4,duration)]
        elif model==5: # frequent technical cards plus open spelled identifiers
            # Fixed six high-use values per role, chosen from own source's
            # stated inventory order, never target frequencies.
            words=[]
            for f,v in enumerate(values):
                if v<min(6,CAPS[f]): words.append(ROLE[f]+HEAD[v]+'y')
                else: words.append('qo'+SYL[OFFSETS[f]+v])
        elif model==6: # role recovered from written place, zero case marking
            words=[ROOTS[v] for v in values]
        elif model==7: # last value per typed slot, an explicit anaphor
            words=[]
            for f,v in enumerate(values):
                words.append('y'+ROLE[f] if registers[f]==v else tagged(f,v))
                registers[f]=v
        elif model==8: # only changed fields of previous record; explicit close
            words=[tagged(f,v) for f,v in enumerate(values) if previous is None or previous[f]!=v]
            words.append(CLOSE);previous=values
        elif model==9: # postfix operators with fixed arity/type
            op,plant,part,state,med,amount,duration=r
            words=[ROOTS[plant],ROOTS[part],ROOTS[state],'ckhy',
                   ROOTS[med],ROOTS[amount],ROOTS[duration],ROOTS[op],'cthy']
        elif model==10:
            material=values[1]
            if material not in templates:
                index=len(templates); templates[material]=index
                rows.append([DEFINE,ROOTS[index],ROOTS[material],CLOSE])
            words=[CALL,ROOTS[templates[material]],ROOTS[values[0]],
                   ROOTS[values[2]],ROOTS[values[3]],ROOTS[values[4]],CLOSE]
        else: raise ValueError(model)
        rows.append(words)
    # Paragraph boundary initializes all local state in models 7,8,10.
    # It is supplied as visible layout for every model, never a hidden reset.
    return rows

def decode(model, rows):
    result=[]; registers=[None]*5; previous=None; templates={}
    for words in rows:
        if model==1:
            assert len(words)==5
            v=[SYL_INV[w]-OFFSETS[f] for f,w in enumerate(words)]
            r=unpack(v)
        elif model==2:r=field_decode(words,TAG_INVERSE)
        elif model==3:r=field_decode(words,INF_INVERSE)
        elif model==4:
            assert len(words)==7
            a=[TAG_INVERSE[words[i]] for i in (0,4,5,6)]
            assert [x[0] for x in a]==[0,2,3,4]
            assert words[1].startswith('qo') and words[2].startswith('ch') and words[2].endswith('y')
            assert words[3].startswith('sh') and words[3].endswith('y')
            r=(a[0][1],ROOT_INV[words[1][2:]],ROOT_INV[words[2][2:-1]],
               ROOT_INV[words[3][2:-1]],a[1][1],a[2][1],a[3][1])
        elif model==5:
            assert len(words)==5;v=[]
            for f,w in enumerate(words):
                short={ROLE[f]+HEAD[k]+'y':k for k in range(min(6,CAPS[f]))}
                v.append(short[w] if w in short else SYL_INV[w[2:]]-OFFSETS[f])
            r=unpack(v)
        elif model==6:
            assert len(words)==5;r=unpack([ROOT_INV[w] for w in words])
        elif model==7:
            assert len(words)==5;v=[]
            for f,w in enumerate(words):
                if w=='y'+ROLE[f]:assert registers[f] is not None;value=registers[f]
                else:
                    ff,value=TAG_INVERSE[w];assert ff==f
                v.append(value);registers[f]=value
            r=unpack(v)
        elif model==8:
            assert words[-1]==CLOSE
            v=list(previous) if previous is not None else [None]*5;seen=set()
            for w in words[:-1]:
                f,value=TAG_INVERSE[w];assert f not in seen;seen.add(f);v[f]=value
            assert None not in v;r=unpack(v);previous=v
        elif model==9:
            # Genuine stack evaluation: operators are recognized by their
            # written signs, with no word lookup or unprinted arguments.
            stack=[]
            for w in words:
                if w=='ckhy':
                    assert len(stack)>=3
                    state,part,plant=stack.pop(),stack.pop(),stack.pop()
                    assert all(isinstance(v,int) for v in (plant,part,state))
                    stack.append(('material',plant,part,state))
                elif w=='cthy':
                    assert len(stack)>=5
                    op,duration,amount,medium,material=[stack.pop() for _ in range(5)]
                    assert material[0]=='material';stack.append((op,*material[1:],medium,amount,duration))
                else:stack.append(ROOT_INV[w])
            assert len(stack)==1;r=stack[0]
        elif model==10:
            assert words[-1]==CLOSE
            if words[0]==DEFINE:
                assert len(words)==4;index=ROOT_INV[words[1]];assert index not in templates
                templates[index]=ROOT_INV[words[2]];continue
            assert words[0]==CALL and len(words)==7
            index=ROOT_INV[words[1]];assert index in templates
            r=unpack([ROOT_INV[words[2]],templates[index],*(ROOT_INV[w] for w in words[3:6])])
        else:raise ValueError(model)
        check_record(r);result.append(tuple(r))
    return result

NAMES={1:'Silbenwörter',2:'Stamm und Rollenendung',3:'Innere Rollenbeugung',
       4:'Begriffshierarchie',5:'Fachkürzel und Buchstabierung',6:'Feste Satzstellen',
       7:'Ausdrückliche Rückverweise',8:'Änderungsprotokoll',9:'Stellenschrift mit Operatoren',
       10:'Definition und Aufruf'}
