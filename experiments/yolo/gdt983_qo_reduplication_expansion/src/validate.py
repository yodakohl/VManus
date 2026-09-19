"""Rebuild literal candidate and flank evidence without importing the runner."""
import collections,csv,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(n):return json.loads((A/n).read_text())
def main():
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for n,h in lock['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    s=json.loads((E/'src/SPEC.json').read_text());allowed=set(json.loads((R/s['scope']).read_text())['allowed_selectors'])
    raw=[];lines={};pcounts=collections.Counter();types=set()
    for n in s['snapshots']:
        src=json.loads((R/n).read_text())
        for line in src['lines']:
            m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page']!='f116v'
            if m['kind']!='P':continue
            ed=m['edition'];pcounts[ed]+=1;gg=[dict(zip(src['group_columns'],x)) for x in line['groups']]
            for i,g in enumerate(gg):
                w=g['ivtff_group_raw'];nextw=gg[i+1]['ivtff_group_raw'] if i+1<len(gg) else None
                good=lambda x: x is not None and bool(re.fullmatch('[a-z]+',x))
                roles=[]
                if good(w) and w[:4]=='qoqo' and len(w)>4:roles.append('COMPRESSED');types.add(w)
                if good(w) and w[:2]=='qo' and len(w)>2 and w==nextw:roles.append('DUP')
                if w=='qo' and good(nextw) and nextw[:2]=='qo' and len(nextw)>2:roles.append('ECHO')
                for role in roles:
                    raw.append(dict(edition=ed,locus=m['locus'],page=m['page'],source_id=g['source_group_id'],index=i,role=role,word=w,following=nextw))
                    lines[ed+'|'+m['locus']]=dict(metadata=m,groups=gg)
    assert raw==read('RAW_INVENTORY.json');assert lines==read('SOURCE_LINES.json')
    predictions=[]
    for c in sorted(types):
        for model in ['DUP','ECHO','SINGLE']:
            base='qo'+c[4:];seq=[base,base] if model=='DUP' else ['qo',base] if model=='ECHO' else [base]
            predictions.append(dict(compressed=c,model=model,expansion=seq))
    assert predictions==read('PREDICTIONS.json')
    ps=json.loads((R/s['paragraphs']).read_text());shorts=[];longs=[];context={}
    for ed,paragraphs in ps.items():
        for p in paragraphs:
            assert p['page'] in allowed and not p['page'].startswith('f84') and p['page']!='f116v'
            for ln in p['lines']:
                ws=ln['words'];common=dict(edition=ed,paragraph=p['id'],page=p['page'],leaf=p['leaf'],locus=ln['locus'],line_eligible=ln['anchor_eligible'])
                for i in range(len(ws)):
                    if ws[i] in types:
                        interior=0<i<len(ws)-1
                        st='LINE_INELIGIBLE' if not ln['anchor_eligible'] else 'ELIGIBLE' if interior else 'MISSING_FLANK'
                        shorts.append(dict(common,compressed=ws[i],index=i,source_id=ln['source_ids'][i],flanks=[ws[i-1],ws[i+1]] if interior else None,status=st));context[ed+'|'+p['id']]=p
                    for pred in predictions:
                        length=len(pred['expansion']);end=i+length
                        if ln['anchor_eligible'] and ws[i:end]==pred['expansion']:
                            longs.append(dict(common,**pred,index=i,source_ids=ln['source_ids'][i:end],flanks=[ws[i-1],ws[end]] if i>0 and end<len(ws) else None))
    assert shorts==read('COMPRESSED_OCCURRENCES.json');assert longs==read('EXPANSION_OCCURRENCES.json')
    long_index=collections.defaultdict(list)
    for b in longs:
        if b['flanks'] is not None:long_index[b['edition'],b['compressed'],tuple(b['flanks'])].append(b)
    matches=[]
    for a in shorts:
        if a['status']=='ELIGIBLE':
            for b in long_index[a['edition'],a['compressed'],tuple(a['flanks'])]:
                matches.append(dict(compressed=a['compressed'],model=b['model'],edition=a['edition'],short=a,long=b,different_leaf=a['leaf']!=b['leaf']))
    assert matches==read('MATCHES.json')
    for m in matches:
        for side in ['short','long']:
            z=m[side];context[z['edition']+'|'+z['paragraph']]=next(p for p in ps[z['edition']] if p['id']==z['paragraph'])
    assert context==read('COMPLETE_PARAGRAPHS.json')
    result=read('RESULT.json');assert result['candidates']==sorted(types)
    assert result['raw_p_lines']==dict(pcounts) and result['raw_inventory']==len(raw)
    assert result['complete_paragraphs']=={e:len(p) for e,p in ps.items()}
    assert result['compressed_occurrences']==len(shorts) and result['expansion_occurrences']==len(longs) and result['matches']==len(matches)
    assert result['compressed_statuses']==dict(collections.Counter(a['status'] for a in shorts))
    for row in result['models']:
        mm=[m for m in matches if m['edition']==row['edition'] and m['model']==row['model'] and m['different_leaf']]
        ntypes=len({m['compressed'] for m in mm});nf=len({tuple(m['short']['flanks']) for m in mm});leaves=sorted({m[side]['leaf'] for m in mm for side in ['short','long']});outside=any(m['short']['leaf']!=75 for m in mm)
        assert row==dict(edition=row['edition'],model=row['model'],cross_leaf_matches=len(mm),compressed_types=ntypes,flank_types=nf,leaves=leaves,compressed_outside_design_leaf=outside,qualified=ntypes>=2 and nf>=2 and len(leaves)>=3 and outside)
    assert result['status']==('CONTEXT_BRIDGE_CANDIDATE' if any(x['qualified'] for x in result['models']) else 'NO_CONTEXT_SUPPORT')
    table=list(csv.DictReader((A/'CANDIDATE_TABLE.tsv').open(),delimiter='\t'));assert len(table)==len(types)*9
    assert len({(r['edition'],r['compressed'],r['model']) for r in table})==len(table)
    for r in table:
        ed,c,m=r['edition'],r['compressed'],r['model'];expected=next(p['expansion'] for p in predictions if p['compressed']==c and p['model']==m);assert r['predicted']==' '.join(expected)
        oo=[a for a in shorts if a['edition']==ed and a['compressed']==c];xx=[a for a in longs if a['edition']==ed and a['compressed']==c and a['model']==m];mm=[x for x in matches if x['edition']==ed and x['compressed']==c and x['model']==m]
        values=dict(raw_count=sum(a['edition']==ed and a['word']==c and a['role']=='COMPRESSED' for a in raw),paragraph_count=len(oo),eligible_compressed=sum(a['status']=='ELIGIBLE' for a in oo),eligible_expansions=len(xx),same_leaf_matches=sum(not x['different_leaf'] for x in mm),different_leaf_matches=sum(x['different_leaf'] for x in mm),independent_confirmation=0)
        assert all(int(r[k])==v for k,v in values.items()),r
    assert result['independent_confirmation']==result['confirmed_words']==0
    out=dict(status='PASS',source_lines=len(lines),raw_records=len(raw),candidate_rows=len(table),shorts=len(shorts),expansions=len(longs),matches=len(matches),scope='Separate source/census reconstruction by same author; not semantic validation.')
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
