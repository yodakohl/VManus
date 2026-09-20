"""Post-result presentation and direct endpoint/sample-map comparisons only."""
from common import *
import collections,csv
checklock();s,g=inputs();panel=read(A/'PANEL.json');rows=read(A/'ROWS.json');candidates=read(A/'CANDIDATE_PREDICTIONS.json');source=read(R/s['source_candidates']);validation=read(A/'VALIDATION.json')
assert validation['status']=='PASS' and validation['unverified_primary_negatives']==0
summary=[];signatures=collections.defaultdict(list);positive=[];explanations=[];conflicts=[]
for c in candidates:
    support=[];absent=[]
    for p,r in zip(panel,rows):
        q=next(q for q in r['rows'] if q['candidate']==c['id'])
        if q['status']=='sat':support.append(p['id'])
        elif q['status']=='unsat':absent.append(p['id'])
    signatures[tuple(support)].append(c['id'])
    summary.append(dict(candidate=c['id'],chedy=c['values']['chedy'],chedy_class=c['chedy_class'],variant=c['variant'],coherent_contexts=support,contradicted_contexts=len(absent),unknown_contexts=len(panel)-len(support)-len(absent),independent_meaning_capacity=0))
names={'W':'Fracht A','G':'Fracht B','C':'Fracht C','FIRST_CARGO':'zuerst erwähnte Fracht','OTHER_CARGO':'andere/erste Fracht'}
def name(x):return names.get(x,x)
def prose(cl):
    k=cl['kind'];x=cl['symbols']
    fixed={'INITIAL':'Fracht und Begleitperson befinden sich am Ausgangsufer.','GOAL':'Ziel ist das andere Ufer ohne Schaden.','SAFETY':'Gefährliche Paare nicht unbeaufsichtigt zusammenlassen (hier wird kein solches Paar genannt).','THEN':'Dann.','STAY':'Die zuletzt beförderte Fracht dort lassen.','ALONE':'Allein zurückfahren.','CONCLUSION':'Alle sind unversehrt dort bei der Begleitperson.'}
    if k in fixed:return fixed[k]
    if k=='CAPACITY':return 'Höchstens eine Fracht neben der Begleitperson; Beispiel: '+name(x[4])+'.'
    if k=='FERRY':return name(x[1])+' zum jeweils anderen Ufer befördern.'
    if k=='EXCLUDE':return 'Ohne '+name(x[1])+' zurückfahren.'
    if k=='WITH_OUT':return 'Mit dem Boot '+name(x[3])+' hinüberbringen.'
    if k=='WITH_RETURN':return 'Mit '+name(x[1])+' zurückfahren.'
    if k=='CONVEY':return 'Als Nächstes '+name(x[2])+' hinüberbringen.'
    if k=='FINAL_TRIP':return 'Abschließend gemeinsam mit '+name(x[4])+' hinüberfahren.'
    if k=='RESULT':return 'Die zuletzt beförderte Fracht ist bei den übrigen, darunter '+name(x[3])+'.'
    raise AssertionError(k)
md=['# Alle positiven bedingten Kontextlesungen','',
    'Alle 72 positiven Kandidaten-/Absatzzeugen stehen unten. Die elf projizierten Wortrollen sind fest; die übrigen Wörter sind je Absatz neu zugeordnet. Dies ist keine gemeinsame vollständige Übersetzung mit f83r. Die 16 ungebundenen Vergleichszeugen stehen separat in ROWS.json. Namen der Frachtstücke sind anonyme Identitäten. Alle Blätter waren bereits exponiert; unabhängige Bedeutungsbestätigung: null.','']
