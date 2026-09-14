"""Fixed-scope whole-form concordance; no semantic inference or normalization."""
from pathlib import Path
import collections,json,hashlib
EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]
TARGETS=['qokal','shedar','dal','chedy','daror']
COMPARE=['okal','qokar','okar','shedy','chedar','dar','darol','lchedy','qokaly']

def build():
    lock=json.loads((EXP/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    rows=json.loads((ROOT/'experiments/yolo/gdt930_label_text_joint_reading/artifacts/SOURCE.json').read_text())['groups']
    lines=collections.defaultdict(list)
    for r in rows: lines[r['edition'],r['locus']].append(r)
    for rr in lines.values(): rr.sort(key=lambda r:int(r['source_group_index']))
    out=[]
    for r in rows:
        if r['ivtff_group_raw'] not in TARGETS+COMPARE: continue
        rr=lines[r['edition'],r['locus']];i=rr.index(r)
        out.append(dict(r,target=r['ivtff_group_raw'] in TARGETS,left_raw=rr[i-1]['ivtff_group_raw'] if i else '',right_raw=rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '',line_groups=rr))
    return {'source_groups':len(rows),'targets':TARGETS,'comparison_forms':COMPARE,'occurrences':out}

if __name__=='__main__':
    d=build();(EXP/'artifacts/CONCORDANCE.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    counts=collections.Counter((r['edition'],r['ivtff_group_raw']) for r in d['occurrences'])
    print('form ZL3b IT2a RF1b')
    for w in TARGETS+COMPARE: print(w,*[counts[e,w] for e in ['ZL3b','IT2a','RF1b']])
    print('\nComplete target lines, ZL3b; RF differing raw lines shown separately later.')
    seen=set()
    for r in d['occurrences']:
        if r['edition']!='ZL3b' or not r['target'] or r['locus'] in seen:continue
        seen.add(r['locus']);print(r['locus'], ' '.join(x['ivtff_group_raw'] for x in r['line_groups']))
