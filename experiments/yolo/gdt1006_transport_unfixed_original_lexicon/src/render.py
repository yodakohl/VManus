"""Post-run presentation only: no additional candidate search or selection."""
from common import *
import collections,csv

checklock()
pred=read(A/'PREDICTIONS.json'); panel=read(A/'PANEL.json')
raw=next(p['words'] for p in panel if p['edition']=='ZL3b')
names={'W':'Fracht A','G':'Fracht B','C':'Fracht C','M':'Begleitperson','B':'Boot',
       'FIRST_CARGO':'zuerst/zuletzt erwähnte Fracht','OTHER_CARGO':'andere/erste Fracht'}
def label(x):return names.get(x,x)
def clause(c):
    s=c['symbols'];k=c['kind']
    fixed={
      'INITIAL':'Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer.',
      'GOAL':'Ziel ist das gegenüberliegende Ufer ohne Schaden.',
      'SAFETY':'Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben.',
      'THEN':'Dann.',
      'COPY':'Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen.',
      'STAY':'Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer).',
      'ALONE':'Allein zurückfahren.',
      'CONCLUSION':'Somit sind alle unversehrt dort, begleitet von der Begleitperson.'}
    if k in fixed:return fixed[k]
    if k=='CAPACITY':return f'Höchstens ein Frachtstück neben der Begleitperson; Beispiel: {label(s[4])}.'
    if k=='WITH_OUT':return f'Mit dem Boot {label(s[3])} hinüberbringen.'
    if k=='EXCLUDE':return f'Ohne {label(s[1])} zurückfahren (Gegenvariante: mit dieser Fracht).'
    if k=='FERRY':return f'{label(s[1])} zum jeweils anderen Ufer übersetzen.'
    if k=='WITH_RETURN':return f'Mit {label(s[1])} zurückfahren.'
    if k=='PAIR':return f'{label(s[0])} wäre mit {label(s[3])} unbeaufsichtigt ein gefährliches Paar.'
    if k=='CONVEY':return f'Als Nächstes {label(s[2])} hinüberbringen.'
    if k=='FINAL_TRIP':return f'Abschließend fahren Begleitperson und {label(s[4])} gemeinsam hinüber.'
    if k=='RESULT':return f'Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter {label(s[3])}.'
    raise AssertionError(k)

md=['# Vollständige bedingte Lesungen aus GDT1006','',
    'Dies sind Modellzeugen, keine bestätigten Übersetzungen. Jede hier gezeigte Lesung deckt alle 63 ZL3b-Gruppen ab. Die unklare sol/chedy-Grenze bleibt bestehen. Fracht A/B/C sind anonyme Identitäten; Tier- und Pflanzennamen werden nicht vorausgesetzt. Die Satzmuster und ihre Bedeutungen sind Annahmen. Anweisungen und Erzählung sind dadurch nicht unterschieden.','',
    'Alle 33 gefundenen kohärenten vollständigen Wörterbücher werden ohne Auswahl gezeigt. Die Projektion enthält 102 Kombinationen aus elf Wortrollen und fünf Bezugseinstellungen. Sie erschöpft nur bei BIJECTIVE die Rollenprojektion, nicht alle vollständigen Wörterbücher innerhalb einer Projektion.','',
    '[102 Kandidaten](PROJECTED_CANDIDATES.tsv) · [Alle 1.232 geprüften Karten](CANDIDATES.tsv) · [Alle 47 Wortdomänen je Familie](WORD_DOMAINS.tsv) · [Satzmuster gegen Inhalt](SYNTAX_VS_WORLD.tsv)','']
