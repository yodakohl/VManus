#!/usr/bin/env python3
import collections,hashlib,json,random,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
def dump(name,obj): (E/'artifacts'/name).write_text(json.dumps(obj,separators=(',',':'),sort_keys=True)+'\n')
def sources():
    for path,digest in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    out={}
    for ed in ['ZL3b','IT2a','RF1b']:
        rows=[]
        for part in ['DISCOVERY','EVALUATION']:
            p=ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{part}_{ed}.json'
            rows+=json.loads(p.read_text())['lines']
        for r in rows: assert not r['metadata']['page'].startswith('f84')
        out[ed]=sorted(rows,key=lambda r:(r['metadata']['page'],int(r['metadata']['source_row_index'])))
    return out

def frames(rows):
    out=[];excluded=[];buf=[];page=None
    for row in rows:
        m=row['metadata']
        if m['page']!=page:
            if buf:excluded.append({'loci':[r['metadata']['locus'] for r in buf],'reason':'UNFINISHED_PAGE'})
            buf=[];page=m['page']
        if str(m['paragraph_start'])=='1':
            if buf:excluded.append({'loci':[r['metadata']['locus'] for r in buf],'reason':'REPLACED_START'})
            buf=[]
            buf.append(row)
        elif buf:buf.append(row)
        if str(m['paragraph_end'])=='1' and buf:
            if len(buf)>=2 and all(r['metadata']['kind']=='P' for r in buf):out.append(buf)
            else:excluded.append({'loci':[r['metadata']['locus'] for r in buf],'reason':'SHORT_OR_NON_P'})
            buf=[]
    if buf:excluded.append({'loci':[r['metadata']['locus'] for r in buf],'reason':'UNFINISHED_PAGE'})
    return out,excluded

def words(row):
    return [{'word':g[2],'id':g[0],'locus':row['metadata']['locus']} for g in row['groups'] if re.fullmatch('[a-z]+',g[2]) and g[3] in ('LINE_START','DEFINITE_SPACE') and g[4] in ('LINE_END','DEFINITE_SPACE')]
