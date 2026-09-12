"""Execute the authored P30 two-operator hypothesis on all admitted BATH3 prose.
No search, decoding, unknown-word inference, or image-fit optimization.
"""
import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

P = Path('research_registry/proposals/translation_programs_20260912/work/P30')

def read(name):
    with (P/name).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def table(name, rows, fields):
    with (P/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def dump(name, obj):
    (P/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

for s in json.loads((P/'SOURCE.json').read_text()):
    assert hashlib.sha256((P/s['projection']).read_bytes()).hexdigest()==s['projection_sha256']
    assert hashlib.sha256(Path(s['source']).read_bytes()).hexdigest()==s['sha256']
lines, panels = read('PROSE.tsv'), read('PANELS.tsv')
assert len(lines)==123 and len(panels)==10
assert {x['page'] for x in lines}=={'f77r','f82r','f83r'}
ops={'qokeedy':1, 'qokedy':0}
lex={'D0':{'qokeedy':'stelle Verbindung A–B her','qokedy':'löse Verbindung A–B'},
     'R0':{'qokeedy':'A–B ist verbunden','qokedy':'A–B ist getrennt'}}
dump('MODEL.json', {'hypothetical_only':True,'confirmed_meanings':0,
    'baseline':{'nodes':['A','B'],'node_identity':'unbound functional sites, not necessarily people','edge_AB':0},
    'operators':ops,'lexicon':lex,'reset':'once per panel, not per physical line or embedded record',
    'repetition':'idempotent edge set/remove; no participant creation or destruction',
    'unknown_words':'preserved open; strict execution additionally assumes they do not alter edge_AB',
    'R0':'timeless assertions about the same fixed A/B pair',
    'R1':'Same full R0 word alignment, but descriptive subjects remain unresolved. No per-token successful assignment, no global contradiction or image match claimed. Stronger live descriptive rival.'})
tokens=[]
for line in lines:
    for i,w in enumerate(line['zl3b_line'].split(),1):
        tokens.append({**{k:line[k] for k in ['page','panel_id','record_id','locus']},'position':i,'word':w})
assert len(tokens)==940
trace=[]; record_summary=[]; panel_summary=[]
for panel in panels:
    state=0
    for record in dict.fromkeys(t['record_id'] for t in tokens if t['panel_id']==panel['panel_id']):
        tt=[t for t in tokens if t['record_id']==record]
        start=state; selected=[]
        for t in tt:
            if t['word'] in ops:
                new=ops[t['word']]
                event={**t,'before':state,'after':new,'changes_edge':new!=state,'participant_count_before':2,'participant_count_after':2}
                trace.append(event); selected.append(event); state=new
        record_summary.append({'page':panel['page'],'panel_id':panel['panel_id'],'record_id':record,
            'groups':len(tt),'operators':len(selected),'entry_edge':start,'exit_edge':state,
            'set':sum(x['word']=='qokeedy' for x in selected),'remove':sum(x['word']=='qokedy' for x in selected),
            'state_changes':sum(x['changes_edge'] for x in selected),
            'R0_same_pair_conflict':len({x['word'] for x in selected})==2,
            'visual_A_B_binding':'UNRESOLVED','complete_configuration_reconstructed':False})
    own=[t for t in trace if t['panel_id']==panel['panel_id']]
    panel_summary.append({'page':panel['page'],'panel_id':panel['panel_id'],'groups':sum(x['groups'] for x in record_summary if x['panel_id']==panel['panel_id']),
        'operators':len(own),'final_edge':state,'changes':sum(t['changes_edge'] for t in own),
        'R0_same_pair_conflict':len({t['word'] for t in own})==2,'image_match':'NOT_SCORED_UNBOUND_TARGETS'})
table('OPERATORS.tsv',trace,list(trace[0]))
table('RECORDS.tsv',record_summary,list(record_summary[0]))
table('PANEL_RESULTS.tsv',panel_summary,list(panel_summary[0]))

for model in lex:
    rows=[{**t,'reading':lex[model].get(t['word'],'⟦'+t['word']+'⟧'),
           'status':'HYPOTHESIS_ONLY' if t['word'] in ops else 'OPEN'} for t in tokens]
    table('ALIGNMENT_'+model+'.tsv',rows,list(rows[0]))
    text=['# P30 '+model+' — alle drei vollständigen Tafeltexte','',
          'Zwei ganze Wortannahmen. Alle anderen Gruppen bleiben sichtbar ungelöst. Diese Ausrichtung ist keine vollständige Übersetzung.','']
    for page in ['f83r','f77r','f82r']:
        text+=['## '+page,'']
        for line in [x for x in lines if x['page']==page]:
            rr=[x for x in rows if x['locus']==line['locus']]
            text+=['**'+line['locus']+' · '+line['record_id']+'**','',
                   '`'+line['zl3b_line']+'`','', ' / '.join(x['reading'] for x in rr),'']
    (P/('READING_'+model+'.md')).write_text('\n'.join(text))
    back=read('ALIGNMENT_'+model+'.tsv')
    assert [(x['locus'],int(x['position']),x['word']) for x in back]==[(x['locus'],x['position'],x['word']) for x in tokens]

# All four record orders; baseline once for the shared panel, never choose best order.
coupled=[r['record_id'] for r in record_summary if r['panel_id']=='F83_LOWER_COUPLED']
assert len(coupled)==4
orders=[]
for order in itertools.permutations(coupled):
    state=0; seq=[]
    for record in order:
        for t in tokens:
            if t['record_id']==record and t['word'] in ops:
                state=ops[t['word']];seq.append(t['word'])
    orders.append({'order':'|'.join(order),'operator_sequence':' '.join(seq),'final_edge':state})
table('RECORD_ORDER_SENSITIVITY.tsv',orders,list(orders[0]))

diagrams=['# P30 — aus D0 erzeugte Konfigurationen','',
 'Jeder Kasten zeigt ausschließlich die hypothetische A/B-Kante nach allen zugehörigen Records. Keine rekonstruierte Gesamtzeichnung.',
 'A/B bleiben ungebundene Funktionsstellen. Eine gestrichelte Verbindung in diesen Diagrammen bezeichnet fehlende Kante, keine unsichere beobachtete Bildkante.',
 'Alle nicht durch D0 erzeugten Bilddetails sind in VISION.md erhalten, nicht als passend vorausgesetzt.','',
 '## Gemeinsames Grundschema','', '```mermaid','graph LR',' A["A: ungebundene Stelle"] -.- B["B: ungebundene Stelle"]','```','',
 'Anfang: e(A,B)=0; Herstellen setzt1, Lösen setzt0. Beide Knoten bleiben erhalten.','']
for page in ['f83r','f77r','f82r']:
    diagrams+=['## Tafel '+page,'','```mermaid','graph TB']
    for i,r in enumerate([x for x in panel_summary if x['page']==page]):
        diagrams += [' subgraph P'+str(i)+'["'+r['panel_id']+' · e='+str(r['final_edge'])+'"]',
                     ' A'+str(i)+'["A"] '+('--'+'-' if r['final_edge'] else '-.-')+' B'+str(i)+'["B"]',' end']
    diagrams+=['```','']
(P/'DIAGRAMS.md').write_text('\n'.join(diagrams))
dump('RESULT.json',{'status':'PARTIAL_DIFFERENCE_LANGUAGE_NO_WORD_IDENTIFICATION',
 'pages':3,'panels':10,'records':13,'groups':940,'operator_positions':len(trace),'open_positions':940-len(trace),
 'whole_word_hypotheses':2,'form_counts':dict(Counter(x['word'] for x in trace)),
 'state_changes':sum(x['changes_edge'] for x in trace),
 'R0_same_pair_conflict_records':sum(x['R0_same_pair_conflict'] for x in record_summary),
 'R0_same_pair_conflict_panels':sum(x['R0_same_pair_conflict'] for x in panel_summary),
 'coupled_orderings':24,'coupled_end_states':sorted({x['final_edge'] for x in orders}),
 'records_in_coupled_with_operators':[x['record_id'] for x in record_summary if x['panel_id']=='F83_LOWER_COUPLED' and x['operators']],
 'text_bound_visual_targets':0,'complete_panel_reconstructions':0,'confirmed_meanings':0,
 'independent_confirmation_capacity':0,'held_pages_opened':0})
dump('VALIDATION.json',{'status':'PASS_SOURCE_CONSERVATION_AND_EXECUTION_ONLY',
 'groups_each_alignment':940,'models':2,'record_orders_exhausted':24,'source_hashes_checked':True,
 'meaning_or_visual_match_validated':False})
print((P/'RESULT.json').read_text())
