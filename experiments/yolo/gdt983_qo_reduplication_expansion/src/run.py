"""Fixed qo-reduplication spelling predictions, no meaning decoder."""
import collections,csv,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def dump(n,x): (E/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def expansions(c):
    b=c[2:]
    return {'DUP':[b,b],'ECHO':['qo',b],'SINGLE':[b]}
def main():
    for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    s=json.loads((E/'src/SPEC.json').read_text());allowed=set(json.loads((R/s['scope']).read_text())['allowed_selectors'])
    inventory=[];source_lines={};candidates=set();counts=collections.Counter()
    for n in s['snapshots']:
        d=json.loads((R/n).read_text())
        for line in d['lines']:
            m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page']!='f116v'
            if m['kind']!='P':continue
            ed=m['edition'];counts[ed]+=1;gg=[dict(zip(d['group_columns'],g)) for g in line['groups']];words=[g['ivtff_group_raw'] for g in gg]
            for i,w in enumerate(words):
                roles=[]
                if re.fullmatch(r'qoqo[a-z]+',w):roles.append('COMPRESSED');candidates.add(w)
                if i+1<len(words) and re.fullmatch('qo[a-z]+',w) and w==words[i+1]:roles.append('DUP')
                if i+1<len(words) and w=='qo' and re.fullmatch('qo[a-z]+',words[i+1]):roles.append('ECHO')
                for role in roles:
                    inventory.append(dict(edition=ed,locus=m['locus'],page=m['page'],source_id=gg[i]['source_group_id'],index=i,role=role,word=w,following=words[i+1] if i+1<len(words) else None))
                    source_lines[ed+'|'+m['locus']]=dict(metadata=m,groups=gg)
    candidates=sorted(candidates)
    predictions=[dict(compressed=c,model=m,expansion=x) for c in candidates for m,x in expansions(c).items()]
    dump('PREDICTIONS.json',predictions);dump('RAW_INVENTORY.json',inventory);dump('SOURCE_LINES.json',source_lines)
    ps=json.loads((R/s['paragraphs']).read_text());occ=[];expanded=[];context={}
    for ed,paras in ps.items():
        for p in paras:
            assert p['page'] in allowed and not p['page'].startswith('f84') and p['page']!='f116v'
            for line in p['lines']:
                ws=line['words'];common=dict(edition=ed,paragraph=p['id'],page=p['page'],leaf=p['leaf'],locus=line['locus'],line_eligible=line['anchor_eligible'])
                for i,w in enumerate(ws):
                    if w in candidates:
                        status='ELIGIBLE' if line['anchor_eligible'] and 0<i<len(ws)-1 else ('LINE_INELIGIBLE' if not line['anchor_eligible'] else 'MISSING_FLANK')
                        occ.append(dict(common,compressed=w,index=i,source_id=line['source_ids'][i],flanks=[ws[i-1],ws[i+1]] if 0<i<len(ws)-1 else None,status=status))
                        context[ed+'|'+p['id']]=p
                    for pred in predictions:
                        x=pred['expansion'];j=i+len(x)
                        if ws[i:j]==x and line['anchor_eligible']:
                            expanded.append(dict(common,**pred,index=i,source_ids=line['source_ids'][i:j],flanks=[ws[i-1],ws[j]] if i>0 and j<len(ws) else None))
    matches=[]
    for a in occ:
        if a['status']!='ELIGIBLE':continue
        for b in expanded:
            if a['edition']==b['edition'] and a['compressed']==b['compressed'] and a['flanks']==b['flanks']:
                matches.append(dict(compressed=a['compressed'],model=b['model'],edition=a['edition'],short=a,long=b,different_leaf=a['leaf']!=b['leaf']))
    for m in matches:
        for side in ['short','long']:
            a=m[side];context[a['edition']+'|'+a['paragraph']]=next(p for p in ps[a['edition']] if p['id']==a['paragraph'])
    summaries=[]
    for ed in ['ZL3b','IT2a','RF1b']:
        for model in s['models']:
            mm=[m for m in matches if m['edition']==ed and m['model']==model and m['different_leaf']]
            cs={m['compressed'] for m in mm};flanks={tuple(m['short']['flanks']) for m in mm};leaves={m[k]['leaf'] for m in mm for k in ['short','long']}
            outside=any(m['short']['leaf']!=s['design_leaf'] for m in mm)
            summaries.append(dict(edition=ed,model=model,cross_leaf_matches=len(mm),compressed_types=len(cs),flank_types=len(flanks),leaves=sorted(leaves),compressed_outside_design_leaf=outside,qualified=len(cs)>=2 and len(flanks)>=2 and len(leaves)>=3 and outside))
    rows=[]
    for pred in predictions:
        for ed in ['ZL3b','IT2a','RF1b']:
            raw=[a for a in inventory if a['edition']==ed and a['role']=='COMPRESSED' and a['word']==pred['compressed']]
            oo=[a for a in occ if a['edition']==ed and a['compressed']==pred['compressed']]
            xx=[a for a in expanded if a['edition']==ed and a['compressed']==pred['compressed'] and a['model']==pred['model']]
            mm=[m for m in matches if m['edition']==ed and m['compressed']==pred['compressed'] and m['model']==pred['model']]
            rows.append(dict(edition=ed,compressed=pred['compressed'],model=pred['model'],predicted=' '.join(pred['expansion']),raw_count=len(raw),paragraph_count=len(oo),eligible_compressed=sum(a['status']=='ELIGIBLE' for a in oo),eligible_expansions=len(xx),same_leaf_matches=sum(not m['different_leaf'] for m in mm),different_leaf_matches=sum(m['different_leaf'] for m in mm),independent_confirmation=0))
    for n,x in [('COMPRESSED_OCCURRENCES.json',occ),('EXPANSION_OCCURRENCES.json',expanded),('MATCHES.json',matches),('COMPLETE_PARAGRAPHS.json',context)]:dump(n,x)
    with (E/'artifacts/CANDIDATE_TABLE.tsv').open('w') as f:
        fields=list(rows[0]) if rows else ['edition','compressed','model','predicted']
        w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    out=dict(status='CONTEXT_BRIDGE_CANDIDATE' if any(m['qualified'] for m in summaries) else 'NO_CONTEXT_SUPPORT',raw_p_lines=dict(counts),candidates=candidates,raw_inventory=len(inventory),complete_paragraphs={e:len(p) for e,p in ps.items()},compressed_occurrences=len(occ),compressed_statuses=dict(collections.Counter(a['status'] for a in occ)),expansion_occurrences=len(expanded),matches=len(matches),models=summaries,independent_confirmation=0,confirmed_words=0)
    dump('RESULT.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
