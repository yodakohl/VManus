"""Separate SQL-neighbour extraction and exhaustive deterministic-choice checks."""
from pathlib import Path
from collections import defaultdict,Counter
from itertools import product
import sys,json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';sys.path.insert(0,str(ROOT))
from tools import word_profiles as wp
READERS=('ZL3b','IT2a','RF1b')
def read(p):return json.loads(p.read_text())
def main():
    for p,h in read(A/'REGISTRATION_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert read(A/'RUN_RECEIPT.json')['runner_sha256']==hashlib.sha256((D/'src/run.py').read_bytes()).hexdigest()
    expected_bases=sorted(set(read(ROOT/'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts/RESULT.json')['non_dal_joint']['base_family'])|{'dal'})
    result=read(A/'RESULT.json');assert result['bases']==expected_bases;bs=set(expected_bases);forms=sorted({b+v for b in bs for v in ('y','dy')})
    conn=wp.ensure_cache(ROOT);assert wp.receipt(conn)==read(A/'SOURCE_RECEIPT.json')==read(ROOT/'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts/SOURCE_RECEIPT.json')
    q='''SELECT t.*,l.ivtff_group_raw AS prev,l.source_group_id AS prev_id,l.right_separator AS prev_sep,r.ivtff_group_raw AS nxt,r.source_group_id AS nxt_id,r.left_separator AS nxt_sep FROM groups t JOIN groups l ON l.edition=t.edition AND l.page=t.page AND l.locus=t.locus AND l.source_group_index=t.source_group_index-1 JOIN groups r ON r.edition=t.edition AND r.page=t.page AND r.locus=t.locus AND r.source_group_index=t.source_group_index+1 WHERE t.kind='P' AND t.ivtff_group_raw IN ('''+','.join('?' for _ in forms)+')'
    events=[]
    for row in conn.execute(q,forms):
        t=dict(row);w=t['ivtff_group_raw'];triple=(t['prev'],w,t['nxt'])
        if any(not x or any(c<'a' or c>'z' for c in x) for x in triple):continue
        seams=[t['prev_sep'],t['left_separator'],t['right_separator'],t['nxt_sep']]
        if set(seams)!={'DEFINITE_SPACE'}:continue
        for v in ('y','dy'):
            if not w.endswith(v) or w[:-len(v)] not in bs:continue
            e={k:t[k] for k in ('edition','page','locus','section','currier','hand','kind','source_group_id','source_group_index','source_group_count')}
            e.update(base=w[:-len(v)],variant=v,form=w,previous=t['prev'],following=t['nxt'],previous_id=t['prev_id'],following_id=t['nxt_id'],seams=seams,position='INTERNAL');events.append(e)
    events.sort(key=lambda e:(e['edition'],e['page'],e['locus'],e['source_group_index'],e['base'],e['variant']))
    for i,e in enumerate(events):e['event_id']=f'E{i:06d}'
    assert events==read(A/'EVENTS.json');byid={e['event_id']:e for e in events};maps={}
    for mode in ('FULL','EDGE'):
        for ed in READERS:
            grouped=defaultdict(lambda:[[],[]])
            for e in events:
                if e['edition']!=ed:continue
                a=e['previous'] if mode=='FULL' else e['previous'][-1];b=e['following'] if mode=='FULL' else e['following'][0]
                key=(e['base'],e['page'],e['section'],e['currier'],e['hand'],'INTERNAL',a,b)
                grouped[key][e['variant']=='dy'].append(e['event_id'])
            maps[mode,ed]=grouped
    cells=[]
    for (mode,ed),d in sorted(maps.items()):
        for k,(ys,ds) in sorted(d.items()):cells.append({'mode':mode,'edition':ed,'input':list(k),'y':ys,'dy':ds,'mixed':len(ys)>0 and len(ds)>0,'minimum_errors':min(len(ys),len(ds))})
    assert cells==read(A/'CELLS.json');display=[];loci=set();joint={}
    for mode in ('FULL','EDGE'):
        for ed in READERS:
            cs=[c for c in cells if c['mode']==mode and c['edition']==ed];mixed=[c for c in cs if c['mixed']];es=[e for e in events if e['edition']==ed]
            stats={'events':len(es),'physical_groups':len({e['source_group_id'] for e in es}),'bases':len({e['base'] for e in es}),'pages':len({e['page'] for e in es}),
                'cells':len(cs),'singleton_cells':sum(len(c['y'])+len(c['dy'])==1 for c in cs),'repeated_cells':sum(len(c['y'])+len(c['dy'])>=2 for c in cs),'mixed_cells':len(mixed),
                'mixed_pages':len({c['input'][1] for c in mixed}),'mixed_bases':sorted({c['input'][0] for c in mixed}),'minimum_errors':sum(min(len(c['y']),len(c['dy'])) for c in cs),
                'decision':'CONTRADICTED' if mixed else 'NO_OBSERVED_CONTRADICTION','metadata_values':{k:dict(sorted(Counter(e[k] for e in es).items())) for k in ('section','currier','hand')}}
            assert result['readers'][mode][ed]==stats
            for c in mixed[:4]:
                pair=[c['y'][0],c['dy'][0]];display.append({'mode':mode,'edition':ed,'input':c['input'],'events':pair})
                for eid in pair:loci.add((byid[eid]['page'],byid[eid]['locus']))
        joint[mode]='CONTRADICTED_IN_ZL_AND_IT' if all(result['readers'][mode][ed]['mixed_cells']>0 for ed in ('ZL3b','IT2a')) else 'NO_JOINT_COUNTERCASE'
    assert result['joint']==joint
    expected_status='FULL_NEIGHBOUR_RULE_CONTRADICTED' if joint['FULL']=='CONTRADICTED_IN_ZL_AND_IT' else 'EDGE_RULE_ONLY_CONTRADICTED' if joint['EDGE']=='CONTRADICTED_IN_ZL_AND_IT' else 'NO_JOINT_LOCAL_RULE_COUNTERCASE'
    assert result['status']==expected_status and read(A/'DISPLAY.json')==display
    lines=[]
    for p,l in sorted(loci):
        for ed in READERS:lines.append({'edition':ed,'page':p,'locus':l,'groups':[dict(r) for r in conn.execute('SELECT '+','.join(wp.COLUMNS)+' FROM groups WHERE edition=? AND page=? AND locus=? ORDER BY source_group_index',(ed,p,l))]})
    conn.close();assert lines==read(A/'WITNESS_LINES.json')
    for ed in READERS:
        assert result['readers']['EDGE'][ed]['minimum_errors']>=result['readers']['FULL'][ed]['minimum_errors']
        for key,(ys,ds) in maps['FULL',ed].items():
            if ys and ds:
                a,b=maps['EDGE',ed][key[:6]+(key[6][-1],key[7][0])];assert a and b
    fixtures=0
    for a,b,c,d in product(range(5),repeat=4):
        n=min(a,b)+min(c,d);brute=min((b if first==0 else a)+(d if second==0 else c) for first,second in product((0,1),repeat=2));assert n==brute
        assert min(a+c,b+d)>=n;fixtures+=1
    out={'status':'PASS','same_author':True,'native_meanings_validated':False,'scope':'Independent cache SQL neighbour extraction, exact cell arithmetic and literal source display only; shared guarded cache','events':len(events),'cells':len(cells),'display_pairs':len(display),'source_lines':len(lines),'small_choice_fixtures':fixtures,'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