def census(ed,rows,zframes):
    byloc={r['metadata']['locus']:r for r in rows};assert len(byloc)==len(rows)
    kept=[];excluded=[]
    for zf in zframes:
        loc=[r['metadata']['locus'] for r in zf]
        if any(l not in byloc or byloc[l]['metadata']['kind']!='P' for l in loc):
            excluded.append({'loci':loc,'reason':'MISSING_OR_NON_P_ALIGNMENT'});continue
        fr=[byloc[l] for l in loc];body=sum([words(r) for r in fr[1:]],[])
        if not body:excluded.append({'loci':loc,'reason':'ZERO_BODY_OPPORTUNITY'});continue
        h=[w for w in words(fr[0]) if w['word'].count('p')+w['word'].count('f')==1 and not any(c in w['word'] for c in 'kt')]
        m=fr[0]['metadata'];kept.append({'id':loc[0],'page':m['page'],'leaf':re.match(r'f\d+',m['page']).group(),'start_index':int(m['source_row_index']),'loci':loc,'anchors':sorted(set(w['word'] for w in h)),'header_occurrences':h,'body':body})
    groups=collections.defaultdict(list)
    for p in kept:groups[p['leaf']].append(p)
    matrices={};prediction=[];maps={'A':str.maketrans('pf','kt'),'B':str.maketrans('pf','tk')}
    for leaf,ps in sorted(groups.items()):
        ps.sort(key=lambda p:(p['page'],p['start_index']));a=sum(len(p['anchors']) for p in ps)
        eligible=len(ps)>=2 and a>0
        cs=[collections.Counter(w['word'] for w in p['body']) for p in ps]
        ms={g:[] for g in maps}
        for i,p in enumerate(ps):
            for g,tr in maps.items():
                row=[sum(c[w.translate(tr)]/len(q['body']) for w in p['anchors'])/a if a else 0 for c,q in zip(cs,ps)]
                ms[g].append(row)
                for w in p['anchors']:
                    target=w.translate(tr);rates=[c[target]/len(q['body']) for c,q in zip(cs,ps)]
                    prediction.append({'edition':ed,'leaf':leaf,'paragraph':p['id'],'anchor':w,'map':g,'predicted_whole':target,'exchangeable':eligible,'own_count':cs[i][target],'own_body_tokens':len(p['body']),'own_rate':rates[i],'exchange_mean_rate':sum(rates)/len(rates),'other_body_counts':[{'paragraph':q['id'],'count':cs[j][target],'tokens':len(q['body'])} for j,q in enumerate(ps) if j!=i],'witnesses':[v for v in p['body'] if v['word']==target],'mobile':max(rates)-min(rates)>1e-15})
        if eligible:matrices[leaf]={'paragraphs':[p['id'] for p in ps],'anchor_count':a,'matrices':ms}
    stats={}
    for g in maps:
        ps=[p for p in prediction if p['map']==g and p['exchangeable']]
        T=sum(sum(m['matrices'][g][i][i] for i in range(len(m['paragraphs']))) for m in matrices.values())/len(matrices) if matrices else 0
        mu=sum(sum(sum(row)/len(row) for row in m['matrices'][g]) for m in matrices.values())/len(matrices) if matrices else 0
        forms=len(set(p['anchor'] for p in ps));mobile=len(set(p['leaf'] for p in ps if p['mobile']))
        stats[g]={'T':T,'conditional_mean':mu,'residual':T-mu,'distinct_anchors':forms,'mobile_leaves':mobile,'capacity':forms>=5 and mobile>=5,'anchor_paragraphs':len(ps),'own_matches':sum(p['own_count'] for p in ps),'own_positive_predictions':sum(p['own_count']>0 for p in ps)}
    dump(f'CENSUS_{ed}.json',{'frames':kept,'exclusions':excluded,'predictions':prediction,'leaves':matrices,'statistics':stats})
    return matrices,stats,{'aligned_frames':len(kept),'excluded_frames':len(excluded),'exchangeable_leaves':len(matrices),'predictions':len(prediction)}
def main():
    data=sources();zf,exc=frames(data['ZL3b']);dump('FRAME_BOUNDARIES.json',{'frames':[[r['metadata']['locus'] for r in f] for f in zf],'exclusions':exc})
    results={};zm=None
    for ed,rows in data.items():
        mats,stats,count=census(ed,rows,zf);results[ed]={'statistics':stats,**count}
        if ed=='ZL3b':zm=mats
    worlds=[];obs=max(s['residual'] for s in results['ZL3b']['statistics'].values())
    for j in range(1024):
        rng=random.Random(920000+j);ts={'A':0.,'B':0.}
        for leaf,m in sorted(zm.items()):
            order=list(range(len(m['paragraphs'])));rng.shuffle(order)
            for g in ts:ts[g]+=sum(m['matrices'][g][i][k] for i,k in enumerate(order))/len(zm)
        rs={g:ts[g]-results['ZL3b']['statistics'][g]['conditional_mean'] for g in ts}
        worlds.append({'world':j,'residuals':rs,'maximum':max(rs.values())})
    ge=sum(w['maximum']>=obs-1e-12 for w in worlds);rank=(1+ge)/1025
    selected=[g for g,s in results['ZL3b']['statistics'].items() if s['capacity'] and s['residual']>0 and rank<=.05]
    status='PROVISIONAL_PARAGRAPH_WHOLEFORM_BRIDGE' if selected else ('BRIDGE_NOT_ESTABLISHED' if any(s['capacity'] for s in results['ZL3b']['statistics'].values()) else 'CAPACITY_STOP')
    dump('WORLDS.json',worlds);dump('RESULT.json',{'experiment':'GDT920','status':status,'editions':results,'primary_observed_maximum':obs,'worlds_ge_observed':ge,'joint_rank_fraction':rank,'provisional_maps':selected,'fresh_confirmation_leaves':0,'confirmed_meanings':0})
    print(json.dumps(json.loads((E/'artifacts/RESULT.json').read_text()),indent=2))
if __name__=='__main__':main()