for p,r in zip(panel,rows):
    good=[]
    for c,q in zip(candidates,r['rows'][1:]):
        assert c['id']==q['candidate'];ends=[]
        for k,lo in [('INITIAL',0),('CONCLUSION',len(p['words'])-6)]:
            for i,terminal in enumerate(g['patterns'][k]):
                word=p['words'][lo+i]
                if word in c['values'] and c['values'][word]!=terminal:ends.append(dict(position=lo+i+1,word=word,predicted=c['values'][word],required_by_scope=terminal,clause=k))
        if ends:assert q['status']=='unsat'
        explanations.append(dict(paragraph=p['id'],candidate=c['id'],status=q['status'],baseline_status=r['rows'][0]['status'],direct_endpoint_contradictions=ends,remaining_full_constraint_exclusion=q['status']=='unsat' and not ends))
        if q['status']!='sat':continue
        old=source['attempts'][c['original_attempt']]['code'];different=[dict(word=w,original_saved_value=old[w],context_saved_value=q['code'][w]) for w in sorted(set(old)&set(q['code'])) if old[w]!=q['code'][w]]
        conflicts.append(dict(paragraph=p['id'],candidate=c['id'],shared_original_words=sorted(set(old)&set(q['code'])),saved_map_conflicts=different,alternative_full_maps_not_queried=True))
        good.append(c['id']);paths=[v for v in q['replay']['paths'] if v['consistent']]
        positive.append(dict(paragraph=p['id'],candidate=c['id'],cargo=q['replay']['cargo'],voyages=[len(v['trace'])-1 for v in paths],references=q['replay']['references'],hazards=q['replay']['hazards']))
        md += [f'## {p["id"]} — {c["id"]}','',f'Quellenflag streng: {p["strict_anchor_eligible"]}; chedy: {c["values"]["chedy"]}; Bezugsregeln: {json.dumps(c["variant"],ensure_ascii=False)}.','', '| Gruppe | Wort | Bedingte Terminalrolle |','|---|---|---|']
        md += [f'| {i+1} | {w} | {q["code"][w]} |' for i,w in enumerate(p['words'])]
        md += ['', '| Vollständige Spanne | Bedingte Lesung |','|---|---|']
        md += [f'| {cl["start"]+1}–{cl["end"]} | {prose(cl)} |' for cl in q['parse']]
        for path in paths:
            md += ['', 'Tatsächliche Ladungen: '+' → '.join(name(v['load']) if v['load'] else 'leer' for v in path['trace'][1:])+'. Keine physischen, Ziel-, Zustands- oder Sicherheitswidersprüche unter dem Modell.']
        md += ['', 'Konflikte mit der gespeicherten vollständigen Ursprungskarte: '+('; '.join(x['word']+': '+x['original_saved_value']+' / '+x['context_saved_value'] for x in different) or 'keine')+'. Dies ist ein Zeugenvergleich, kein Ausschluss aller alternativen gemeinsamen Karten.','']
    if good:assert len(good)==36
(A/'READINGS.md').write_text('\n'.join(md).rstrip()+'\n')
put('CANDIDATE_SUMMARY.json',summary);put('SUPPORT_GROUPS.json',[dict(contexts=list(k),candidates=v) for k,v in signatures.items()]);put('POSITIVE_CONSEQUENCES.json',positive);put('EXPLANATIONS.json',explanations);put('SAVED_MAP_CONFLICTS.json',conflicts)
with (A/'CANDIDATE_SUMMARY.tsv').open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['candidate','chedy','class','variant','coherent_contexts','contradictions','unknown','independent_meaning_capacity'])
    for c in summary:w.writerow([c['candidate'],c['chedy'],c['chedy_class'],json.dumps(c['variant'],sort_keys=True),';'.join(c['coherent_contexts']),c['contradicted_contexts'],c['unknown_contexts'],0])
out=dict(scope_counts=dict(collections.Counter(r['scope_status'] for r in read(A/'CENSUS.json'))),query_paragraphs=len(panel),query_leaves=len({p['leaf'] for p in panel}),strict_contexts=sum(p['strict_anchor_eligible'] for p in panel),candidate_outcomes=dict(collections.Counter(e['status'] for e in explanations)),endpoint_contradictions=sum(bool(e['direct_endpoint_contradictions']) for e in explanations),other_full_constraint_exclusions=sum(e['remaining_full_constraint_exclusion'] for e in explanations),identical_support_groups=len(signatures),all_positive_saved_maps_conflict=all(c['saved_map_conflicts'] for c in conflicts),positive_witnesses=len(positive),full_joint_dictionary='NOT_TESTED',confirmed_words=0,independent_meaning_capacity=0)
put('SUMMARY.json',out);print(json.dumps(out,indent=2))
