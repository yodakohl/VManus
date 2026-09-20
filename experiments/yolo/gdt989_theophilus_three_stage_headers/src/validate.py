#!/usr/bin/env python3
"""Separate common-core enumeration and raw-source reconstruction; no runner imports."""
import collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def independent(heads,writer):
    if len(set(heads))!=9:return []
    sols=[]
    for n in range(1,min(len(heads[2]),len(heads[6]))):
        if writer=='STAGE_PREFIX':
            core=heads[2][-n:]
            if heads[6][-n:]!=core:continue
            a,b=heads[2][:-n],heads[6][:-n]
            if not all(heads[i].startswith(a) for i in (3,4)) or not all(heads[i].startswith(b) for i in (7,8)):continue
            r,l=heads[3][len(a):],heads[4][len(a):]
            if heads[7]!=b+r or heads[8]!=b+l:continue
        else:
            core=heads[2][:n]
            if heads[6][:n]!=core:continue
            a,b=heads[2][n:],heads[6][n:]
            if not all(heads[i].endswith(a) for i in (3,4)) or not all(heads[i].endswith(b) for i in (7,8)):continue
            r,l=heads[3][:-len(a)],heads[4][:-len(a)]
            if heads[7]!=r+b or heads[8]!=l+b:continue
        names=[heads[0],heads[1],core,r,l,heads[5]]
        if not all(names) or len(set(names))!=6 or a==b:continue
        sols.append(dict(zip(['MEMBRINA','PRASINUS','POSC','ROSA','LUMINA','VENEDA','FIRST','SECOND'],names+[a,b])))
    return sorted(sols,key=lambda c:json.dumps(c,sort_keys=True))
def main():
    for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    s=json.loads((E/'src/SOURCE.json').read_text()); paras=json.loads((ROOT/s['paragraph_input']).read_text())
    raw={}
    for phase in ('DISCOVERY','EVALUATION'):
        for ed in paras:
            d=json.loads((ROOT/(s['header_input_prefix']+phase+'_'+ed+'.json')).read_text()); cols=d['group_columns']
            for line in d['lines']:
                m=line['metadata'];assert not m['page'].startswith('f84') and m['page']!='f116v'
                for values in line['groups']:
                    g=dict(zip(cols,values));assert g['source_group_id'] not in raw
                    raw[g['source_group_id']]=(g,line,cols)
    hs={}
    for ed,rows in paras.items():
        for p in rows:
            key=ed+'|'+p['id'];ident=p['lines'][0]['source_ids'][0]
            assert ident in raw
            g,line,cols=raw[ident]; assert line['metadata']['page']==p['page'] and line['metadata']['locus']==p['lines'][0]['locus']
            records=[dict(zip(cols,v)) for v in line['groups']]
            eligible=g==records[0] and int(g['source_group_index'])==1 and bool(re.fullmatch('[a-z]+',g['ivtff_group_raw']))
            eligible=eligible and (int(records[1]['source_group_index'])==2 and g['right_separator']==records[1]['left_separator']=='DEFINITE_SPACE' if len(records)>1 else int(line['metadata']['source_group_count'])==1)
            hs[key]=(bool(eligible),g['ivtff_group_raw'],ident)
    stored=json.loads((A/'HEADERS.json').read_text());assert set(stored)==set(hs)
    for k,(ok,word,ident) in hs.items():
        h=stored[k];assert h['eligible']==ok and h['group']==raw[ident][0] and h['expected_source_id']==ident
        line=raw[ident][1];cols=raw[ident][2]
        assert h['next_group']==(dict(zip(cols,line['groups'][1])) if len(line['groups'])>1 else None)
        assert h['source_group_count']==int(line['metadata']['source_group_count'])
    expected=[]
    for ed,rows in paras.items():
        for page in sorted({p['page'] for p in rows}):
            seq=sorted([p for p in rows if p['page']==page],key=lambda p:p['lines'][0]['row'])
            for last in range(8,len(seq)):
                group=seq[last-8:last+1]
                gap=any(int(a['lines'][-1]['locus'].split('.')[-1])+1!=int(b['lines'][0]['locus'].split('.')[-1]) for a,b in zip(group,group[1:]))
                recs=[hs[ed+'|'+p['id']] for p in group]
                expected.append((ed,page,group,recs,gap))
    bundles=json.loads((A/'BUNDLES.json').read_text());cases=json.loads((A/'CASES.json').read_text());assert len(bundles)==len(expected) and len(cases)==2*len(expected)
    count=collections.Counter(); allcodes=0; eq=collections.defaultdict(list)
    for bi,(ed,page,group,recs,gap) in enumerate(expected):
        b=bundles[bi];assert b['bundle']==bi+1 and b['edition']==ed and b['page']==page and b['leaf']==group[0]['leaf']
        assert b['paragraphs']==[p['id'] for p in group] and b['heads']==[r[1] for r in recs] and b['source_ids']==[r[2] for r in recs] and bool(b['gaps'])==gap
        assert b['header_records']==[stored[ed+'|'+p['id']] for p in group]
        for wi,writer in enumerate(s['writers']):
            row=cases[2*bi+wi]; assert row['case']==2*bi+wi+1 and row['bundle']==bi+1 and row['writer']==writer and row['edition']==ed and row['page']==page
            codes=[] if gap or not all(r[0] for r in recs) else independent(b['heads'],writer)
            want='UNKNOWN_GAP' if gap else 'UNKNOWN_HEADER' if not all(r[0] for r in recs) else 'HEADER_FIT' if codes else 'CONTRADICTION'
            assert row['status']==want and sorted(row['codes'],key=lambda c:json.dumps(c,sort_keys=True))==codes
            count[want]+=1;allcodes+=len(codes)
            for c in codes:eq[json.dumps([writer,c,b['heads']],sort_keys=True)].append(row['case'])
    classes=[dict(writer=json.loads(k)[0],code=json.loads(k)[1],predicted_heads=json.loads(k)[2],owner_cases=v) for k,v in sorted(eq.items())]
    assert json.loads((A/'CONSEQUENCE_CLASSES.json').read_text())==classes
    pred=collections.defaultdict(list)
    for c in classes:pred[tuple(c['predicted_heads'])].append(dict(writer=c['writer'],code=c['code'],owner_cases=c['owner_cases']))
    assert json.loads((A/'PREDICTION_CLASSES.json').read_text())==[dict(predicted_heads=list(k),indistinguishable_codes=v) for k,v in sorted(pred.items())]
    result=json.loads((A/'RESULT.json').read_text());assert result['status_counts']==dict(count) and result['candidate_codes']==allcodes and result['cases']==len(cases) and result['bundles']==len(expected)
    assert result['confirmed_translated_words']==result['independent_confirmation_capacity']==0 and result['search_significance'] is None
    out=dict(status='PASS',cases_checked=len(cases),headers_checked=len(hs),bundles_checked=len(expected),candidate_codes=allcodes,common_core_enumeration=True,separate_implementation=True,independent_meaning_validation=False)
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
