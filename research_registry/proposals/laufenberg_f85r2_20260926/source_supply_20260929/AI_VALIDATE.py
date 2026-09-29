#!/usr/bin/env python3
"""Local receipt/text completeness checks; no iconographic or semantic validation."""
import hashlib,json
from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parent
R=D.parents[3]
def read(n):return json.loads((D/n).read_text())
checks=[]
def ck(n,v):
 checks.append({'check':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
s=read('AI_COMPLETE_SOURCE.json');r=read('AI_SOURCE_RECEIPTS.json');i=read('AI_INPUTS.json')
ck('two_complete_units',s['units']==['fol.5r','fol.5v'])
ck('six_stanzas',len(s['stanzas'])==6)
ck('all48_lines',sum(len(x['lines']) for x in s['stanzas'])==48)
ck('unique_complete_stanza_ids',[x['id'] for x in s['stanzas']]==['5r-A','5r-B','5r-C','5v-A','5v-B','5v-C'])
for x in s['stanzas']:
 ck(x['id']+'eight_lines',len(x['lines'])==8)
 ck(x['id']+'sense_and_uncertainty',bool(x['sense']) and bool(x['uncertainties']))
ck('explicit_nondiplomatic',s['status']=='COMPLETE_LOCAL_WORKING_READING_NOT_DIPLOMATIC')
ck('all_upper_diagram_lines',len(s['upper_5r_inscription']['working_lines'])==8)
ck('all_lower_number_positions',set(s['lower_5r_labels']['uncertain_stack_labels'])=={'left','right','bottom'})
ck('whole_before_details','whole folios before' in s['reading_method'])
for q in r['acquired_or_copied']:
 p=R/q['file'];ck('receipt_hash:'+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==q['sha256']);ck('receipt_size:'+p.name,p.stat().st_size==q['bytes'])
for q in i['source_files']:ck('predecessor_hash:'+q['path'],hashlib.sha256((R/q['path']).read_bytes()).hexdigest()==q['sha256'])
for name,size in [('AI_MORGAN_005r.jpg',(435,600)),('AI_MORGAN_005v.jpg',(424,600)),('AI_MORGAN_005ra.jpg',(510,600)),('AI_MORGAN_005rb.jpg',(530,600)),('AI_MORGAN_005va.jpg',(475,600))]:
 im=Image.open(D/name);ck('actual_JPEG:'+name,im.format=='JPEG');ck('dimensions:'+name,im.size==size)
for n,folio in [('AI_MORGAN_005r_CATALOGUE.html','5r'),('AI_MORGAN_005v_CATALOGUE.html','5v')]:
 t=(D/n).read_text();ck('catalogue_identity:'+folio,('MS M.721 fol. '+folio) in t);ck('catalogue_date:'+folio,'second half of 15th century' in t)
md=(D/'AI_REVIEW.md').read_text()
for phrase in ['no new RAW card','not a dated colophon','not a claim that such historical witnesses are absent','IDEA672','IDEA633','IDEA743','No new Voynich','No ideas add','uncertain']:
 ck('limit:'+phrase,phrase in md)
ck('no_full_moon_equivalence','No full-Moon/Sun facial equivalence established' in s['claim_ceiling'])
print(json.dumps({'status':'PASS','kind':'receipt, completeness and stated-limit checks only; not semantic/image validation','checks':len(checks),'details':checks,'new_idea_cards':0,'whole_source_folios':2,'source_poem_lines':48},ensure_ascii=False,indent=2))
