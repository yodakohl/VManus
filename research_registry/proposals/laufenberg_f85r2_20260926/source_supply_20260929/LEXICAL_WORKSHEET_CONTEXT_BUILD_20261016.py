#!/usr/bin/env python3
"""Bounded retrieval aid: existing exact-form profiles, not a new corpus analysis."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
BASE='LEXICAL_WORKSHEET_CONTEXT_20261016'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
worksheet=HERE/'LEXICAL_WORKSHEET_20261016.json'
x=json.loads(worksheet.read_text()); unit=next(u for u in x['units'] if u['unit_id']=='f75v_IT2a')
source=unit['original_source']; lines=source['source_unit']['lines']; columns=source['source_unit']['group_columns']
raw=[dict(zip(columns,g)) for l in lines for g in l['groups']]
assert len(raw)==77 and [l['metadata']['locus'] for l in lines]==[f'f75v.{i}' for i in range(43,50)]
forms=sorted({g['ivtff_group_raw'] for g in raw})
args=[['./vmanus-work','words','profile',*forms[i:i+16],'--json','--limit','2'] for i in range(0,len(forms),16)]
responses=[subprocess.check_output(cmd,cwd=ROOT) for cmd in args]
batches=[json.loads(v) for v in responses]
assert all(z['source_receipt']==batches[0]['source_receipt'] for z in batches)
response=b'\n'.join(responses)
result={'source_receipt':batches[0]['source_receipt'],'profiles':[p for z in batches for p in z['profiles']]}
assert {p['form'] for p in result['profiles']}==set(forms)
pat=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
profiles=[]; evidence={}
for p in result['profiles']:
 f=p['form']; it=p['editions']['IT2a']; parsed=pat.findall(f)
 refs=[]
 for e in p.get('prior_evidence',[]):
  refs.append(e['id'])
  evidence[e['id']]={k:e[k] for k in ['id','kind','sources','does_not_establish'] if k in e}
 profiles.append({'form':f,'IT_count':it['count'],'IT_selectors_with_form':it['pages_with_form'],'IT_selectors_total':it['pages_total'],'IT_currier_counts':{z['value']:z['count'] for z in it['strata']['currier']},'IT_section_counts':{z['value']:z['count'] for z in it['strata']['section']},'IT_positions':it['positions'],'IT_adjacent_pairs':it['repetition']['adjacent_pairs'],'IT_max_per_line':it['repetition']['max_per_line'],'IT_previous_exact':it['neighbors']['previous'][:2],'IT_next_exact':it['neighbors']['next'][:2],'ZL_count':p['editions']['ZL3b']['count'],'RF_count':p['editions']['RF1b']['count'],'raw_codepoint_length':len(f),'working22_unit_length':len(parsed) if ''.join(parsed)==f else None,'WE_links':refs})
profiles.sort(key=lambda p:p['form']); by={p['form']:p for p in profiles}
highlights={'frequent10':[p['form'] for p in sorted(profiles,key=lambda p:(-p['IT_count'],p['form']))[:10]],'rare6':[p['form'] for p in sorted(profiles,key=lambda p:(p['IT_count'],p['form']))[:6]],'longest6_raw_codepoints':[p['form'] for p in sorted(profiles,key=lambda p:(-p['raw_codepoint_length'],p['form']))[:6]]}
receipt=result['source_receipt'];receipt['inputs'].pop('selectors',None)
limits=['Retrieval/synthesis aid only; no new manuscript finding, lexical progress, word meaning, POS or operator assignment.','Counts are exact standalone raw forms in the exposed179-selector profile population; selector dispersion is not physical-folio dispersion. Embedded strings and alternate readers are not pooled.','Positions are source-line positions, not grammar. Repeated adjacent forms are retained; no event identity inferred.','The three optional worksheet expansions are not used. Each original whole form receives its own profile.','Length is raw Unicode codepoints; the secondary22-unit tokenizer is an analytical convention, not phonemes or a proved native alphabet. Longest selection uses raw codepoint length, ties lexical; highlight categories may overlap.','WE cards are navigation links and limits only; no historical content gloss is imported.','Global previous/next neighbor summaries are exact profile results, not independently established grammatical relations.','No new source/image admission, reserve, raw TSV parsing, statistical test, model fitting or normalized glyph forms.']
out={'status':'EXISTING_PROFILE_RETRIEVAL_AND_DIPLOMATIC_CONTEXT_ONLY','date':'2026-10-16','source_original_wrapper':source,'source_columns':columns,'source_rows':raw,'raw_group_count':77,'distinct_exact_forms':len(forms),'source_pins':[{'path':rel(worksheet),'sha256':sha(worksheet)},{'path':rel(Path(__file__).resolve()),'sha256':sha(Path(__file__).resolve())}],'profile_invocation':args,'profile_response_sha256':hashlib.sha256(response).hexdigest(),'profile_response_hash_convention':'Four bounded command stdout byte strings joined with one LF; each already includes its own terminal LF','profile_batch_sha256':[hashlib.sha256(v).hexdigest() for v in responses],'profile_source_receipt':receipt,'profiles':profiles,'highlights':highlights,'WE_navigation':sorted(evidence.values(),key=lambda e:e['id']),'limits':limits}
(HERE/(BASE+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
m=['# f75v.43–49: Originaltext und vorhandene Exaktformprofile','',f'Abrufhilfe, kein neuer Manuskriptbefund und kein lexikalischer Fortschritt. **77 originale IT2a-Gruppen; {len(forms)} verschiedene genaue Formen.** Keine optionale Aufteilung übernommen.','', '## Diplomatischer Text','', '`|` = DEFINITE_SPACE; [LINE_START]/[LINE_END] sind gespeicherte Ränder. G-Nummern zusammen mit IT2a und Locus ergeben die vollständige Quell-ID. JSON bewahrt jede originale Gruppe und beide Separatorfelder.','']
sep={'DEFINITE_SPACE':' | ','LINE_END':' [LINE_END]','UNCERTAIN_SMALL_SPACE':' ~ ','DRAWING_INTERRUPTION':' [DRAWING_INTERRUPTION] '}
for l in lines:
 md=l['metadata'];gg=l['groups'];m.extend([f"**{md['locus']} — PS={md['paragraph_start']}, PE={md['paragraph_end']}**",'', '[LINE_START] '+' '.join([])])
 m[-1]='[LINE_START] '+''.join(f"G{int(g[1]):03d} `{g[2]}`"+sep.get(g[4],f' [{g[4]}] ') for g in gg);m.append('')
m+=['## Auswahl für manuelles Nachdenken','','Auswahl ausschließlich innerhalb der Originalformen dieser Passage; Häufigkeiten stammen aus dem gesamten zugelassenen Profilbestand. Bei Gleichstand alphabetisch, Kategorien dürfen sich überschneiden.','']
for key,title in [('frequent10','10 häufigste'),('rare6','6 seltenste'),('longest6_raw_codepoints','6 längste nach Roh-Codepoints')]:
 m += [f"**{title}:** "+'; '.join(f"`{f}` (IT {by[f]['IT_count']}; Länge {by[f]['raw_codepoint_length']}/{by[f]['working22_unit_length']} Roh/22)" for f in highlights[key]),'']
m+=['## Alle Exaktformen, jeweils einmal','','IT-Dispersion zählt Selektoren, keine physischen Blätter. A/B und Abschnittswerte sind genaue IT-Anzahlen. Position = Anfang/Mitte/Ende/allein; Wiederholung = benachbarte Paare / Maximum je Locus. ZL/RF sind getrennte Alternativlesungen.','', '| Form | IT | Selektoren | A/B | Abschnitte | Position | Wiederholung | ZL | RF | Länge Roh/22 | Vorher (2) | Nachher (2) | WE |','|---|---:|---:|---|---|---|---|---:|---:|---|---|---|---|']
def neigh(v):return ', '.join(f"{z['form']}:{z['count']}" for z in v) or '—'
for p in profiles:
 pos=p['IT_positions'];m.append('| '+ ' | '.join([f"`{p['form']}`",str(p['IT_count']),f"{p['IT_selectors_with_form']}/{p['IT_selectors_total']}",'/'.join(str(p['IT_currier_counts'].get(k,0)) for k in ['A','B']),', '.join(f'{k}:{v}' for k,v in p['IT_section_counts'].items()),'/'.join(str(pos[k]) for k in ['start','middle','end','single']),f"{p['IT_adjacent_pairs']}/{p['IT_max_per_line']}",str(p['ZL_count']),str(p['RF_count']),f"{p['raw_codepoint_length']}/{p['working22_unit_length']}",neigh(p['IT_previous_exact']),neigh(p['IT_next_exact']),', '.join(p['WE_links'])])+' |')
m+=['','## Quellen und Grenzen','',f"Original und vollständige Daten: [{BASE}.json]({BASE}.json). Profilaufruf: `vmanus-work words profile` für genau die {len(forms)} ursprünglichen Formen, `--json --limit 2`. Profil-Bytehash: `{out['profile_response_sha256']}`.",'','Die22-Arbeitseinheiten sind `a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh`. Keine Lautwerte.','']
for e in out['WE_navigation']:
 links=[]
 for s in e.get('sources',[]):
  links.append(f"[{s['path']}](../../../../{s['path']})")
 m += [f"**{e['id']}** ({e.get('kind','')}): "+'; '.join(links)+'. Grenzen: '+'; '.join(e.get('does_not_establish',[])),'']
m+=['Alle Formwerte bleiben unassigned. Die drei optionalen Zerlegungen, Altglossen und grammatische Rollen sind keine Fakten dieses Dokuments.','']
(HERE/(BASE+'.md')).write_text('\n'.join(m))
print(json.dumps({'status':'written','raw_groups':77,'exact_forms':len(forms),'highlights':highlights,'profile_response_sha256':out['profile_response_sha256'],'files':[rel(HERE/(BASE+ext)) for ext in ['.json','.md']]}))
