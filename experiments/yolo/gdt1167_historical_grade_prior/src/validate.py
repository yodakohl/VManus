#!/usr/bin/env python3
"""Independent source/annotation/finite-prior accounting. No runner imports."""
import argparse
import collections
import csv
from fractions import Fraction
import hashlib
import html
import itertools
import json
from pathlib import Path
import re

SOURCE_SHA = 'cb62ae0241ff61b7d0e35954df2041f16e97d9fc2a29cadf05d76111b91faabd'


def load(path):
    return json.loads(path.read_text())


def tsv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


def reconstruct(raw):
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    text=raw.decode('latin1')
    heading='<h2>An Irish Materia Medica</h2>'
    assert text.count(heading)==3
    offset=text.rfind(heading)+len(heading)
    body=text[offset:]
    matches=list(re.finditer(r'<p>\s*(\d+)\.\s*',body,re.I))
    assert len(matches)==286
    rows=[]
    for i,m in enumerate(matches):
        stop=matches[i+1].start() if i+1<len(matches) else len(body)
        plain=html.unescape(re.sub(r'<[^>]*>',' ',body[m.end():stop]))
        opening=' '.join(plain.split())[:320]
        heat=re.findall(r'\b(?:hot|cold)\b',opening,re.I)
        wet=re.findall(r'\b(?:dry|moist|wet)\b',opening,re.I)
        category=''
        if len(heat)==len(wet)==1:
            category=heat[0].lower()+'_'+('dry' if wet[0].lower()=='dry' else 'moist')
        rows.append({'ordinal':i+1,'source_number':m.group(1),
            'source_line':text[:offset+m.start()].count('\n')+1,
            'auto_category':category,'thermal_hits':len(heat),'humidity_hits':len(wet),
            'opening_sha256':hashlib.sha256(opening.encode()).hexdigest(),'opening':opening})
    return rows


def source_check(root,rawpath):
    repo=root.parents[2]
    prior=repo/'experiments/yolo/gdt1057_quality_full_source_orientation/artifacts'
    rows=reconstruct(rawpath.read_bytes())
    saved=tsv(prior/'SOURCE_ENTRIES.tsv')
    assert len(saved)==len(rows)
    for a,b in zip(rows,saved):
        assert all(str(a[k])==v for k,v in b.items()),('prior_source_identity',a['ordinal'])
    audit=tsv(prior/'MANUAL_AUDIT.tsv')
    assert len({r['ordinal'] for r in audit})==len(audit)==213
    assert {int(r['ordinal']) for r in audit}=={r['ordinal'] for r in rows if r['auto_category']}
    accept={int(r['ordinal']) for r in audit if r['decision']=='ACCEPT'}
    assert len(accept)==210
    assert all(r['decision'] in {'ACCEPT','EXCLUDE'} for r in audit)
    assert set(range(1,293))-{int(r['source_number']) for r in rows}=={7,20,160,181,220,244}
    expected={(r['ordinal'],q) for r in rows if r['ordinal'] in accept for q in r['auto_category'].split('_')}
    assert len(expected)==420
    assert collections.Counter(q for _,q in expected)=={'hot':150,'cold':60,'dry':177,'moist':33}
    return rows,expected


def compare_permutations(counts):
    known=sum(counts.values())
    if not known:
        return []
    target=(2,4,35,2)
    scores=[]
    for perm in itertools.permutations((1,2,3,4)):
        mapped={g:Fraction(n,43) for g,n in zip(perm,target)}
        tv=sum((abs(mapped[g]-Fraction(counts.get(g,0),known)) for g in range(1,5)),Fraction())/2
        scores.append((perm,tv))
    return sorted(scores,key=lambda r:(r[1],r[0]))


def annotation_check(packet, windows, expected):
    data=packet['rows']
    assert len(data)==420
    keyed={}
    grade_terms={1:r'first|one|1st|1|I',2:r'second|two|2nd|2|II',3:r'third|three|3rd|3|III',4:r'fourth|four|4th|4|IV'}
    for row in data:
        key=row['ordinal'],row['quality']
        assert key in expected and key not in keyed,('annotation_identity',key)
        assert row['axis']==('thermal' if row['quality'] in {'hot','cold'} else 'humidity')
        assert row['status'] in {'FIXED','UNKNOWN','INTERVAL'}
        assert row['subgrade'] in {None,'BEGIN','MIDDLE','END'}
        assert isinstance(row['reason'],str) and row['reason'].strip()
        span=row['source_offset']
        if span is not None:
            assert isinstance(span,list) and len(span)==2
            begin,end=span
            assert type(begin)==type(end)==int and 0<=begin<end<=len(windows[row['ordinal']])
        if row['status']=='FIXED':
            assert type(row['grade'])==int and row['grade'] in range(1,5) and span is not None
            evidence=windows[row['ordinal']][span[0]:span[1]]
            assert re.search(r'\b(?:'+grade_terms[row['grade']]+r')\b',evidence,re.I),('grade_not_in_evidence_span',key,row['grade'],span)
        else:
            assert row['grade'] is None,('unknown_or_interval_has_scalar_grade',key)
        keyed[key]=row
    assert set(keyed)==expected
    return keyed


