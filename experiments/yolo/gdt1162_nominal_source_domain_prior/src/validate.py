#!/usr/bin/env python3
"""Independent source-window/annotation/accounting validator; no semantic certification.
Core accounting derived from frozen METHOD before inspecting runner serialization.
Never imports runner/extractor or uses text classification.
"""
import argparse, hashlib, json, re
from pathlib import Path
EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
WORKS=['GALEN','QUINTE','SALERNO','BALNEIS']
CATS=['WATER','AIR','BASIN_ART','PIPE_ART','BASIN_NAT','PIPE_NAT']
RANK={'N':0,'U':1,'E':2}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def shatext(t):return hashlib.sha256(t.encode()).hexdigest()
def read(p):return json.loads(p.read_text())
def require(value,message):
    if not value:raise AssertionError(message)
def aggregate_independently(windows, labels):
    cells={}
    for work in WORKS:
        ids=[w['id'] for w in windows if w['work']==work]
        for scale in [100,200,400]:
            chunks=[ids[i:i+scale//100] for i in range(0,len(ids),scale//100)]
            category={c:{'lower':0,'upper':0} for c in CATS}
            pairs={p:{'marginal1':{'lower':0,'upper':0},'marginal2':{'lower':0,'upper':0},'joint':{'lower':0,'upper':0}} for p in ['T','F_ART','F_BROAD']}
            for chunk in chunks:
                obs={o:{c:max(RANK[labels[o][key]['values'][c]] for key in chunk) for c in CATS} for o in ['A','B']}
                for c in CATS:
                    category[c]['lower']+=int(all(obs[o][c]==2 for o in obs))
                    category[c]['upper']+=int(any(obs[o][c]>0 for o in obs))
                for name,cs in [('T',[('WATER',),('AIR',)]),('F_ART',[('BASIN_ART',),('PIPE_ART',)]),('F_BROAD',[('BASIN_ART','BASIN_NAT'),('PIPE_ART','PIPE_NAT')])]:
                    states={o:[max(obs[o][c] for c in group) for group in cs] for o in obs}
                    for j,tag in enumerate(['marginal1','marginal2']):
                        pairs[name][tag]['lower']+=int(all(states[o][j]==2 for o in obs))
                        pairs[name][tag]['upper']+=int(any(states[o][j]>0 for o in obs))
                    pairs[name]['joint']['lower']+=int(all(all(v==2 for v in states[o]) for o in obs))
                    pairs[name]['joint']['upper']+=int(all(any(states[o][j]>0 for o in obs) for j in range(2)))
            cells[(work,scale)]={'windows':len(chunks),'categories':category,'pairs':pairs}
    decisions={}
    for x,y in [('T','F_ART'),('T','F_BROAD'),('F_ART','T'),('F_BROAD','T')]:
        comparisons=[]
        for (work,scale),row in cells.items():
            comparisons.append({'work':work,'scale':scale,'passes':{m:row['pairs'][x][m]['lower']>=row['pairs'][y][m]['upper'] for m in ['marginal1','marginal2','joint']}})
        all_cells=all(all(c['passes'].values()) for c in comparisons)
        strict=[any(row['pairs'][x][m]['lower']>row['pairs'][y][m]['upper'] for row in cells.values()) for m in ['marginal1','marginal2']]
        positive={s:sum(cells[(w,s)]['pairs'][x]['joint']['lower']>0 for w in WORKS) for s in [100,200,400]}
        decisions[x+'>'+y]={'passes':all_cells and all(strict) and all(n>=2 for n in positive.values()),'all_cells':all_cells,'strict_marginals':strict,'positive_joint_works':positive,'cells':comparisons}
    status='CONDITIONAL_T_NOMINAL_PRIORITY' if decisions['T>F_ART']['passes'] and decisions['T>F_BROAD']['passes'] else 'CONDITIONAL_F_NOMINAL_PRIORITY' if decisions['F_ART>T']['passes'] and decisions['F_BROAD>T']['passes'] else 'NO_ROBUST_SOURCE_PRIORITY'
    return cells,decisions,status

def accounting_edge_cases():
    windows=[{'id':w+':'+str(i),'work':w} for w in WORKS for i in range(2)]
    labels={o:{r['id']:{'values':{c:'N' for c in CATS}} for r in windows} for o in ['A','B']}
    # Cross-observer disagreement: two individually possible concepts retain joint possibility.
    labels['A']['GALEN:0']['values']['WATER']='E'
    labels['B']['GALEN:0']['values']['AIR']='E'
    cells,decisions,status=aggregate_independently(windows,labels)
    require(cells[('GALEN',100)]['pairs']['T']['joint']=={'lower':0,'upper':1},'cross-observer conservative joint')
    require(not any(d['passes'] for d in decisions.values()),'zero baselines cannot earn dominance')
    # Distinct adjacent windows can create a larger-window joint; never sum base joints.
    for o in labels:
        labels[o]['QUINTE:0']['values']['WATER']='E'
        labels[o]['QUINTE:1']['values']['AIR']='E'
    cells,_,_=aggregate_independently(windows,labels)
    require(cells[('QUINTE',100)]['pairs']['T']['joint']['lower']==0,'base distinct-window no joint')
    require(cells[('QUINTE',200)]['pairs']['T']['joint']['lower']==1,'recomputed aggregate joint')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args()
    accounting_edge_cases()
    spec=read(EXP/'SPEC.json'); checks=['Synthetic edge cases: cross-observer joint possibility, coarsened joint creation, zero strictness']
    for path,pin in spec['preregistration_bindings'].items():require(digest(EXP/path)==pin,'preregistration hash '+path)
    checks.append('All frozen preregistration/source/helper/metadata hashes')
    sources=read(EXP/'src/SOURCES.json')
    for path,pin in sources['dependencies'].items():require(digest(ROOT/path)==pin,'legacy dependency hash '+path)
    for source in sources['sources']:
        path=args.cache/source['cache_name'];require(digest(path)==source['sha256'] and path.stat().st_size==source['bytes'],'raw source hash '+source['id'])
    checks.append('All four original raw bytes and legacy extractor dependencies')
    meta=read(EXP/'artifacts/SOURCE_UNITS.json');localpath=args.cache/'annotation_units.json'
    require(digest(localpath)==meta['local_annotation_units_sha256'],'local complete extraction hash')
    require(meta['extractor_sha256']==digest(EXP/'src/extract.py'),'extractor binding')
    require(meta['sources_sha256']==digest(EXP/'src/SOURCES.json'),'source manifest binding')
    local=read(localpath)
    require([{k:v for k,v in r.items() if k!='text'} for r in local['units']]==meta['units'],'public unit projections')
    require(set(local['bodies'])==set(WORKS),'four complete bodies')
    expected=[]
    for work in WORKS:
        body=local['bodies'][work]; text=body['text']; units=[u for u in local['units'] if u['work']==work]
        require({k:v for k,v in body.items() if k!='text'}==meta['bodies'][work],'body metadata '+work)
        require(shatext(text)==body['text_sha256'] and len(text)==body['characters'],'body content '+work)
        require(text=='\n\n'.join(u['text'] for u in units),'source order/body join '+work)
        tokens=list(re.finditer(r'\S+',text));require(len(tokens)==body['words'],'body words '+work)
        wordpos=0
        for u in units:
            require(u['body_word_start']==wordpos and u['body_word_end_exclusive']==wordpos+u['words'],'unit word coverage')
            require(text[u['body_char_start']:u['body_char_end_exclusive']]==u['text'],'unit char slice')
            require(shatext(u['text'])==u['text_sha256'] and len(u['text'].split())==u['words'],'unit text hash/words')
            wordpos+=u['words']
        require(wordpos==len(tokens),'unit final coverage')
        for n,start in enumerate(range(0,len(tokens),100)):
            end=min(start+100,len(tokens));a=tokens[start].start();b=tokens[end-1].end();snippet=text[a:b]
            expected.append(dict(id=f'{work}:{n+1:04d}',work=work,index=n,word_start=start,word_end=end,char_start=a,char_end=b,text=snippet,text_sha256=shatext(snippet),source_units=[u['unit_id'] for u in units if u['body_word_start']<end and u['body_word_end_exclusive']>start]))
    require(len(expected)==579 and len({r['id'] for r in expected})==579,'579 distinct windows')
    require(sum(r['word_end']-r['word_start'] for r in expected)==57707,'all57707words')
    public=read(EXP/'artifacts/WINDOWS.json')
    require(public['base_words']==100 and public['scales']==[100,200,400],'fixed scales')
    require(public['windows']==[{k:v for k,v in r.items() if k!='text'} for r in expected],'independent public windows')
    require(read(args.cache/'windows.json')['windows']==expected,'local windows exact')
    checks.append('Complete572units/579windows source order, character spans, words, hashes and lossless coverage')
    require(len(local['units'])==572,'572 source units')
    require(meta['works']['GALEN']['audit']['native1049_all_paragraph_metadata_equal'] is True,'native1049 readiness')
    legacy=read(ROOT/'experiments/yolo/gdt1049_galen_season_concept_countercheck/artifacts/SOURCE_UNITS.json')
    galen=[r for r in local['units'] if r['work']=='GALEN']
    require(len(galen)==266,'266Galen')
    require([(r['unit_id'].split(':',1)[1],r['text_sha256'],r['words']) for r in galen]==[(r['paragraph_id'],r['paragraph_sha256'],r['words']) for r in legacy['paragraphs']],'native1049 all original paragraph hashes')
    checks.append('Native1049 full266paragraph comparison; extraction readiness only, not new independent raw parsing')
    byid={r['id']:r for r in expected}; labels={'A':{},'B':{}};bindings={}
    for path in sorted((EXP/'artifacts').glob('ANNOTATIONS_*.json')):
        packet=read(path);o=packet['observer'];require(o in labels,'observer enum')
        require(packet.get('complete_reading') is True,'complete reading declaration')
        for field in ['reader','recorded_utc','prior_exposure']:require(isinstance(packet.get(field),str) and packet[field].strip(),'packet metadata '+field)
        require(isinstance(packet.get('rows'),list),'rows list')
        for row in packet['rows']:
            key=row['id'];require(key in byid and key not in labels[o],'unique admitted annotation ID')
            require(set(row['values'])==set(CATS) and set(row['values'].values())<=set(RANK),'six category schema')
            evidence=row['evidence'];require(isinstance(evidence,dict) and set(evidence)<=set(CATS),'evidence schema')
            for c,value in row['values'].items():
                if value=='N':continue
                require(c in evidence,'E/U evidence present');e=evidence[c]
                quote=e.get('quote');require(isinstance(quote,str) and quote.strip() and len(quote.split())<=12 and quote in byid[key]['text'],'exact local E/U quote <=12words')
                require(isinstance(e.get('reason'),str) and e['reason'].strip(),'E/U reason')
                if 'antecedent_id' in e or 'antecedent_quote' in e:
                    aid=e.get('antecedent_id');aq=e.get('antecedent_quote')
                    require(aid in byid and byid[aid]['work']==byid[key]['work'],'antecedent within samework')
                    require(isinstance(aq,str) and aq.strip() and len(aq.split())<=12 and aq in byid[aid]['text'],'exact antecedent quote <=12words')
            labels[o][key]=row
        bindings[str(path.relative_to(EXP))]=digest(path)
    coverage={o:len(rows) for o,rows in labels.items()}
    checks.append('Available packet schema, unique ownership, exact short E/U/antecedent witnesses; no semantic truth check')
    resultpath=EXP/'artifacts/RESULT.json'; result=read(resultpath) if resultpath.exists() else None
    complete=all(set(rows)==set(byid) for rows in labels.values())
    output={'experiment':'GDT1162','status':'INCOMPLETE','coverage':coverage,'required_per_observer':579,'checks':checks,'source_only':True,'mechanical_not_semantic':True,'input_bindings':bindings,'validator_sha256':digest(Path(__file__))}
    if result is not None:
        require(result['coverage']==coverage and result['bindings']==bindings,'result coverage/bindings')
        require(result['confirmed_words']==0 and result['new_target_access']==0,'claim limits')
    if not complete:
        if result is not None:require(result['status']=='INCOMPLETE_SOURCE_ANNOTATION_NO_PRIORITY' and 'cells' not in result and 'comparisons' not in result and result['required_per_stream']==579,'incomplete decision')
        output['missing_per_observer']={o:[key for key in byid if key not in labels[o]] for o in labels}
        output['reason']='Full two-observer annotation and accounting comparison not complete; no PASS or negative conceptual finding.'
    else:
        cells,decisions,status=aggregate_independently(expected,labels)
        output['independent_status']=status
        output['category_counts']=[dict(work=w,scale=s,**data) for (w,s),data in cells.items()]
        output['dominance_details']=decisions
        if result is None:output['reason']='Complete annotations but missing RESULT; no final comparison/PASS.'
        else:
            projected=[]
            for (w,s),data in cells.items():
                cell={'work':w,'scale':s,'windows':data['windows']}
                for p,parts in data['pairs'].items():cell[p]={bound:[parts[m][bound] for m in ['marginal1','marginal2','joint']] for bound in ['lower','upper']}
                projected.append(cell)
            require(result['cells']==projected,'all12cells all pair bounds')
            require(result['comparisons']=={k:v['passes'] for k,v in decisions.items()},'four complete dominance decisions')
            require(result['status']==status,'final status')
            checks.append('Independent per-observer coarsening, category/pair bounds, all12cells, strict/joint gates and final decision')
            output['status']='PASS'
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'coverage':coverage,'checks':len(checks)}))
if __name__=='__main__':main()
