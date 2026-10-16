#!/usr/bin/env python3
"""Exploratory next-base application, with every original group retained."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pretty(t):return t['raw'] if t['kind']=='UNASSESSED_BASE' else t['symbol'].upper()+'('+pretty(t['argument'])+')'
def compile_groups(groups):
    terms=[];pending=[];pending_groups=[]
    for g in groups:
        raw=g[2];cut=0
        while cut<len(raw) and raw[cut] in 'qol':cut+=1
        pending.extend({'symbol':c,'source_group_id':g[0],'character_offset':i} for i,c in enumerate(raw[:cut]))
        pending_groups.append(g[0])
        if cut==len(raw):continue
        t={'kind':'UNASSESSED_BASE','raw':raw[cut:],'source_group_id':g[0],'character_offset':cut,'meaning':'UNASSIGNED'}
        for op in reversed(pending):
            t={'kind':'UNASSIGNED_PREFIX_FUNCTION',**op,'argument':t,'meaning':'UNASSIGNED'}
        terms.append({'source_group_ids':pending_groups[:],'expression':t,'display':pretty(t)})
        pending=[];pending_groups=[]
    return terms,pending,pending_groups
sourcepath=HERE/'LEXICAL_WORKSHEET_CONTEXT_20261016.json'
x=json.loads(sourcepath.read_text());source=x['source_original_wrapper']['source_unit']
groups=[g for line in source['lines'] for g in line['groups']]
assert len(groups)==77 and len({g[0] for g in groups})==77
terms,pending,unclosed=compile_groups(groups)
assert not pending and not unclosed
assert [i for t in terms for i in t['source_group_ids']]==[g[0] for g in groups]
used={g[0]:[] for g in groups};bases=set()
def trace(t):
    gid=t['source_group_id'];offset=t['character_offset']
    if t['kind']=='UNASSESSED_BASE':
        bases.add(t['raw']);used[gid].extend((offset+i,c) for i,c in enumerate(t['raw']))
    else:
        used[gid].append((offset,t['symbol']));trace(t['argument'])
for term in terms:trace(term['expression'])
for g in groups:assert sorted(used[g[0]])==list(enumerate(g[2]))
operator_only=[g for g in groups if all(c in 'qol' for c in g[2])]
contrasts=[]
for split,joined in [(['ol','chedy'],'olchedy'),(['qol','chedy'],'qolchedy'),(['ol','shedy'],'olshedy')]:
    a,ap,_=compile_groups([[str(i),'',s,'',''] for i,s in enumerate(split)])
    b,bp,_=compile_groups([['joined','',joined,'','']])
    assert not ap and not bp and a[0]['display']==b[0]['display']
    contrasts.append({'split':split,'joined':joined,'candidate_term':a[0]['display'],'equality_status':'ASSUMED_BY_THIS_GRAMMAR_NOT_CONFIRMED_NATIVE_MEANING'})
result={'idea':'IDEA001092','status':'COMPLETE_SCOPED_CONSTRUCTION_NO_CONTENT_READING','source_pin':{'path':str(sourcepath.relative_to(ROOT)),'sha256':sha(sourcepath)},'revision_note_sha256':sha(HERE/'PREFIX_ROLE_OPEN_APPLICATION_NOTE_20261016.json'),'build_sha256':sha(Path(__file__)),'original_source':source,'raw_group_count':len(groups),'closed_term_count':len(terms),'base_variable_count':len(bases),'operator_only_groups':operator_only,'open_at_paragraph_end':pending,'terms':terms,'joined_split_contrasts':contrasts,'word_meanings':'UNASSIGNED','prefix_functions':'UNASSIGNED','between_term_relations':'UNASSIGNED','selected_over_v1':False,'limits':['Coverage is possible for arbitrary text ending in a non-operator tail; it does not favor this grammar.','Shared tails, joined/split content identity, and cross-line scope are hypotheses.','ASTs do not reconstruct physical spacing; original source retains every gap.','No Class/noun defaults, command/preparation glosses, repetition deletion, or reader pooling.','A written next base closes pending syntax, not a demonstrated later consumer of known content.','No experiment or translation success is claimed.']}
(HERE/'PREFIX_ROLE_OPEN_APPLICATION_DRAFT_20261016.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
md=['# Eine einfache Regel über den ganzen Absatz','','**Unbestätigter Bauversuch, keine Übersetzung.** q, o und l am Anfang sind unbestimmte Vorsätze. Besteht eine ganze Gruppe nur daraus, warten sie auf den nächsten Wortkern – auch über eine Zeilengrenze. Alle anderen Zeichen des Kerns bleiben unverändert.','','Die vollständigen 77 Originalgruppen ergeben hier '+str(len(terms))+' geschlossene Ausdrücke mit '+str(len(bases))+' verschiedenen Restformen. Das belegt nur, dass diese gewählte Schreibregel auf diesem Absatz ausführbar ist. Funktionen, Bedeutungen und Beziehungen zwischen den Ausdrücken fehlen weiterhin.','','## Originaltext','']
for line in source['lines']:md += [line['metadata']['locus']+': '+' '.join(g[2] for g in line['groups']),'']
md += ['## Konstruktion in Originalreihenfolge','']
for i,t in enumerate(terms,1):md += [str(i)+'. `'+t['display']+'` — '+', '.join(t['source_group_ids'])]
md += ['','## Was die einfache Regel kostet','','Acht Gruppen brauchen den nächsten Wortkern. Das qol am Ende von Zeile43 bindet sogar olshees am Anfang von Zeile44: Q(O(L(O(L(shees))))). Das ist eine Vorhersage dieser Regel, keine erkannte Satzbedeutung.','','ol chedy und olchedy ergeben hier denselben Ausdruck O(L(chedy)); entsprechend qol chedy/qolchedy und ol shedy/olshedy. Gleicher Inhalt wird dabei angenommen. Die bloße Schreibähnlichkeit beweist ihn nicht.','','qokedy qokedy bleibt zweimal Q(O(kedy)). Keine Wiederholung wird zu einer einzigen Erwähnung verkürzt oder als Betonung übersetzt.','','Die erste Version mit getrennten Wortbäumen bleibt erhalten. Beide sind unselektierte Alternativen. Diese zweite Version hat eine feste Anheftungsregel, aber noch keine Inhaltsrekonstruktion: Q/O/L und alle Restbedeutungen bleiben unzugewiesen. Die ursprünglichen Lücken, IDs und Metadaten stehen unverändert im JSON; aus den Bäumen allein wären sie nicht wiederzugewinnen.','']
(HERE/'PREFIX_ROLE_OPEN_APPLICATION_DRAFT_20261016.md').write_text('\n'.join(md))
print(json.dumps({'groups':len(groups),'terms':len(terms),'base_variables':len(bases),'operator_only_groups':len(operator_only),'open_at_end':len(pending),'exact_source_coverage':True,'content_reading':False}))
