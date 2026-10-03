#!/usr/bin/env python3
"""Registered source windows and exact four-grade prior accounting; no target reads."""
import argparse,csv,hashlib,html,itertools,json,re,subprocess,urllib.request
from collections import Counter
from fractions import Fraction
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
OLD=ROOT/'experiments/yolo/gdt1057_quality_full_source_orientation'
URL='https://celt.ucc.ie/published/G600005.html'
RAW_SHA='cb62ae0241ff61b7d0e35954df2041f16e97d9fc2a29cadf05d76111b91faabd'
PINS={'SOURCE_ENTRIES.tsv':'a764e68731edcaee5c7b9ddb15bd11828879bb0ff2dcd3b91d7f5f63503661ab','MANUAL_AUDIT.tsv':'c0fd4c7c71fdfadf1127574bafea1a6d04cef461648bad1246f2db65619fcf4f'}
FORMS=['DAN','DAIN','DAIIN','DAIIIN'];COUNTS=[2,4,35,2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def h(data):return hashlib.sha256(data).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def read(p):return json.loads(p.read_text())
def exact(x):return {'numerator':x.numerator,'denominator':x.denominator,'value':float(x)}
def extract(raw):
    source=raw.decode('latin1');heads=list(re.finditer(r'<h2>An Irish Materia Medica</h2>',source));assert len(heads)==3
    start=heads[2].end();starts=list(re.finditer(r'<p>\s*(\d+)\.\s*',source[start:],re.I));assert len(starts)==286
    rows=[]
    for i,m in enumerate(starts):
        begin=start+m.end();end=start+starts[i+1].start() if i+1<len(starts) else len(source)
        opening=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',source[begin:end]))).strip()[:320]
        rows.append({'ordinal':i+1,'source_number':m.group(1),'source_line':source.count('\n',0,start+m.start())+1,'opening':opening,'opening_sha256':h(opening.encode()),'opening_length':len(opening)})
    return rows

def prepare(a):
    assert a.registered_commit and re.fullmatch(r'[0-9a-f]{7,40}',a.registered_commit)
    bindings={}
    for rel in ['METHOD.md','PREREGISTRATION.md','src/run.py']:
        path=EXP/rel;repo=str(path.relative_to(ROOT));committed=subprocess.run(['git','show',a.registered_commit+':'+repo],cwd=ROOT,check=True,capture_output=True).stdout
        assert h(committed)==sha(path),'registered bytes differ: '+rel;bindings[rel]=sha(path)
    for name,pin in PINS.items():assert sha(OLD/'artifacts'/name)==pin
    a.runtime.mkdir(parents=True,exist_ok=True)
    source=a.source or OLD/'runtime/G600005.html'
    if source.exists():raw=source.read_bytes()
    else:
        with urllib.request.urlopen(URL,timeout=30) as f:raw=f.read()
    assert h(raw)==RAW_SHA,'source hash changed; no extraction'
    (a.runtime/'G600005.html').write_bytes(raw)
    rows=extract(raw)
    with (OLD/'artifacts/SOURCE_ENTRIES.tsv').open(newline='') as f:old=list(csv.DictReader(f,delimiter='\t'))
    with (OLD/'artifacts/MANUAL_AUDIT.tsv').open(newline='') as f:audit=list(csv.DictReader(f,delimiter='\t'))
    assert len(old)==286
    for r,o in zip(rows,old):
        for k in ['ordinal','source_number','source_line','opening_sha256']:assert str(r[k])==o[k],(r['ordinal'],k)
    accepts={int(r['ordinal']):r for r in audit if r['decision']=='ACCEPT'};assert len(accepts)==210
    windows=[];metadata=[]
    for r in rows:
        if r['ordinal'] not in accepts:continue
        accepted=accepts[r['ordinal']];assert accepted['source_number']==r['source_number'];thermal,humidity=accepted['auto_category'].split('_')
        assert thermal in ['hot','cold'] and humidity in ['dry','moist']
        meta={k:v for k,v in r.items() if k!='opening'};meta.update(thermal=thermal,humidity=humidity)
        metadata.append(meta);windows.append({**meta,'opening':r['opening']})
    assert sum(r['humidity']=='dry' for r in windows)==177
    dump(a.runtime/'windows.json',{'source_sha256':RAW_SHA,'windows':windows})
    output={'status':'SOURCE_WINDOWS_READY_NOT_ANNOTATED','experiment':'GDT1167','registered_commit':a.registered_commit,'bindings':bindings,'source_url':URL,'source_sha256':RAW_SHA,'legacy_metadata_pins':PINS,'detected_starts':286,'accepted_entries':210,'required_axis_rows_per_reader':420,'primary_dry_entries':177,'runtime_windows_sha256':sha(a.runtime/'windows.json'),'entries':metadata,'copyright_policy':'Full windows remain runtime-only; no public source prose'}
    dump(EXP/'artifacts/SOURCE_RECEIPT.json',output)
    print(json.dumps({k:output[k] for k in ['status','detected_starts','accepted_entries','primary_dry_entries','runtime_windows_sha256']}))

def annotation_rows(obj,entries):
    result={}
    for r in obj['rows']:
        key=(r['ordinal'],r['axis']);assert key not in result and r['ordinal'] in entries and r['axis'] in ['thermal','humidity']
        e=entries[r['ordinal']];assert r['quality']==e[r['axis']]
        assert r['status'] in ['FIXED','UNKNOWN','INTERVAL'] and r.get('subgrade') in [None,'BEGIN','MIDDLE','END']
        if r['status']=='FIXED':assert type(r['grade']) is int and r['grade'] in [1,2,3,4] and r.get('source_offset') is not None
        else:assert r['grade'] is None
        if r.get('source_offset') is not None:
            bounds=r['source_offset'];assert len(bounds)==2 and all(type(z) is int for z in bounds) and 0<=bounds[0]<bounds[1]<=e['opening_length']
        assert isinstance(r['reason'],str) and r['reason'].strip()
        result[key]=r
    assert set(result)=={(i,axis) for i in entries for axis in ['thermal','humidity']}
    return result

def scientific(r):return tuple(r.get(k) for k in ['quality','status','grade','subgrade'])
def score(a):
    receipt=read(EXP/'artifacts/SOURCE_RECEIPT.json')
    for rel,pin in receipt['bindings'].items():assert sha(EXP/rel)==pin
    entries={r['ordinal']:r for r in receipt['entries']};assert len(entries)==210
    paths=[a.annotations_a,a.annotations_b,a.adjudication];assert all(p is not None for p in paths)
    # Explicit root freeze required before reading the annotation payloads.
    lock=read(a.annotation_lock);assert lock['status']=='ALL_ANNOTATIONS_FROZEN'
    for p in paths:assert lock['bindings'][str(p.relative_to(EXP))]==sha(p)
    ra=annotation_rows(read(paths[0]),entries);rb=annotation_rows(read(paths[1]),entries);ad=read(paths[2]);final=annotation_rows(ad,entries)
    disagreements={k for k in ra if scientific(ra[k])!=scientific(rb[k])}
    required=disagreements|{k for k in final if scientific(final[k])!=scientific(ra[k]) or scientific(final[k])!=scientific(rb[k])}
    notes={(r['ordinal'],r['axis']):r for r in ad['disagreements']};assert len(notes)==len(ad['disagreements']) and set(notes)==required
    assert all(isinstance(r['reason'],str) and r['reason'].strip() for r in notes.values())
    qualities={}
    for quality in ['dry','hot','cold','moist']:
        rs=[r for r in final.values() if r['quality']==quality];counts=[sum(r['status']=='FIXED' and r['grade']==g for r in rs) for g in [1,2,3,4]];unknown=len(rs)-sum(counts)
        qualities[quality]={'entries':len(rs),'known':sum(counts),'unknown':unknown,'grade_counts':counts,'known_grade_proportions':[exact(Fraction(c,sum(counts))) for c in counts] if sum(counts) else None,'unknown_fraction':exact(Fraction(unknown,len(rs))),'grade_bounds':[{'grade':g,'lower':exact(Fraction(counts[g-1],len(rs))),'upper':exact(Fraction(counts[g-1]+unknown,len(rs)))} for g in [1,2,3,4]]}
    assert qualities['dry']['entries']==177
    dry=qualities['dry'];table=[]
    if dry['known']:
        for perm in itertools.permutations([1,2,3,4]):
            target=[0]*4
            for c,g in zip(COUNTS,perm):target[g-1]=c
            tv=sum(abs(Fraction(target[i],43)-Fraction(dry['grade_counts'][i],dry['known'])) for i in range(4))/2
            table.append({'mapping':dict(zip(FORMS,perm)),'permutation':list(perm),'target_grade_counts':target,'tv':exact(tv)})
        table.sort(key=lambda r:(Fraction(r['tv']['numerator'],r['tv']['denominator']),r['permutation']))
        vals=[Fraction(r['tv']['numerator'],r['tv']['denominator']) for r in table]
        for r,v in zip(table,vals):r['rank']=1+sum(t<v for t in vals);r['best']=v==min(vals)
        original=next(r for r in table if r['permutation']==[1,2,3,4]);best=[r for r in table if r['best']]
        status='ORIGINAL_MAPPING_COMPATIBLE_ONLY' if original['best'] else 'ORIGINAL_NUMERAL_PRIOR_WEAKENED'
    else:original=None;best=[];status='NO_KNOWN_DRY_GRADES'
    result={'experiment':'GDT1167','status':status,'source_sha256':RAW_SHA,'source_receipt_sha256':sha(EXP/'artifacts/SOURCE_RECEIPT.json'),'annotation_bindings':{str(p.relative_to(EXP)):sha(p) for p in paths},'annotation_lock_sha256':sha(a.annotation_lock),'rows_per_reader':420,'A_B_disagreements':len(disagreements),'adjudication_records':len(notes),'qualities':qualities,'target_forms':FORMS,'target_counts':COUNTS,'permutations':table,'original_mapping':original,'best_mappings':best,'DAIIN_best_grades':sorted({r['mapping']['DAIIN'] for r in best}),'confirmed_words':0,'new_target_access':0,'claim_ceiling':'Conditional source frequency prior only; no new numeral/quality meaning, source identity, significance or repaired earlier model'}
    dump(EXP/'artifacts/RESULT.json',result)
    lines=['# GDT1167 complete fixed numeral comparison','','All24 permutations are retained. A preferred frequency permutation is not a translation.','','|Rank|DAN|DAIN|DAIIN|DAIIIN|Exact TV|TV decimal|Best|','|---:|---:|---:|---:|---:|---|---:|---|']
    for r in table:lines.append('|'+ '|'.join(map(str,[r['rank'],*r['permutation'],str(r['tv']['numerator'])+'/'+str(r['tv']['denominator']),f"{r['tv']['value']:.9f}",r['best']]))+'|')
    (EXP/'CANDIDATE_TABLE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':status,'dry':dry,'original_rank':None if original is None else original['rank'],'best_mappings':len(best),'DAIIN_best_grades':result['DAIIN_best_grades']}))

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True,choices=['prepare','score']);p.add_argument('--runtime',type=Path);p.add_argument('--source',type=Path);p.add_argument('--registered-commit');p.add_argument('--annotations-a',type=Path);p.add_argument('--annotations-b',type=Path);p.add_argument('--adjudication',type=Path);p.add_argument('--annotation-lock',type=Path);a=p.parse_args()
    for key in ['runtime','source','annotations_a','annotations_b','adjudication','annotation_lock']:
        value=getattr(a,key)
        if value is not None:setattr(a,key,value.resolve())
    if a.stage=='prepare':assert a.runtime is not None;prepare(a)
    else:assert a.annotation_lock is not None;score(a)
if __name__=='__main__':main()
