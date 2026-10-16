#!/usr/bin/env python3
"""One explicitly unconfirmed prefix construction on the complete source."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def construct(raw):
    remainder=raw;prefixes=[]
    while len(remainder)>1 and remainder[0] in 'qol':
        prefixes.append(remainder[0]);remainder=remainder[1:]
    node={'kind':'UNASSESSED_BASE','raw':remainder,'meaning':'UNASSIGNED'}
    for prefix in reversed(prefixes):
        node={'kind':'UNASSIGNED_PREFIX_FUNCTION','symbol':prefix,'argument':node,'meaning':'UNASSIGNED'}
    return node
def render(node):
    return node['raw'] if node['kind']=='UNASSESSED_BASE' else node['symbol']+render(node['argument'])
def pretty(node):
    return node['raw'] if node['kind']=='UNASSESSED_BASE' else node['symbol'].upper()+'('+pretty(node['argument'])+')'
def tail(node):
    return node['raw'] if node['kind']=='UNASSESSED_BASE' else tail(node['argument'])
def prefixes(node):
    return [] if node['kind']=='UNASSESSED_BASE' else [node['symbol']]+prefixes(node['argument'])
sourcepath=HERE/'LEXICAL_WORKSHEET_CONTEXT_20261016.json'
source=json.loads(sourcepath.read_text())
original=source['source_original_wrapper']['source_unit']
assert source['raw_group_count']==77 and source['distinct_exact_forms']==52
outlines=[];allterms=[];qruns=[]
for line in original['lines']:
    entries=[];run=[]
    for g in line['groups']:
        term=construct(g[2]);assert render(term)==g[2]
        record={'original_group':g,'expression':term,'display':pretty(term),'base':tail(term),'prefixes':prefixes(term),'word_meaning':'UNASSIGNED','outer_syntactic_role':'UNASSIGNED'}
        entries.append(record);allterms.append(record)
        if g[2].startswith('q'):run.append(g[0])
        else:
            if len(run)>1:qruns.append(run)
            run=[]
    if len(run)>1:qruns.append(run)
    outlines.append({'metadata':line['metadata'],'groups':entries})
assert len(allterms)==77
families={}
for row in allterms:families.setdefault(row['base'],set()).add(row['original_group'][2])
families={k:sorted(v) for k,v in sorted(families.items())}
contrasts=[{'split_raw':['ol','chedy'],'joined_raw':['olchedy']},
           {'split_raw':['qol','chedy'],'joined_raw':['qolchedy']},
           {'split_raw':['ol','shedy'],'joined_raw':['olshedy']}]
for c in contrasts:
    c['split_expressions']=[pretty(construct(z)) for z in c['split_raw']]
    c['joined_expressions']=[pretty(construct(z)) for z in c['joined_raw']]
    c['semantic_relation']='UNASSIGNED; distinct candidate structures are not a selected content difference'
result={'idea':'IDEA001092','status':'WHOLE_SOURCE_COMPOSITION_DRAFT_NOT_A_CONTENT_READING','source_pin':{'path':str(sourcepath.relative_to(ROOT)),'sha256':sha(sourcepath)},'plan_pin':{'path':str((HERE/'PREFIX_ROLE_PASSAGE_PLAN_20261016.json').relative_to(ROOT)),'sha256':sha(HERE/'PREFIX_ROLE_PASSAGE_PLAN_20261016.json')},'build_sha256':sha(Path(__file__)),'grammar':'Peel leading q/o/l while nonempty tail remains; nest in source order. One terminal prefix-shaped character is a distinct base variable. No role/meaning is supplied by the symbol names.','lines':outlines,'raw_group_count':77,'exact_whole_forms':52,'base_variables':len(families),'families':families,'contrasts':contrasts,'consecutive_q_groups_within_original_lines':qruns,'all_word_meanings':'UNASSIGNED','unassigned_functions':['Q','O','L'],'unassigned_outer_syntax':True,'counts_are_not_translation_progress':True,'limits':['This grammar covers arbitrary strings; coverage and literal roundtrip do not favor it.','Root identity and prefix segmentation are hypotheses, not confirmed morphology.','Single terminal l is a base variable distinct from the hypothesized prefix function L. This is a paid grammar convention, not a deciphered homograph.','No word boundary, glyph run, p/y prefix or alternate reader is normalized.','No default noun/Class and no semantic no-op assigned to unhandled text. All original occurrences and repetitions survive.','No operator function, clause attachment or later content consumer is established.']}
write('PREFIX_ROLE_PASSAGE_DRAFT_20261016.json',result)
tick=chr(96)
md=['# Ein ganzer Absatz mit unzugewiesenen Bausteinen','',
'**Konstruktionsversuch, noch keine Inhaltslesung.** Alle77originalenIT-Gruppen bleiben erhalten. Q, O und L sind hier nur Namen unbestimmter Funktionen. Die Wortbedeutungen und Satzrollen bleiben unzugewiesen.','',
'Die Regel wird überall gleich angewandt: Anfangs-q/o/l stehen außen um den verbleibenden nichtleeren Rest. Das ist eine gewählte Zerlegung, kein identifizierter Sprachbau. Ein einzelnes letztes l bleibt eine eigene Basisvariable, statt ein Operator ohne Argument zu werden.','']
for line in outlines:
    md += ['## '+line['metadata']['locus'],'',
           '**Original:** '+' '.join(g['original_group'][2] for g in line['groups']),'',
           '**Konstruktion:** '+' · '.join(tick+g['display']+tick for g in line['groups']),'']
md+=['## Was gemeinsam sichtbar wird','',
'Wiederkehrende Restformen verwenden in diesem Entwurf dieselbe Variable. Beispiele sind kedy in O(L(kedy))/Q(O(kedy)), keedy in O(keedy)/Q(O(keedy)), und chedy als ganze Form sowie in O(L(chedy))/Q(O(L(chedy))). Kein Rest erhält einen erfundenen Stoff-, Tätigkeits- oder Zahlenwert.','',
'Die getrennten und zusammengezogenen Formen werden ausdrücklich verschieden dargestellt:','']
for c in contrasts:
    md += ['- '+' · '.join(tick+s+tick for s in c['split_expressions'])+' gegenüber '+' · '.join(tick+s+tick for s in c['joined_expressions'])+'.']
md += ['','Das wählt keine Bedeutungsverschiedenheit. Ohne die Funktionen und eine Zwischenwortregel ist etwa noch nicht bekannt, ob O(l) und ein folgendes chedy überhaupt zusammengehören. Genau diese offene Stelle darf eine flüssige deutsche Geschichte nicht verdecken.','',
'Die Wiederholungen sind ebenfalls noch da. qokeey qokeey bleibt zweimal Q(O(keey)); qokedy qokedy bleibt zweimal Q(O(kedy)). Es ist noch nicht entschieden, ob das Wiederholung, Verstärkung, zwei Erwähnungen oder etwas anderes ausdrückt.','',
'## Die fehlende Lesung','',
'Der Entwurf liefert Wortaufbau und eine gemeinsame Notation über den ganzen Absatz. Er liefert noch keine grammatischen Funktionen für Q/O/L, keine Satzgliederung und keinen geschriebenen späteren Verbraucher eines berechneten Inhalts. Damit ist er **keine vollständige konsistente Inhaltsrekonstruktion**, auch nicht mit bloß unbekannten Stoffnamen. Ein neuer Decoder würde diese fehlenden Angaben nicht ersetzen.','',
'GDT751/753 erlauben aus alten Karten kein q=Befehl/o=Zubereitung. GDT1146s feste rechte Rezeptargumente und R771s pauschale Class-/DAIIN-Regeln bleiben fehlgeschlagen. Deshalb werden ihre Glossen und Klassen hier nicht als Lückenfüller verwendet.','',
'Die unmittelbaren q-Folgen zeigen zudem, was eine künftige Grammatik ausdrücklich erklären muss: mehrere q-Formen stehen direkt nacheinander. Ein Modell mit starren disjunkten Verb-/Nomenklassen darf solche Wörter nicht nach Bedarf umklassifizieren.','',
'Quelle, jede Quell-ID, beide Separatoren, alle Metadaten und Eingabepins stehen im JSON. Der unveränderte Zeichentext lässt sich aus jedem Baum wiederherstellen; das prüft nur die Datenwiedergabe.','']
(HERE/'PREFIX_ROLE_PASSAGE_DRAFT_20261016.md').write_text('\n'.join(md))
print(json.dumps({'status':result['status'],'raw_groups':77,'exact_whole_forms':52,'base_variables':len(families),'q_runs':qruns,'meaning_selection':'NONE'}))
