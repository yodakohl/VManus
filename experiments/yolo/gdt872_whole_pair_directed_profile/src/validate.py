#!/usr/bin/env python3
"""Independent endpoint-first reconstruction from guarded runtime projections."""
import csv, hashlib, json, math, re, sys
from collections import defaultdict, Counter
from pathlib import Path
B=Path(__file__).resolve().parents[1]; ROOT=B.parents[2]; A=B/'artifacts'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def readtsv(p):
    with p.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def folio(p):return re.fullmatch(r'(f\d+)[rv]\d*',p).group(1)
def inventories(s,key):return {r[side]:(r['pair_id'],side) for r in s[key] for side in ['CH','SH']}
def exact(g):return int(g['clean_ascii_fragment_count'])==1 and g['clean_ascii_fragments']==g['ivtff_group_raw']
def forbidden(s):return s=='UNCERTAIN_SMALL_SPACE' or s.startswith('DRAWING_')
def reconstruct(s,atlas,lines):
    anchors=inventories(s,'anchors'); responses=inventories(s,'responses');assert not anchors.keys()&responses.keys()
    meta={(r['page'],r['locus']):r for r in lines};assert len(meta)==len(lines)
    grouped=defaultdict(list)
    ids=set()
    for g in atlas:
        assert not g['page'].startswith('f84');assert g['source_group_id'] not in ids;ids.add(g['source_group_id'])
        grouped[g['edition'],g['page'],g['locus']].append(g)
    for key,gs in grouped.items():
        gs.sort(key=lambda g:int(g['source_group_index']));assert [int(g['source_group_index']) for g in gs]==list(range(1,len(gs)+1));assert all(int(g['source_group_count'])==len(gs) for g in gs)
        for g in gs:assert len(g['clean_ascii_fragments'].split())==int(g['clean_ascii_fragment_count'])
    for key,m in meta.items():
        gs=grouped.get((s['primary_edition'],)+key);assert gs is not None
        assert ' '.join(x for g in gs for x in g['clean_ascii_fragments'].split())==m['eva_clean']
    parity={}
    for page,locus in {(g['page'],g['locus']) for g in atlas}:
        seq=[[g['ivtff_group_raw'] for g in grouped.get((ed,page,locus),[])] for ed in s['diagnostic_editions']]
        parity[page,locus]=bool(all(seq) and all(v==seq[0] for v in seq))
    pages=defaultdict(list)
    for g in atlas:
        if g['edition']==s['primary_edition']:pages[g['page']].append(g)
    result=[]
    for page,gs in pages.items():
        gs.sort(key=lambda g:(int(g['source_row_index']),int(g['source_group_index'])))
        # Enumerate endpoints first, independently of the builder's anchor-first traversal.
        for end,e in enumerate(gs):
            for distance in s['lags']:
                for direction,step in [('forward',1),('backward',-1)]:
                    start=end-step*distance
                    if not 0<=start<len(gs):continue
                    a=gs[start];surf=a['ivtff_group_raw']
                    if surf not in anchors or not exact(a):continue
                    path=gs[min(start,end):max(start,end)+1]
                    if any(not meta.get((g['page'],g['locus']),{}).get('strict_paragraph_id') for g in path):continue
                    if any(forbidden(l['right_separator']) or forbidden(r['left_separator']) for l,r in zip(path,path[1:])):continue
                    am=meta[page,a['locus']];em=meta[page,e['locus']]
                    ap,aside=anchors[surf];rr=responses.get(e['ivtff_group_raw']) if exact(e) else None
                    row={'page':page,'physical_folio':folio(page),'anchor_locus':a['locus'],'response_locus':e['locus'],'anchor_surface':surf,'response_surface':e['ivtff_group_raw'],'anchor_pair_id':ap,'anchor_sign':aside,'response_pair_id':rr[0] if rr else 'NONE','response_sign':rr[1] if rr else '', 'direction':direction,'lag':distance,'lag_band':'NEAR' if distance in s['lag_bands']['NEAR'] else 'DISTAL','paragraph_relation':'within_para' if am['strict_paragraph_id']==em['strict_paragraph_id'] else 'cross_para','response_hit':int(rr is not None),'agreement':int(rr is not None and aside==rr[1]),'disagreement':int(rr is not None and aside!=rr[1]),'anchor_page_group_index':start,'response_page_group_index':end}
                    result.append(dict(row,view='PRIMARY'))
                    if all(parity[g['page'],g['locus']] for g in path):result.append(dict(row,view='DIAGNOSTIC'))
    return result

