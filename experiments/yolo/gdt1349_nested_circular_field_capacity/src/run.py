from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
import csv,gzip,hashlib,itertools,json,re,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def read(p):
    data=p.read_bytes();return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)
def save(name,obj):
    data=json.dumps(obj,indent=2,sort_keys=True).encode()+b'\n';(B/'artifacts'/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def nested(rows):
    alphabet=sorted({u for r in rows for u in r['units']});parent={u:u for u in alphabet}
    def find(u):
        while parent[u]!=u:u=parent[u]
        return u
    first={}
    for row in rows:first.setdefault(tuple(row['units']),row)
    certificate=[]
    while True:
        found=None
        for word,row in first.items():
            values=[find(u) for u in word]
            for a,b in itertools.combinations(sorted(set(values)),2):
                positions=[];last=None
                for i,v in enumerate(values):
                    if v in (a,b) and v!=last:positions.append(i);last=v
                if len(positions)>=4:found=(a,b,row,positions[:4]);break
            if found:break
        if not found:break
        a,b,row,pos=found;groups=[[u for u in alphabet if find(u)==v] for v in [a,b]]
        certificate.append({'witness':row,'positions':pos,'merged_classes':groups});parent[max(a,b)]=min(a,b)
    groups=defaultdict(list)
    for u in alphabet:groups[find(u)].append(u)
    classes=sorted(groups.values());labels={u:i for i,cs in enumerate(classes) for u in cs}
    activity=[];multi=returns=0;max_used=max_depth=0
    for cs in classes:
        cc=set(cs);activity.append({'units':cs,'unit_tokens':sum(sum(u in cc for u in r['units']) for r in rows),'groups':sum(any(u in cc for u in r['units']) for r in rows),'physical_leaves':len({int(re.match(r'f(\d+)',r['page'])[1]) for r in rows if any(u in cc for u in r['units'])})})
    for row in rows:
        values=[labels[u] for u in row['units']];used=set(values);multi+=len(used)>1;max_used=max(max_used,len(used));intervals={v:(values.index(v),len(values)-1-values[::-1].index(v)) for v in used}
        depth=max(1+sum(a<i and j<b for u,(a,b) in intervals.items() if u!=v) for v,(i,j) in intervals.items());returns+=depth>1;max_depth=max(max_depth,depth)
    return {'classes':classes,'maximum_classes':len(classes),'multi_class_groups_upper_bound':multi,'groups_nested_under_finest':returns,'max_classes_used_in_word_under_finest':max_used,'max_depth_under_finest':max_depth,'activity':activity,'certificate':certificate},labels
def cover_capacity(k,cuts):
    full=(1<<k)-1;allowed=sorted({full,*cuts,*(full^m for m in cuts)})
    if not cuts:return {'status':'EXACT','maximum_classes':1,'partition_masks':[full],'allowed_subset_count':1,'states':0}
    if all((1<<i) in allowed for i in range(k)):return {'status':'EXACT','maximum_classes':k,'partition_masks':[1<<i for i in range(k)],'allowed_subset_count':len(allowed),'states':0}
    if len(allowed)>4096:return {'status':'BOUNDS_ONLY_SUBSET_CAP','lower':2,'upper':k,'partition_masks':[cuts[0],full^cuts[0]],'allowed_subset_count':len(allowed)}
    calls=0
    @lru_cache(None)
    def best(remaining):
        nonlocal calls
        calls+=1
        if calls>200000:raise RuntimeError('state cap')
        if remaining==0:return ()
        low=remaining&-remaining;answer=None
        for part in sorted((a for a in allowed if a&low and a&remaining==a),key=lambda a:(a.bit_count(),a)):
            tail=best(remaining^part)
            if tail is not None and (answer is None or len(tail)+1>len(answer)):answer=(part,)+tail
            if answer is not None and len(answer)==remaining.bit_count():break
        return answer
    try:
        answer=best(full);assert answer
        return {'status':'EXACT','maximum_classes':len(answer),'partition_masks':list(answer),'allowed_subset_count':len(allowed),'states':calls}
    except RuntimeError:return {'status':'BOUNDS_ONLY_STATE_CAP','lower':2,'upper':k,'partition_masks':[cuts[0],full^cuts[0]],'allowed_subset_count':len(allowed),'states':calls}
def circular(rows,nest,labels,binary):
    k=len(nest['classes']);words=sorted({tuple(labels[u] for u in r['units']) for r in rows},key=lambda w:(-len(w),w));text=f'{k} {len(words)}\n'+'\n'.join(str(len(w))+' '+' '.join(map(str,w)) for w in words)+'\n'
    try:cuts=json.loads(subprocess.run([str(binary)],input=text,text=True,capture_output=True,check=True,timeout=60).stdout)
    except subprocess.TimeoutExpired:return {'status':'UNKNOWN_ENUMERATION_TIMEOUT','nested_upper_bound':k}
    capacity=cover_capacity(k,cuts);full=(1<<k)-1;parts=capacity['partition_masks'];class_sets=[[u for i,cs in enumerate(nest['classes']) if part>>i&1 for u in cs] for part in parts]
    word_masks=Counter(sum(1<<i for i in {labels[u] for u in r['units']}) for r in rows);unit_mass=Counter(u for r in rows for u in r['units']);cut_activity=[]
    activity_complete=len(cuts)<=4096
    for mask in cuts if activity_complete else []:
        left={u for i,cs in enumerate(nest['classes']) if mask>>i&1 for u in cs};mixed=sum(f for w,f in word_masks.items() if w&mask and w&(full^mask))
        cut_activity.append({'mask':mask,'mixed_groups':mixed,'selected_unit_tokens':sum(unit_mass[u] for u in left),'selected_groups':sum(f for w,f in word_masks.items() if w&mask),'complement_groups':sum(f for w,f in word_masks.items() if w&(full^mask))})
    assignment={u:i for i,cs in enumerate(class_sets) for u in cs}
    for r in rows:
        v=[assignment[u] for u in r['units']]
        for c in set(v):assert sum(v[i]==c and v[(i+1)%len(v)]!=c for i in range(len(v)))<=1
    return {'status':'ALL_CUTS_ENUMERATED','checked_cuts':(1<<(k-1))-1,'valid_cuts':cuts,'cut_activity':cut_activity,'activity_complete':activity_complete,'max_binary_mixed_groups':max((r['mixed_groups'] for r in cut_activity),default=0) if activity_complete else None,'capacity':capacity,'witness_classes':class_sets}
def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    binary=R/'.cache/gdt1349_cuts';binary.parent.mkdir(exist_ok=True);subprocess.run(['g++','-O2','-std=c++17',str(B/'src/cuts.cpp'),'-o',str(binary)],check=True,capture_output=True)
    data=read(R/SOURCE);allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={}
    for reader,rows in data.items():
        leaves=defaultdict(set)
        for row in rows:
            assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert ''.join(row['units'])==row['ivtff_group_raw'];leaves[tuple(row['units'])].add(int(re.match(r'f(\d+)',row['page'])[1]))
        for label,panel in [('FULL',rows),('PHYSICAL_LEAVES_GE2',[r for r in rows if len(leaves[tuple(r['units'])])>=2])]:
            n,labels=nested(panel);c=circular(panel,n,labels,binary);name=reader+'_'+label;results[name]={'groups':len(panel),'types':len({tuple(r['units']) for r in panel}),'nested':n,'circular':c};print(json.dumps({'panel':name,'groups':len(panel),'nested_classes':n['classes'],'nested_multi':n['multi_class_groups_upper_bound'],'circular_cuts':len(c.get('valid_cuts',[])),'circular_capacity':c.get('capacity')},sort_keys=True),flush=True)
    save('RESULT.json',{'status':'NESTED_AND_CIRCULAR_FIELD_CAPACITY','panels':results})
if __name__=='__main__':main()
