"""Retrospective fixed-event raw source fidelity; no model fit."""
import csv, hashlib, io, json, subprocess
from collections import defaultdict, Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
A=E/'artifacts'; R=E/'runtime'
def digest(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def require(ok,message):
    if not ok:raise ValueError(message)
def table(rows,cols):
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return f.getvalue()
def acquire(spec):
    with (ROOT/spec['allowlist']).open(newline='') as f:pages=[r['page'] for r in csv.DictReader(f,delimiter='\t')]
    require(len(pages)==len(set(pages))==179 and not any(p.startswith('f84') for p in pages),'allowlist')
    data={};projections={};R.mkdir(exist_ok=True)
    for name,source in spec['sources'].items():
        args=[str(ROOT/'vmanus-exp'),'query-tsv',str(ROOT/source['path']),'--selector',source['selector'],'--allow',','.join(pages),'--columns',','.join(source['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
        proc=subprocess.run(args,capture_output=True,check=True)
        stats=[json.loads(line.removeprefix('GUARD_STATS ')) for line in proc.stderr.decode().splitlines() if line.startswith('GUARD_STATS ')]
        require(len(stats)==1,'guard stats '+name)
        (R/(name+'.tsv')).write_bytes(proc.stdout)
        projections[name]={'path':source['path'],'sha256':digest(proc.stdout),'bytes':len(proc.stdout),'guard_stats':stats[0]}
        data[name]=list(csv.DictReader(io.StringIO(proc.stdout.decode()),delimiter='\t'))
        require(stats[0]['selected']==len(data[name]),'guard row count '+name)
    write(A/'PROJECTIONS.json',projections)
    return data

def audit(spec,data):
    events=data['EVENTS'];require(len(events)==1777 and len({e['event_id'] for e in events})==1777,'event population')
    old={e['event_id']:e for e in read(ROOT/spec['baseline_metadata'])}
    require(set(old)=={e['event_id'] for e in events},'865 event IDs')
    for e in events:
        b=old[e['event_id']]
        require(all(str(b[k])==e[k] for k in ['carrier','axis','surface','page','locus','token_index']),'865 event metadata '+e['event_id'])
    cross={(r['page'],r['locus']):r for r in data['CROSS']}
    require(len(cross)==len(data['CROSS']),'duplicate cross line')
    wanted={(e['page'],e['locus']) for e in events}
    grouped=defaultdict(list)
    ids=set()
    for row in data['ATLAS']:
        require(row['source_group_id'] not in ids,'duplicate atlas source group');ids.add(row['source_group_id'])
        if (row['page'],row['locus']) in wanted and row['edition'] in spec['editions']:
            grouped[(row['page'],row['locus'],row['edition'])].append(row)
    lines=[];positions={}
    for page,locus in sorted(wanted):
        require((page,locus) in cross,'missing cross '+locus)
        for edition,fields in sorted(spec['editions'].items()):
            key=(page,locus,edition);groups=sorted(grouped[key],key=lambda r:int(r['source_group_index']))
            n=len(groups)
            require(n>0 and [int(r['source_group_index']) for r in groups]==list(range(1,n+1)),'incomplete group indices '+str(key))
            require(all(int(r['source_group_count'])==n for r in groups),'group count '+str(key))
            flat=[];pmap={}
            for i,g in enumerate(groups):
                fs=g['clean_ascii_fragments'].split();count=len(fs)
                status='ZERO_ASCII_FRAGMENT' if count==0 else 'ONE_ASCII_FRAGMENT' if count==1 else 'MULTI_ASCII_FRAGMENT'
                ps=[int(x) for x in g['legacy_surface_positions_1based'].split(',')] if g['legacy_surface_positions_1based'] else []
                require(int(g['clean_ascii_fragment_count'])==count and g['legacy_mapping_status']==status,'fragment count/status '+g['source_group_id'])
                require(ps==list(range(len(flat)+1,len(flat)+count+1)),'noncontiguous source positions '+g['source_group_id'])
                if i: require(groups[i-1]['right_separator']==g['left_separator'],'separator mismatch '+g['source_group_id'])
                for pos,fragment in zip(ps,fs):
                    require(pos not in pmap,'ambiguous position '+str(key));pmap[pos]=(g,fragment)
                flat.extend(fs)
            require(flat==cross[(page,locus)][fields['clean']].split(),'full clean line parity '+str(key))
            positions[key]=pmap
            lines.append({'page':page,'locus':locus,'edition':edition,'groups':n,'tokens':len(flat),'sequence_sha256':digest(' '.join(flat).encode()),'passed':True})
    # No target category is computed until all complete lines pass parity.
    targets=[]
    for event in sorted(events,key=lambda e:e['event_id']):
        for edition,fields in sorted(spec['editions'].items()):
            key=(event['page'],event['locus'],edition);position=int(event[fields['position']]);pmap=positions[key]
            require(position in pmap,'missing target position '+event['event_id']+'/'+edition)
            g,fragment=pmap[position]
            require(fragment==event['surface'],'target surface mismatch '+event['event_id']+'/'+edition)
            count=int(g['clean_ascii_fragment_count'])
            category='CLEANER_FRAGMENT' if count>1 else 'EXACT_RAW_WHOLE' if g['ivtff_group_raw']==event['surface'] else 'NORMALIZED_WHOLE'
            targets.append({**{k:event[k] for k in ['event_id','page','locus','axis','carrier','surface']},'edition':edition,'position':position,'source_group_id':g['source_group_id'],'source_group_index':int(g['source_group_index']),'raw':g['ivtff_group_raw'],'fragment_count':count,'category':category,'left_separator':g['left_separator'],'right_separator':g['right_separator']})
    def counts(rows):
        c=Counter(r['category'] for r in rows);return {k:c[k] for k in spec['categories']}
    byevent=defaultdict(list)
    for t in targets:byevent[t['event_id']].append(t)
    result={'status':'COMPLETE_FIXED_EVENT_RAW_GROUP_FIDELITY','claim_ceiling':spec['claim_ceiling'],'event_count':len(events),'target_count':len(targets),'line_reading_count':len(lines),
        'by_edition':{ed:counts([t for t in targets if t['edition']==ed]) for ed in spec['editions']},
        'by_edition_axis':{ed:{ax:counts([t for t in targets if t['edition']==ed and t['axis']==ax]) for ax in ['L','DY']} for ed in spec['editions']},
        'all_three_exact':sum(all(t['category']=='EXACT_RAW_WHOLE' for t in ts) for ts in byevent.values()),
        'all_three_single_group':sum(all(t['category']!='CLEANER_FRAGMENT' for t in ts) for ts in byevent.values()),
        'events_any_cleaner_fragment':sum(any(t['category']=='CLEANER_FRAGMENT' for t in ts) for ts in byevent.values()),
        'uncertain_boundary_targets':sum('UNCERTAIN_SMALL_SPACE' in (t['left_separator'],t['right_separator']) for t in targets),
        'drawing_boundary_targets':sum(any(t[k].startswith('DRAWING_') for k in ['left_separator','right_separator']) for t in targets)}
    write(A/'EVENTS.json',events);write(A/'LINE_PARITY.json',lines);write(A/'TARGETS.json',targets)
    for edition in spec['editions']:
        rows=sorted([r for r in data['ATLAS'] if r['edition']==edition and (r['page'],r['locus']) in wanted],key=lambda r:(r['page'],r['locus'],int(r['source_group_index'])))
        (A/('SOURCE_GROUPS_'+edition+'.tsv')).write_text(table(rows,spec['sources']['ATLAS']['columns']))
    return result

def main():
    for p,h in read(E/'src/PREREG_LOCK.json').items():require(digest((ROOT/p).read_bytes())==h,'locked bytes '+p)
    spec=read(E/'src/SPEC.json')
    try: result=audit(spec,acquire(spec))
    except (ValueError,KeyError) as err: result={'status':'STOP_SOURCE_CONTRACT','reason':str(err),'claim_ceiling':spec['claim_ceiling']}
    write(A/'RESULT.json',result);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
