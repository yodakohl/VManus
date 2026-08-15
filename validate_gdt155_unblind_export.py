#!/usr/bin/env python3
"""Validate GDT155 unblind joins, chronology bindings, and output hashes."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BL=ROOT/'gdt155_blinded_diplomatic.tsv';BS=ROOT/'gdt155_blinded_abbreviation_sites.tsv';UL=ROOT/'gdt155_unblinded_lines.tsv';US=ROOT/'gdt155_unblinded_abbreviation_sites.tsv';UR=ROOT/'gdt155_unblinded_record_truth.tsv';RES=ROOT/'gdt155_unblind_export.json';OUT=ROOT/'gdt155_unblind_export_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
checks=[]
def ck(n,x,d):checks.append({'check':n,'pass':bool(x),'detail':d});assert x,(n,d)
r=json.loads(RES.read_text());bl=read(BL);bs=read(BS);ul=read(UL);us=read(US);ur=read(UR)
ck('schema',r['schema']=='GDT155_UNBLIND_EXPORT_V1',r['schema']);ck('status',r['status']=='COMMITTED_EXPANSION_TRUTH_EXPORTED_AFTER_BLIND_FREEZE',r['status']);ck('commitment_match',r['truth_commitment_match'] is True,r['truth_content_sha256']);ck('chronology',r['chronology']=={'source_freeze_commit':'d62de97','blind_analysis_commit':'99bab66','unblind_after_both':True},r['chronology'])
unblind_line_ids={x['line_id'] for x in ul}
ck('line_count',len(ul)==len(bl)==r['counts']['lines'],len(ul));ck('site_count',len(us)==len(bs)==r['counts']['sites'],len(us));ck('record_count',len(ur)==r['counts']['records'],len(ur));ck('line_join',unblind_line_ids=={x['line_id']for x in bl},len(ul));ck('site_join',{x['site_id']for x in us}=={x['site_id']for x in bs},len(us));surface={x['site_id']:x['surface_span_bare']for x in bs};ck('surface_preserved',all(surface[x['site_id']]==x['surface_span_bare']for x in us),len(us));ck('site_line_join',all(x['line_id'] in unblind_line_ids for x in us),len(us));ck('expanded_present',all(x['expanded_span']!=''for x in us),sum(x['expanded_span']!=''for x in us));ck('external_only',{x['corpus']for x in ul+us+ur}=={'STE1','NUREMBERG'},sorted({x['corpus']for x in ul+us+ur}));ck('no_voynich_locator',not({'locus','folio','physical_folio','voynich_page'}&set(ul[0])),list(ul[0]));ck('f84_flags',r['f84']=={'voynich_inputs':0,'accessed':False},r['f84'])
for p in(UL,US,UR):ck('hash_'+p.name,sha(p)==r['outputs'][p.name],r['outputs'][p.name])
copy=dict(r);want=copy.pop('result_content_sha256');ck('content_hash',csha(copy)==want,want)
v={'schema':'GDT155_UNBLIND_EXPORT_VALIDATION_V1','status':f'PASS_{len(checks)}_CHECK_UNBLIND_EXPORT_INTEGRITY','checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__)),'scope':'Published join/hash/chronology validation; source-level truth commitment was checked by the exporter and will be independently rebuilt in the final validator.'};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(v['status'])
