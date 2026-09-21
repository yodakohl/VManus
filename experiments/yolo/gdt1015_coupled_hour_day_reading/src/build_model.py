"""Serialize the first explicit exploratory draft; no search or outcome computation."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
source=json.loads((P/'src/SOURCE.json').read_text())
entries='''kolchdy|DEFINE|als Definition
qokedy|DAY|vollständige Tag-Nacht-Einheit
qopol|SPAN|Zeitspanne
qotedor|COMPLETE|abgeschlossen
chopchedy|RETURN_INTERVAL|Wiederkehrintervall
qotal|INCLUDES|schließt ein
chedy|DAYLIGHT|helle Tageszeit
kam|BOUNDARY|Grenze
otedy|ORDER|Folge
qodched|SEVEN|sieben
olqo|SUCCESSIVE|aufeinanderfolgend
dar|MEMBER|Glied
checkho|CYCLIC|kreisförmig
lolol|RETURN_START|zum Anfang zurückkehren
okal|AFTER|nach
okarchedy|LAST_MEMBER|letztes Glied
tcheol|WHEN|wenn
olchedy|START|Beginn
qokeedy|HOUR|eine gezählte Stunde
qotedy|ADVANCE|weiterschreiten
chedar|BY|gemäß
cheey|NEXT_MEMBER|nächstes Glied der genannten Folge
lchey|NOT|nicht
solarol|RESET|neu ansetzen
r|THEREFORE|daher
olchy|NAME|Name
qokal|DERIVED|abgeleitet
chey|FROM|von
qokain|INITIAL_POINT|Ausgangspunkt
deeedy|SELECT|wähle
qokeey|FIRST|erster
qokaiin|RULER|herrschender Planet
kedy|COUNT_WITH|mit einrechnen
lchedy|NIGHT|Nacht
lkeedy|ASSIGNED_TO|zugeordnet zu
dy|THIS|dieser: typabhängiger Rückverweis
daiin|TWENTY_FOUR|vierundzwanzig
chdy|CONSISTS_OF|besteht aus
or|REDUCE|vereinfache
ol|REMOVE|ziehe ab
s|CYCLE|Kreis
aiin|THREE|drei
ra|DAY_COUNT|Tageszählung
dam|REMAINDER|Rest
dshedy|NOW|nun
qoteey|COUNT_THROUGH|durchzählen
qokeeey|WHOLE|ganz
lteedy|UNTIL|bis
ralchey|AFTER_LAST_HOUR|nach der letzten Stunde
polched|OTHER_METHOD|andere Rechnung
otain|SKIP|überspringe
shedy|ONE_MEMBER|ein Glied
dal|THEN_AFTER|danach
ykeey|UNSKIPPED|nicht übersprungen
l|IN|in
araiin|REACH|erreiche
ory|SAME|gleich
okain|METHOD|Rechnung
char|AGREES_IN|stimmt überein hinsichtlich
lchy|RULERSHIP|Herrschaftszuordnung'''
lex={}
for row in entries.splitlines():
    word,value,de=row.split('|');lex[word]={'value':value,'german':de,'origin':'RAW379_HYPOTHESIS' if word in source['old_hypotheses'] else 'NEW_GUESS'}
assert set(lex)==set(source['words']) and len(lex)==60
spec=[
('C01',1,8,'DAY_DEFINITION','Als vollständiger Tag gilt ein abgeschlossenes Wiederkehrintervall, das die helle Tageszeit bis zu ihrer Grenze einschließt.',{'day_register':'DAY','daylight_is_part':True,'day_boundary':'unspecified; no sunrise or equal hour lengths asserted'}),
('C02',9,16,'CYCLE_DEFINITION','Die Folge hat sieben aufeinanderfolgende Glieder in einem Kreis; nach dem letzten kehrt sie zum Anfang zurück.',{'cycle_length_word':10,'cycle_register':'H'}),
('C03',17,24,'HOUR_TRANSITION','Wenn eine folgende Stunde beginnt, schreite zum nächsten Glied fort und setze nicht neu an.',{'domain':'successive ordinal hours after the initial hour','advance_word':20,'successor_word':22,'scope':'all hours, unless explicitly overridden by a rival'}),
('C04',25,29,'NAME_RULE','Daher ist der Name vom Ausgangspunkt abgeleitet.',{'subject':'most recent DAY register','name_reference':'ruler at initial hour'}),
('C05',30,33,'INITIAL_RULER','Wähle den ersten Herrscher zu Beginn.',{'initial_phase':'free among all seven, not a recovered planetary name','START':'initial HOUR of DAY'}),
('C06',34,39,'NIGHT_INCLUDED','Rechne die Nacht in den Tag mit ein; eine Stunde ist einem Herrscher zugeordnet.',{'NIGHT':'part of DAY, not added outside the complete day','HOUR':'general member of DAY','RULER':'assigned by H'}),
('C07',40,43,'DAY_LENGTH','Dieser [Tag] besteht aus vierundzwanzig von diesen [Stunden].',{'THIS_40':'most recent reference of type DAY','THIS_43':'most recent reference of type HOUR','count_word':41,'same_word_same_function':'typed most-recent demonstrative; not same individual referent'}),
('C08',44,47,'NIGHT_SUCCESSION','Auf eine Nachtstunde folgt eine Stunde mit dem nächsten Glied.',{'HOUR_44':'source hour restricted to NIGHT','HOUR_46':'following hour','NEXT_MEMBER_47':'same successor as C03','night_count':'not specified by target; rival audit considers all 1..23 daylight-hour counts'}),
('C09',48,55,'REDUCTION','Daher vereinfache: Ziehe drei Kreise von der Tageszählung ab; es bleibt der Rest.',{'cycles_word':52,'cycle':'C02','day_count':'C07','well_formed_remainder':'zero or greater and less than cycle length','note':'Euclidean arithmetic is an analyst reconstruction, not Dio wording'}),
('C10',56,63,'METHOD_A','Zähle nun von der hellen Tageszeit durch den ganzen Tag bis zur Stunde nach der letzten.',{'starts_at':'initial daylight hour of abstract DAY','end_word':63,'hour_indices':'initial hour 0; last 23; after-last 24','daylight_initial':'extra model assumption, not stated by Dio; no physical sunrise claim','stores':'method_A ruler after complete day'}),
('C11',64,75,'METHOD_B','Andere Rechnung: Überspringe ein Glied und ein Glied; wähle danach gemäß dem ersten nicht übersprungenen Glied im Kreis und erreiche dieselbe Herrschaftszuordnung.',{'start':'same initial ruler as METHOD_A','unit_words':[66,67],'repetition':'two separate unit operands under SKIP; neither omitted','selection':'first unskipped is the next member after both skipped members','same_reference':'ruler stored by method_A, not absolute hour identity','stores':'method_B ruler'}),
('C12',76,80,'METHOD_COMPARISON','Rechnung und Rechnung stimmen hinsichtlich der Herrschaft einer Stunde überein.',{'METHOD_76':'most recent method (B)','METHOD_78':'preceding distinct method (A)','HOUR':'generic type, not identical absolute ordinal hour','projection_word':80,'note':'Distinct-register binding is explicitly assumed; a same-register rival is retained.'})]
clauses=[]
for cid,a,b,kind,de,binding in spec:
    raw=source['words'][a-1:b]
    clauses.append(dict(id=cid,start=a,end=b,kind=kind,words=raw,pattern=[lex[w]['value'] for w in raw],german=de,binding=binding))
model={
 'experiment':'GDT1015','version':'v01','phase':'EXPLORATORY_DRAFT_NOT_INDEPENDENT_TRANSLATION',
 'source':'src/SOURCE.json','lexicon':lex,'clauses':clauses,
 'grammar':{'clause_boundaries':'all twelve spans explicitly supplied by analyst; not recovered punctuation','productions':'one exact value-pattern per named clause; twelve productions, each observed only once','within_clause':'ordered role slots given by each pattern and binding object','scope':'C01-C09 establish a persistent model; C10/C11 calculate from the same initial ruler; C12 compares projections','no_omitted_groups':True,'no_silent_reset':True,'no_per_occurrence_lexical_change':True,'global_word_value_does_not_mean_global_object_identity':True,'components':'all sixty forms are opaque; no productive component meanings claimed'},
 'arithmetic':{'cycle_length':7,'day_hours':24,'complete_cycles_to_remove':3,'skip_operands':[1,1],'initial_phase_domain':list(range(7)),'label_order_for_source_example':['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon'],'hour_numbering':'offset 0 is first hour; hour after last of day is offset 24'},
 'candidates':[
  {'id':'PRIMARY','overrides':{},'word_changes':{},'grammar_changes':[],'expected_distinction':'two derivations and explicit NEXT_MEMBER agree for all seven phases'},
  {'id':'AT_LAST','overrides':{'method_a_endpoint':'last'},'word_changes':{'ralchey':'LAST_HOUR'},'grammar_changes':[],'expected_distinction':'ends at offset 23 instead of 24; compare with two skips then first unskipped'},
  {'id':'AFTER_FIRST_UNSKIPPED','overrides':{'selection':'one_past_first_unskipped'},'word_changes':{},'grammar_changes':['C11 BY FIRST UNSKIPPED selects the successor of the first unskipped member; FIRST remains ordinal first'],'expected_distinction':'alternative is offset 4 instead of 3'},
  {'id':'ONE_REFERENT_FOR_DOUBLE','overrides':{'double_unit':'same_skipped_member'},'word_changes':{},'grammar_changes':['C11 two ONE_MEMBER tokens are appositive references to one skipped member, not additive operands'],'expected_distinction':'alternative is offset 2 instead of 3'},
  {'id':'SAME_METHOD_REFERENCE','overrides':{'comparison':'B_B'},'word_changes':{},'grammar_changes':['C12 both METHOD slots resolve to latest method B'],'expected_distinction':'final comparison becomes tautological; C11 SAME still refers to method A'},
  {'id':'NIGHT_REVERSE','overrides':{'night_direction':-1},'word_changes':{},'grammar_changes':['C03 forward scope only daylight; C08 NIGHT opens reversed local succession for shared NEXT_MEMBER; C06 includes night in same day'],'expected_distinction':'different active direction, not changed word value; audit every unspecified daylight count 1..23'},
  {'id':'NIGHT_RESET','overrides':{'night_reset':True},'word_changes':{},'grammar_changes':['C03 NOT RESET applies only within daylight/night blocks; C08 first NIGHT hour returns to initial ruler, then local NEXT continues; C06 includes night in same day'],'expected_distinction':'extra boundary reset not lexically written; audit every unspecified daylight count 1..23'}
 ],
 'unproved_assumptions':[
  'All five inherited whole meanings remain hypotheses; fifty-five further whole meanings are invented in this draft.',
  'Twelve clause boundaries and twelve exact construction templates are supplied, not inferred from independent grammar.',
  'Numbers seven, twenty-four, three, one are assigned to qodched, daiin, aiin, shedy without independent numeral evidence.',
  'Both dy references require typed grammar; this form has one reference function but different typed referents.',
  'The absolute planetary names and initial ruler are not encoded by independently read target words.',
  'A daylight initial abstract hour and the treatment of its endpoint are supplied by the model, not native-image evidence.',
  'Repeated shedy is interpreted compositionally as two units, whereas repeated METHOD is bound to distinct registers.',
  'All exact templates could overfit one paragraph. No second paragraph, independent held leaf or meaning evidence is supplied.',
  'A different cyclic institution or purely abstract cyclic calculation is observationally equivalent here; astronomy is not selected.',
  'The manuscript-wide word-formation observations are not explained by this opaque lexicon.'
 ],
 'planned_checks':{'complete_coverage':80,'global_types':60,'all_phases':7,'night_scope_daylight_counts':list(range(1,24)),'all_label_permutations':5040,'independent_engine':'explicit list walking with no import of primary calculation','control':'no control of entire source/gloss/grammar search; no significance','meaning_confirmation_capacity':0}
}
(P/'MODEL_v01.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
lines=['# Vollständiger hypothetischer Leseentwurf v01','',
'Explorative Konstruktion für alle 80 Gruppen von f82r.11–19. Keine bestätigte Übersetzung. Fünf alte Vermutungen bleiben unverändert; 55 Wortwerte und zwölf Satzkonstruktionen kommen als neue Annahmen hinzu. Alle Formen bleiben zunächst unzerlegt.','',
'## Zusammenhängender Vorschlag','']+[c['german'] for c in clauses]+['','## Jede geschriebene Gruppe','',
'|Position|Zeile|Rohform|Einheitlicher Wert|Deutsche Arbeitsglosse|Satz|','|---|---|---|---|---|---|']
pos=0
for record in source['records']:
 for word in record['raw'].split():
  pos+=1;c=next(c for c in clauses if c['start']<=pos<=c['end']);e=lex[word]
  lines.append(f"|{pos}|{record['locus']}|{word}|{e['value']}|{e['german']}|{c['id']}|")
lines+=['','## Vollständige Satzkonstruktionen und Bindungen','']
for c in clauses:
 lines += [f"### {c['id']} — Gruppen {c['start']}–{c['end']}",'', '`'+' '.join(c['pattern'])+'`','',c['german'],'', 'Bindungen: `'+json.dumps(c['binding'],ensure_ascii=False,sort_keys=True)+'`.','']
lines+=['## Offene Annahmen','']+['- '+x for x in model['unproved_assumptions']]
lines+=['','## Vor dem Test festgelegte Alternativen','']
for c in model['candidates']:
 lines += ['- **'+c['id']+'**: '+c['expected_distinction']+'; Wortänderungen `'+json.dumps(c['word_changes'])+'`; Grammatikänderungen `'+json.dumps(c['grammar_changes'],ensure_ascii=False)+'`.']
(P/'READING_v01.md').write_text('\n'.join(lines)+'\n')
print('Saved complete v01 draft, without executing its consequences.')
if __name__=='__main__': pass