def semantic_signature(row):
    return tuple(row[k] for k in ['status','grade','subgrade'])


def fixtures():
    result=compare_permutations({1:2,2:4,3:35,4:2})
    assert len(result)==24 and result[0][1]==0
    assert {p for p,v in result if v==0}=={(1,2,3,4),(4,2,3,1)}
    assert compare_permutations({})==[]
    assert all(v==0 for _,v in compare_permutations({1:2,2:4,3:35,4:2})[:2])
    return {'status':'PASS','scope':'synthetic source-prior arithmetic only'}


def full_validation(args):
    root=Path(__file__).resolve().parents[1]
    receipt=load(root/'artifacts/SOURCE_RECEIPT.json')
    assert receipt['registered_commit']
    for rel,pin in receipt['bindings'].items():
        assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==pin,rel
    rawpath=args.source or args.runtime/'G600005.html'
    rows,expected=source_check(root,rawpath)
    repo=root.parents[2]
    prior=repo/'experiments/yolo/gdt1057_quality_full_source_orientation/artifacts'
    pins={'SOURCE_ENTRIES.tsv':'a764e68731edcaee5c7b9ddb15bd11828879bb0ff2dcd3b91d7f5f63503661ab','MANUAL_AUDIT.tsv':'c0fd4c7c71fdfadf1127574bafea1a6d04cef461648bad1246f2db65619fcf4f'}
    assert receipt['legacy_metadata_pins']==pins
    for filename,pin in pins.items():
        assert hashlib.sha256((prior/filename).read_bytes()).hexdigest()==pin
    windowpath=args.runtime/'windows.json'
    assert hashlib.sha256(windowpath.read_bytes()).hexdigest()==receipt['runtime_windows_sha256']
    runtime=load(windowpath)
    assert runtime['source_sha256']==receipt['source_sha256']==SOURCE_SHA
    accepted={i for i,q in expected}
    reconstructed=[]
    for r in rows:
        if r['ordinal'] not in accepted:
            continue
        thermal,humidity=r['auto_category'].split('_')
        reconstructed.append({k:r[k] for k in ['ordinal','source_number','source_line','opening','opening_sha256']}|{'opening_length':len(r['opening']),'thermal':thermal,'humidity':humidity})
    assert runtime['windows']==reconstructed
    assert receipt['entries']==[{k:v for k,v in r.items() if k!='opening'} for r in reconstructed]
    assert receipt['detected_starts']==286 and receipt['accepted_entries']==210 and receipt['required_axis_rows_per_reader']==420 and receipt['primary_dry_entries']==177
    windowmap={r['ordinal']:r['opening'] for r in rows}
    lock=load(args.annotation_lock)
    assert lock['status']=='ALL_ANNOTATIONS_FROZEN'
    paths=[args.annotations_a,args.annotations_b,args.adjudication]
    for p in paths:
        assert hashlib.sha256(p.read_bytes()).hexdigest()==lock['bindings'][str(p.relative_to(root))]
    a,b,final=(annotation_check(load(p),windowmap,expected) for p in paths)
    differences={k for k in expected if semantic_signature(a[k])!=semantic_signature(b[k])}
    adjudicated=differences|{k for k in expected if semantic_signature(final[k])!=semantic_signature(a[k]) or semantic_signature(final[k])!=semantic_signature(b[k])}
    notes=load(args.adjudication)['disagreements']
    required={(i,'thermal' if q in {'hot','cold'} else 'humidity') for i,q in adjudicated}
    assert len(notes)==len(required) and {(r['ordinal'],r['axis']) for r in notes}==required
    assert all(isinstance(r['reason'],str) and r['reason'].strip() for r in notes)
    result=load(root/'artifacts/RESULT.json')
    def exact(value):
        return {'numerator':value.numerator,'denominator':value.denominator,'value':float(value)}
    qualities={}
    for quality in ['dry','hot','cold','moist']:
        selected=[r for (i,q),r in final.items() if q==quality]
        counts=collections.Counter(r['grade'] for r in selected if r['status']=='FIXED')
        n=len(selected);known=sum(counts.values());unknown=n-known
        qualities[quality]={'entries':n,'known':known,'unknown':unknown,'grade_counts':[counts[g] for g in range(1,5)],'known_grade_proportions':[exact(Fraction(counts[g],known)) for g in range(1,5)] if known else None,'unknown_fraction':exact(Fraction(unknown,n)), 'grade_bounds':[{'grade':g,'lower':exact(Fraction(counts[g],n)),'upper':exact(Fraction(counts[g]+unknown,n))} for g in range(1,5)]}
    assert result['qualities']==qualities
    drycounts={g:qualities['dry']['grade_counts'][g-1] for g in range(1,5)}
    permutations=compare_permutations(drycounts)
    forms=['DAN','DAIN','DAIIN','DAIIIN']; table=[]
    for perm,tv in permutations:
        counts=[0]*4
        for grade,count in zip(perm,[2,4,35,2]):
            counts[grade-1]=count
        table.append({'mapping':dict(zip(forms,perm)),'permutation':list(perm),'target_grade_counts':counts,'tv':exact(tv),'rank':1+sum(v<tv for _,v in permutations),'best':tv==permutations[0][1]})
    assert result['permutations']==table
    original=next((r for r in table if r['permutation']==[1,2,3,4]),None)
    best=[r for r in table if r['best']]
    assert result['original_mapping']==original and result['best_mappings']==best
    assert result['DAIIN_best_grades']==sorted({r['mapping']['DAIIN'] for r in best})
    assert result['target_forms']==forms and result['target_counts']==[2,4,35,2]
    status='NO_KNOWN_DRY_GRADES' if original is None else 'ORIGINAL_MAPPING_COMPATIBLE_ONLY' if original['best'] else 'ORIGINAL_NUMERAL_PRIOR_WEAKENED'
    assert result['status']==status
    assert result['A_B_disagreements']==len(differences) and result['adjudication_records']==len(notes)
    assert result['rows_per_reader']==420 and result['confirmed_words']==result['new_target_access']==0
    assert result['annotation_bindings']=={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert result['annotation_lock_sha256']==hashlib.sha256(args.annotation_lock.read_bytes()).hexdigest()
    assert result['source_receipt_sha256']==hashlib.sha256((root/'artifacts/SOURCE_RECEIPT.json').read_bytes()).hexdigest()
    lines=(root/'CANDIDATE_TABLE.md').read_text().splitlines()
    formatted=['|'+'|'.join(map(str,[r['rank'],*r['permutation'],str(r['tv']['numerator'])+'/'+str(r['tv']['denominator']),f"{r['tv']['value']:.9f}",r['best']]))+'|' for r in table]
    assert [line for line in lines if re.match(r'^\|\d',line)]==formatted
    return {'status':'PASS','scope':'Independent source identities, annotation accounting and exact finite arithmetic; not independent historical interpretation','source_windows_rebuilt':286,'accepted_entries':210,'axis_rows_each_packet':420,'packets_checked':3,'semantic_reader_disagreements':len(differences),'offset_differences_not_semantic_disagreements':sum(a[k]['source_offset']!=b[k]['source_offset'] for k in expected if k not in differences),'all_numeral_permutations':len(table),'registered_status':status,'original_rank':None if original is None else original['rank'],'dry_grade_counts':qualities['dry']['grade_counts'],'dry_unknown':qualities['dry']['unknown'],'limitations':['Grade offsets verified against source substrings; attachment and historical semantic annotation remain reader/adjudicator judgments.','One translated source and reused target aggregate do not establish a Voynich meaning, significance, or a calibrated historical prior.'],'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'result_sha256':hashlib.sha256((root/'artifacts/RESULT.json').read_bytes()).hexdigest()}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--fixtures',action='store_true')
    ap.add_argument('--runtime',type=Path)
    ap.add_argument('--source',type=Path)
    ap.add_argument('--annotations-a',type=Path)
    ap.add_argument('--annotations-b',type=Path)
    ap.add_argument('--adjudication',type=Path)
    ap.add_argument('--annotation-lock',type=Path)
    args=ap.parse_args()
    for name in ['runtime','source','annotations_a','annotations_b','adjudication','annotation_lock']:
        value=getattr(args,name)
        if value is not None:
            setattr(args,name,value.resolve())
    if args.fixtures:
        print(json.dumps(fixtures()))
        return
    assert all([args.runtime,args.annotations_a,args.annotations_b,args.adjudication,args.annotation_lock])
    result=full_validation(args)
    root=Path(__file__).resolve().parents[1]
    (root/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
