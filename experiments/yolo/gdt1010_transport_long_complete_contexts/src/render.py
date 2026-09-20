from common import *
import collections,csv

names={'W':'Fracht A','G':'Fracht B','C':'Fracht C','M':'Begleitperson','B':'Boot',
       'FIRST_CARGO':'zuerst/zuletzt erwähnte Fracht','OTHER_CARGO':'andere/erste Fracht'}
def label(x):return names.get(x,x)
def clause(c):
    s=c['symbols'];k=c['kind']
    fixed={
      'INITIAL':'Die genannten Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer.',
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

rows=read(A/'ROWS.json');panel=read(A/'PANEL.json');checks={x['id']:x for x in read(A/'VALIDATION.json')['checks']};summary=[]
md=['# Vollständige gespeicherte Lesungen und ihre Widersprüche','','Dies sind acht gescheiterte Stichproben aus vier grammatisch möglichen Systemen. Andere Karten bleiben offen. Alle Wörter und Varianten bleiben sichtbar; keine Bedeutungsbestätigung.']
for r in rows:
    if r['status']!='SAT':continue
    md+=['',r['id']+': '+r['paragraph_ids'][1],'']
    for wi,w in enumerate(r['witnesses']):
        md+=['','## Karte '+str(wi),'','| Form | Wert |','|---|---|']
        md += ['| '+k+' | '+v+' |' for k,v in sorted(w['aliases'].items())]
        for pi,parsed in enumerate(w['parses']):
            p=panel[r['system'][pi]];md+=['','### '+p['id'],'','| Gruppen | Vollständiger Wortlaut | Hypothetische Aussage |','|---|---|---|']
            for c in parsed:md.append('| '+str(c['start']+1)+'–'+str(c['end'])+' | '+' '.join(p['words'][c['start']:c['end']])+' | '+clause(c)+' |')
        md+=['','| Variante | Einstellungen | Ausgangsabsatz | Neuer Absatz | Vollständiger gemeinsamer Inhalt |','|---|---|---|---|---|']
        def description(p):
            return p.get('error',p['status'])
        for v in w['meaning_check'].get('variants',[]):
            md.append('| '+str(v['variant_index'])+' | '+', '.join(k+'='+x for k,x in v['variant'].items())+' | '+description(v['paragraphs'][0])+' | '+description(v['paragraphs'][1])+' | '+str(v['original_full_content'])+'/'+v['status']+' |')
        summary.append(dict(system=r['id'],paragraph=r['paragraph_ids'][1],sample=wi,original_coherent=sum(v['original_full_content'] for v in w['meaning_check'].get('variants',[])),new_coherent=sum(v['paragraphs'][1]['status']=='COHERENT' for v in w['meaning_check'].get('variants',[])),shared_coherent=sum(v['status']=='COHERENT_COMMON_READING' for v in w['meaning_check'].get('variants',[])),other_maps='UNRESOLVED',independent_meaning_capacity=0))
(A/'READINGS.md').write_text('\n'.join(md)+'\n');put('SAMPLE_SUMMARY.json',summary)
with (A/'SAMPLE_SUMMARY.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(summary[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(summary)
print(json.dumps(dict(samples=len(summary),coherent=sum(x['shared_coherent'] for x in summary))))