def self_test():
    s={'anchors':[{'pair_id':'A','CH':'a','SH':'b'}],'responses':[{'pair_id':'R','CH':'x','SH':'y'}],'primary_edition':'ZL3b','diagnostic_editions':['ZL3b','IT2a','RF1b'],'lags':[1,2,3],'lag_bands':{'NEAR':[1,2]}}
    lines=[{'page':'f1r','locus':'f1r.1','strict_paragraph_id':'P','eva_clean':'a z x'},{'page':'f1r','locus':'f1r.2','strict_paragraph_id':'Q','eva_clean':'y'},{'page':'f1v','locus':'f1v.1','strict_paragraph_id':'R','eva_clean':'x'}];atlas=[]
    for ed in s['diagnostic_editions']:
        for ln,raws in zip(lines,[['a','z','@0','x'],['y'],['x']]):
            for i,raw in enumerate(raws,1):atlas.append({'edition':ed,'page':ln['page'],'locus':ln['locus'],'source_group_id':ed+ln['locus']+str(i),'source_group_index':str(i),'source_group_count':str(len(raws)),'source_row_index':'1' if ln['locus'].endswith('.1') else '2','ivtff_group_raw':raw,'clean_ascii_fragments':'' if raw=='@0' else raw,'clean_ascii_fragment_count':'0' if raw=='@0' else '1','left_separator':'SPACE','right_separator':'SPACE'})
    out=reconstruct(s,atlas,lines);hits=[r for r in out if r['response_hit']];assert len(hits)==2 and all(r['lag']==3 and r['response_surface']=='x' for r in hits)
    assert len(out)==6;assert folio('f1r')==folio('f1v')==folio('f1v2')=='f1'
    # A blocked traversed endpoint edge excludes paths; an outer anchor edge does not.
    atlas[0]['left_separator']='DRAWING_GAP';assert reconstruct(s,atlas,lines)==out
    atlas[0]['right_separator']='UNCERTAIN_SMALL_SPACE';assert reconstruct(s,atlas,lines)==[]
    atlas[0]['right_separator']='SPACE';atlas[-2]['ivtff_group_raw']='other'
    changed=reconstruct(s,atlas,lines);assert len(changed)==6 # unrelated line is not traversed
    # A raw discrepancy on the traversed RF line removes the diagnostic opportunities only.
    next(g for g in atlas if g['edition']=='RF1b' and g['locus']=='f1r.1' and g['source_group_index']=='2')['ivtff_group_raw']='different'
    changed=reconstruct(s,atlas,lines);assert len(changed)==3 and all(r['view']=='PRIMARY' for r in changed)
    print('PASS_SYNTHETIC_RAW_LAG_GAPS_VIEWS_FOLIO')

def main():
    if '--self-test' in sys.argv:self_test();return
    s=json.loads((B/'src/SPEC.json').read_text());receipt=json.loads((A/'GDT872_QUERY_RECEIPTS.json').read_text());paths={}
    assert receipt['atlas_source']['selector']=='page' and set(receipt['atlas_source']['forbidden_prefixes'])=={'f84','f84r'}
    assert all(q['allowed_value_count']==179 and q['forbidden_prefixes']=='f84|f84r' and q['query_returncode']==0 for q in receipt['gdt807_guarded_queries'])
    for name,d in receipt['runtime_projections'].items():
        p=ROOT/d['path'];assert p.is_file() and sha(p)==d['sha256'];assert (B/'runtime').resolve() in p.resolve().parents;paths[name]=p
    # No permitted projection is interpreted before all hashes and receipt selectors pass.
    atlas=readtsv(paths['atlas_tsv']);lines=json.loads(paths['line_records_json'].read_text())['records'];assert len(atlas)==receipt['atlas_guarded_query']['selected']
    expected=reconstruct(s,atlas,lines);actual=json.loads(paths['opportunities_json'].read_text())['records']
    canon=lambda x:json.dumps(x,sort_keys=True)
    assert Counter(map(canon,expected))==Counter(map(canon,actual)),'individual opportunity replay'
    hitrows=readtsv(A/'GDT872_DIRECTED_HITS.tsv');keys=list(hitrows[0]) if hitrows else []
    assert Counter(tuple(str(r[k]) for k in keys) for r in expected if r['response_hit'])==Counter(tuple(r[k] for k in keys) for r in hitrows),'exact hits'
    fields=['view','physical_folio','anchor_pair_id','anchor_sign','direction','lag_band','paragraph_relation'];cells=defaultdict(list)
    for r in expected:cells[tuple(r[k] for k in fields)].append(r)
    aggs=readtsv(A/'GDT872_OPPORTUNITY_AGGREGATES.tsv');assert len(aggs)==len(cells)*len(s['responses'])*2
    seen=set()
    for row in aggs:
        key=tuple(row[k] for k in fields);rpair=row['response_pair_id'];rside=row['response_sign'];assert (key,rpair,rside) not in seen;seen.add((key,rpair,rside))
        opp=cells[key];hit=[r for r in opp if r['response_hit'] and r['response_pair_id']==rpair and r['response_sign']==rside];agree=sum(r['agreement'] for r in hit)
        assert int(row['opportunities'])==len(opp) and int(row['response_hits'])==len(hit)
        assert int(row['agreement'])==agree and int(row['disagreement'])==len(hit)-agree
        per=defaultdict(list)
        for r in opp:per[r['page'],r['anchor_page_group_index']].append(r)
        macro=sum(sum(r in hit for r in v)/len(v) for v in per.values())/len(per)
        assert math.isclose(float(row['macro_anchor_rate']),macro,abs_tol=1e-10)
        if hit:assert math.isclose(float(row['conditional_concordance']),agree/len(hit),abs_tol=1e-10)
        else:assert row['conditional_concordance']=='NA'
    result=json.loads((A/'RESULT.json').read_text())
    for view,pre in [('PRIMARY',''),('DIAGNOSTIC','diagnostic_')]:
        rr=[r for r in expected if r['view']==view];assert result[pre+'opportunity_count']==len(rr);assert result[pre+'response_hit_count']==sum(r['response_hit'] for r in rr)
    out={'status':'PASS','scope':'independent endpoint-first raw-position replay and all output counts/rates; no scientific significance or meaning','opportunities_by_view':dict(Counter(r['view'] for r in expected)),'hits_by_view':dict(Counter(r['view'] for r in expected if r['response_hit'])),'input_hashes':{p.name:sha(p) for p in [B/'src/SPEC.json',B/'src/run.py',B/'src/validate.py',A/'RESULT.json',A/'GDT872_QUERY_RECEIPTS.json']}}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
