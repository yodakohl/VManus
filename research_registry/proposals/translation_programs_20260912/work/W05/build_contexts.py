"""Readable full run census and complete alternate raw lines for every case locus."""
import csv,json
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent/'W02'
def read(name):return list(csv.DictReader((E/name).open(),delimiter='\t'))
def table(name,rows):
    with (E/name).open('w') as out:
        w=csv.DictWriter(out,fieldnames=list(rows[0])+['row_status'],delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)
cases=read('ALL_VERB_RUNS.tsv');args=read('ARGUMENTS.tsv')
source=json.loads((P/'SOURCE.json').read_text())
alt=json.loads((P/'ALTERNATE_LINES.json').read_text())['readings']
loci={r['locus'] for r in cases}
rows=[]
for ed,lines in alt.items():
    for line in lines:
        locus=line['metadata']['locus']
        if locus not in loci:continue
        local=[r for r in cases if r['edition']==ed and r['locus']==locus]
        rows.append(dict(edition=ed,locus=locus,raw_line=' '.join(g['ivtff_group_raw'] for g in line['groups']),
            all_group_separators=';'.join(g['right_separator'] for g in line['groups']),
            maximal_runs=';'.join(r['run']+'='+r['verbs'] for r in local),
            J_eligible=';'.join(r['run'] for r in local if r['J_status']=='SHARED_EXPLICIT_RIGHT'),
            M_eligible=';'.join(r['run'] for r in local if r['M_status']=='SHARED_EXPLICIT_RIGHT')))
table('COMPLETE_ALTERNATE_CASE_LINES.tsv',rows)
text=['# Sämtliche 16 primären maximalen Verbfolgen','',
    'B ist W04 C/R. J benötigt ein unmittelbar folgendes Material; M erlaubt nur die vorab festgelegten bekannten Modifikatorrollen dazwischen. Beide sind unbestätigte Syntaxvorschläge. Jeder Patient ist die konkrete geschriebene Nennung, keine unabhängig erkannte Charge.','',
    '| Folge | Rohzeile | J / M | B-Patienten → M-Patienten | Offene Argumente in M |',
    '|---|---|---|---|---|']
for c in cases:
    if c['edition']!='ZL3b':continue
    text.append('| '+c['run']+' | `'+c['raw_line']+'` | '+c['J_status']+' / '+c['M_status']+
        ('; Material '+c['M_primary_form'] if c['M_primary_form'] else '')+' | '+c['B_patients']+' → '+c['M_patients']+
        ' | '+(c['M_debts'].replace('|',';') or 'keine der markierten Argumentlücken; Bedeutungen/Grammatik bleiben angenommen')+' |')
(E/'ALL_CASES.md').write_text('\n'.join(text)+'\n')
# Include unchanged paragraphs explicitly; all commands remain in the full rendering.
paragraphs=[]
for t in source['targets']:
    p=t['hosts']['ZL3b'][0]
    local=[c for c in cases if c['edition']=='ZL3b' and c['paragraph']==p['id']]
    paragraphs.append(dict(paragraph=p['id'],line_count=len(p['lines']),group_count=sum(len(l['words']) for l in p['lines']),
        all_runs=';'.join(c['run'] for c in local),
        J_eligible=';'.join(c['run'] for c in local if c['J_status']=='SHARED_EXPLICIT_RIGHT'),
        M_eligible=';'.join(c['run'] for c in local if c['M_status']=='SHARED_EXPLICIT_RIGHT'),
        status='CONDITIONAL_REBINDING' if any(c['M_status']=='SHARED_EXPLICIT_RIGHT' for c in local) else 'UNCHANGED_FROM_W04_C_R'))
table('PARAGRAPH_COVERAGE.tsv',paragraphs)
print(json.dumps(dict(paragraphs=len(paragraphs),primary_runs=16,alternate_case_lines=len(rows),case_loci=len(loci))))