summary=[];consequences=[];symmetry=[];observations=collections.defaultdict(list)
for family in ['FUNCTIONAL','BIJECTIVE']:
    r=read(A/f'FAMILY_{family}.json');cs=[a for a in r['attempts'] if a['coherent_variants']]
    summary.append(dict(family=family,evaluated_maps=len(r['attempts']),coherent_maps=len(cs),failed_maps=r['failed_maps'],projected_tuples=len(r['positive_tuples']),projection_exhausted=r['exhaustive_projection'],stop_reason=r['stop_reason'],primary_wall_seconds=r['wall_seconds']))
    md += [f'## {family}','',f'{len(cs)} kohärente vollständige Karten; {len(r["positive_tuples"])} positive Rollen-/Bezugsvarianten. Projektionsraum vollständig: {r["exhaustive_projection"]}. Stopp: {r["stop_reason"]}.','']
    norm=collections.defaultdict(list)
    for t in r['positive_tuples']:
        key=min(tuple(dict(zip('WGC',q)).get(t['values'][w],t['values'][w]) for w in pred['projection_words']) for q in itertools.permutations('WGC'))+(t['variant_index'],)
        norm[key].append(t['tuple'])
    symmetry.append(dict(family=family,exhaustive=r['exhaustive_projection'],classes=[dict(canonical_values=list(k[:-1]),variant_index=k[-1],tuple_ids=v) for k,v in norm.items()]))
    for a in cs:
        aid=a['attempt'];md += [f'### {family} Karte {aid}','',f'Kohärente Bezugseinstellungen: {a["coherent_variants"]}. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_{family}.json.','', '| Form | Bedingte Terminalrolle |','|---|---|']
        md += [f'| {w} | {v} |' for w,v in a['code'].items()]
        md += ['', '| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |','|---|---|---|']
        for c in a['parse']:md.append(f'| {c["start"]+1}–{c["end"]} | {" ".join(raw[c["start"]:c["end"]])} | {clause(c)} |')
        md += ['', '| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |','|---|---|---|---|---|']
        for v in a['full_replays']:
            if v['variant_index'] not in a['coherent_variants']:continue
            paths=[p for p in v['paths'] if p['consistent'] and len(p['trace'])==8];assert paths
            for pi,p in enumerate(paths):
                loads=[q['load'] for q in p['trace'][1:]]
                hazards='; '.join(' + '.join(label(x) for x in h) for h in v['hazards'])
                refs='; '.join(f'{x["clause"]}: {x["symbol"]} → {label(x["value"])}' for x in v['references']) or 'keine Frachtverweise'
                md.append(f'| V{v["variant_index"]:02d} | {", ".join(k+"="+x for k,x in v["variant"].items())} | {hazards} | {" → ".join(label(x) if x else "leer" for x in loads)} | {refs} |')
                physical=dict(hazards=v['hazards'],trace=p['trace'],there_references=p.get('there_references',[]))
                signature=digest(physical)
                observations[signature].append(dict(family=family,attempt=aid,variant_index=v['variant_index'],path=pi))
                consequences.append(dict(family=family,attempt=aid,variant_index=v['variant_index'],path=pi,variant=v['variant'],hazards=v['hazards'],references=v['references'],trace=p['trace'],there_references=p.get('there_references',[]),physical_signature=signature,contradictions=[],independent_meaning_capacity=0))
        md += ['', 'Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.','']

md += ['## Was die erhaltenen Konsequenzen nicht unterscheiden','',
 'Die sechs globalen Umbenennungen der drei anonymen Frachtstücke ändern keine Transportlogik. SYMMETRY.json gruppiert ausschließlich die elf projizierten Rollen und die Bezugsvariante unter diesen Umbenennungen: sechs Klassen bei BIJECTIVE und 18 bisher beobachtete bei FUNCTIONAL. Das beweist keine Gleichheit der nichtprojizierten Wörterbücher.','',
 'OBSERVATION_GROUPS.json gruppiert exakt identische gespeicherte Gefahrpaare, Zustandsfolgen und Ortsbezüge. Diese Gruppen gelten nur für die geprüften Zeugen. Unterschiedliche Referenzregeln oder Wortrollen bleiben in CANDIDATE_CONSEQUENCES.json sichtbar, selbst wenn sie auf diesem Verlauf dieselben Zustände ergeben. Singleton-Wörterbücher innerhalb einer positiven Projektion wurden nicht vollständig aufgezählt.','',
 'Zielufer und gegenwärtiges Ufer fallen an den beobachteten Ortsbezügen zusammen. Bei Karten ohne FIRST_CARGO hat dessen FIRST/RECENT-Einstellung keinen Effekt. Ein wiederholter Eigenname und ein korrekt aufgelöster Rückverweis können dieselbe Fahrtfolge beschreiben. Die Wortformen selbst identifizieren weder Boot, Person noch Pflanze unabhängig von der angenommenen Geschichte.','']
(A/'READINGS.md').write_text('\n'.join(md).rstrip()+'\n')
put('SUMMARY.json',dict(experiment='GDT1006',families=summary,projected_word_count=11,complete_dictionary_words=47,confirmed_words=0,independent_meaning_capacity=0,significance=False))
put('SYMMETRY.json',symmetry);put('CANDIDATE_CONSEQUENCES.json',consequences)
put('OBSERVATION_GROUPS.json',[dict(signature=k,witnesses=v) for k,v in observations.items()])
expected=sum(len(a['coherent_variants']) for family in ['FUNCTIONAL','BIJECTIVE'] for a in read(A/f'FAMILY_{family}.json')['attempts'])
assert len(consequences)==expected
print(json.dumps(dict(maps=sum(x['coherent_maps'] for x in summary),coherent_witness_variants=len(consequences),exact_observed_groups=len(observations),symmetry_classes={x['family']:len(x['classes']) for x in symmetry}),indent=2))
