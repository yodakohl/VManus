"""Literal native countercases to a fixed deterministic local spelling rule."""
from pathlib import Path
from collections import defaultdict,Counter
import sys,json,re,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';sys.path.insert(0,str(ROOT))
from tools import word_profiles as wp
READERS=('ZL3b','IT2a','RF1b');MODES=('FULL','EDGE')
BANK=ROOT/'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts/RESULT.json'
RECEIPT=ROOT/'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts/SOURCE_RECEIPT.json'
def save(name,obj):(A/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def literal(s):return re.fullmatch('[a-z]+',s) is not None
def main():
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    bases=sorted(set(json.loads(BANK.read_text())['non_dal_joint']['base_family'])|{'dal'})
    forms=defaultdict(list)
    for b in bases:
        for variant in ('y','dy'):forms[b+variant].append((b,variant))
    conn=wp.ensure_cache(ROOT);receipt=wp.receipt(conn);assert receipt==json.loads(RECEIPT.read_text())
    pages=set(receipt['inputs']['selectors']);assert len(pages)==179 and not any(p.startswith('f84') or p=='f116v' for p in pages)
    rows=[dict(r) for r in conn.execute('SELECT '+','.join(wp.COLUMNS)+' FROM groups ORDER BY edition,page,locus,source_group_index')];conn.close()
    lines=defaultdict(list)
    for row in rows:
        assert row['page'] in pages and row['edition'] in READERS
        lines[row['edition'],row['page'],row['locus']].append(row)
    events=[]
    for key,line in sorted(lines.items()):
        for l,t,r in zip(line,line[1:],line[2:]):
            word=t['ivtff_group_raw']
            if t['kind']!='P' or word not in forms or not all(literal(x['ivtff_group_raw']) for x in (l,t,r)):continue
            if not(l['source_group_index']+1==t['source_group_index'] and t['source_group_index']+1==r['source_group_index']):continue
            seams=[l['right_separator'],t['left_separator'],t['right_separator'],r['left_separator']]
            if any(x!='DEFINITE_SPACE' for x in seams):continue
            for b,v in forms[word]:
                e={k:t[k] for k in ('edition','page','locus','section','currier','hand','kind','source_group_id','source_group_index','source_group_count')}
                e.update(base=b,variant=v,form=word,previous=l['ivtff_group_raw'],following=r['ivtff_group_raw'],previous_id=l['source_group_id'],following_id=r['source_group_id'],seams=seams,position='INTERNAL')
                events.append(e)
    events.sort(key=lambda e:(e['edition'],e['page'],e['locus'],e['source_group_index'],e['base'],e['variant']))
    for i,e in enumerate(events):e['event_id']=f'E{i:06d}'
    cellmap=defaultdict(list)
    for e in events:
        common=tuple(e[k] for k in ('base','page','section','currier','hand','position'))
        cellmap['FULL',e['edition'],common+(e['previous'],e['following'])].append(e)
        cellmap['EDGE',e['edition'],common+(e['previous'][-1],e['following'][0])].append(e)
    cells=[];stats={};display=[];witness_loci=set()
    for (mode,ed,key),es in sorted(cellmap.items()):
        ys=[e['event_id'] for e in es if e['variant']=='y'];ds=[e['event_id'] for e in es if e['variant']=='dy']
        cells.append({'mode':mode,'edition':ed,'input':list(key),'y':ys,'dy':ds,'mixed':bool(ys and ds),'minimum_errors':min(len(ys),len(ds))})
    byid={e['event_id']:e for e in events}
    for mode in MODES:
        stats[mode]={}
        for ed in READERS:
            cs=[c for c in cells if c['mode']==mode and c['edition']==ed];es=[e for e in events if e['edition']==ed];mixed=[c for c in cs if c['mixed']]
            stats[mode][ed]={'events':len(es),'physical_groups':len({e['source_group_id'] for e in es}),'bases':len({e['base'] for e in es}),'pages':len({e['page'] for e in es}),
                'cells':len(cs),'singleton_cells':sum(len(c['y'])+len(c['dy'])==1 for c in cs),'repeated_cells':sum(len(c['y'])+len(c['dy'])>1 for c in cs),
                'mixed_cells':len(mixed),'mixed_pages':len({c['input'][1] for c in mixed}),'mixed_bases':sorted({c['input'][0] for c in mixed}),
                'minimum_errors':sum(c['minimum_errors'] for c in cs),'decision':'CONTRADICTED' if mixed else 'NO_OBSERVED_CONTRADICTION',
                'metadata_values':{k:dict(sorted(Counter(e[k] for e in es).items())) for k in ('section','currier','hand')}}
            for c in mixed[:4]:
                pair=[c['y'][0],c['dy'][0]];display.append({'mode':mode,'edition':ed,'input':c['input'],'events':pair})
                for eid in pair:e=byid[eid];witness_loci.add((e['page'],e['locus']))
        for ed in READERS:
            assert stats['FULL'][ed]['minimum_errors']<=stats.get('EDGE',{}).get(ed,stats['FULL'][ed])['minimum_errors']
    for c in cells:
        if c['mode']=='FULL' and c['mixed']:
            k=tuple(c['input'][:6])+ (c['input'][6][-1],c['input'][7][0]);es=cellmap['EDGE',c['edition'],k]
            assert {e['variant'] for e in es}=={'y','dy'}
    joint={mode:'CONTRADICTED_IN_ZL_AND_IT' if all(stats[mode][ed]['mixed_cells'] for ed in ('ZL3b','IT2a')) else 'NO_JOINT_COUNTERCASE' for mode in MODES}
    result={'experiment':'GDT1204','status':'FULL_NEIGHBOUR_RULE_CONTRADICTED' if joint['FULL']=='CONTRADICTED_IN_ZL_AND_IT' else 'EDGE_RULE_ONLY_CONTRADICTED' if joint['EDGE']=='CONTRADICTED_IN_ZL_AND_IT' else 'NO_JOINT_LOCAL_RULE_COUNTERCASE',
        'bases':bases,'readers':stats,'joint':joint,'scope':'Conditional literal deterministic spelling-input contradiction only; no semantic difference, morphology, stochastic-rule rejection or independent confirmation.'}
    save('SOURCE_RECEIPT.json',receipt);save('EVENTS.json',events);save('CELLS.json',cells);save('DISPLAY.json',display)
    save('WITNESS_LINES.json',[{'edition':ed,'page':p,'locus':l,'groups':lines.get((ed,p,l),[])} for p,l in sorted(witness_loci) for ed in READERS])
    save('RESULT.json',result);save('RUN_RECEIPT.json',{'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps({'status':result['status'],'bases':len(bases),'joint':joint,'counts':{m:{ed:{k:v for k,v in s.items() if k not in ('metadata_values','mixed_bases')} for ed,s in ss.items()} for m,ss in stats.items()}},indent=2))
if __name__=='__main__':main()
