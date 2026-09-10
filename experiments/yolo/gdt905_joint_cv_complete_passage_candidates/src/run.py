#!/usr/bin/env python3
"""Bounded exact construction; no language score, held data or source-copy crib."""
import argparse, collections, csv, datetime, gzip, hashlib, importlib.util, io, json, pickle, struct, subprocess, sys, time
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
PRE=ROOT/'experiments/yolo/gdt892_joint_abugida_paradigm_reconstruction'
sys.path.insert(0,str(PRE/'src'))
import core, csp, grammar
ALPHABET='acdefghiklmnopqrstxy'
STOP_AT=None

def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(E/'artifacts'/n).write_text(enc(x))
def read(n):return json.loads((E/'artifacts'/n).read_text())
def remaining():return float('inf') if STOP_AT is None else (STOP_AT-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def check_lock():
    for p,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/p)==h,p
def reference(cache, patterns=False):
    meta=json.loads((PRE/'artifacts/REFERENCE.json').read_text())
    names=['reference.pkl']+(['patterns_'+v+'.pkl' for v in core.VOWELS] if patterns else [])
    for n in names:assert sha(cache/n)==meta['cache_files'][n]['sha256'],n
    with (cache/'reference.pkl').open('rb') as f:ref=pickle.load(f)
    assert len(ref['forms'])==425561
    return ref
def selected(target):
    return [(ed,r) for ed,rs in sorted(target['panels'].items()) for r in sorted(rs,key=lambda x:x['paragraph_id']) if 12<=len(r['words'])<=24]
def intake():
    old=module(ROOT/'experiments/yolo/gdt904_vinidarius_complete_relational_register/src/run.py','gdt904_intake')
    target=old.intake();write('TARGET.json',target)
    scope={ed:dict(total=len(rs),selected=sum(12<=len(r['words'])<=24 for r in rs),excluded=[dict(paragraph_id=r['paragraph_id'],word_count=len(r['words']),reason='OUTSIDE_REGISTERED_12_24_GROUP_SCOPE') for r in rs if not 12<=len(r['words'])<=24]) for ed,rs in target['panels'].items()}
    write('SCOPE.json',scope);print(enc({ed:{k:v for k,v in d.items() if k!='excluded'} for ed,d in scope.items()}),flush=True)
def scans(cache,work):
    reference(cache,True)
    # Reexport the exact hash-bound pattern indexes, never trust an old binary.
    pattern_file=work/'pattern_sets.bin'
    with pattern_file.open('wb') as out:
        for v in core.VOWELS:
            with (cache/('patterns_'+v+'.pkl')).open('rb') as f:index=pickle.load(f)
            out.write(struct.pack('<I',len(index)))
            for pat in sorted(index):out.write(struct.pack('<H',len(pat)));out.write(bytes(pat))
    binary=work/'maskscan'
    subprocess.run(['g++','-O3','-std=c++17','-fopenmp',str(PRE/'src/maskscan.cpp'),'-o',str(binary)],check=True)
    dest=E/'artifacts/mask_scans';dest.mkdir(exist_ok=True)
    output=[]
    for ed,r in selected(read('TARGET.json')):
        row=dict(edition=ed,paragraph_id=r['paragraph_id'],word_count=len(r['words']))
        if set(''.join(r['words']))-set(ALPHABET):
            row.update(status='OUTSIDE_CHANNEL_ALPHABET',surviving_masks=0,outside_characters=sorted(set(''.join(r['words']))-set(ALPHABET)))
        elif remaining()<=0:row.update(status='UNKNOWN_TOTAL_BUDGET')
        else:
            words=sorted(set(r['words']));inp=work/'input.txt';out=work/'masks.csv'
            inp.write_text(ALPHABET+'\n'+str(len(words))+'\n'+'\n'.join(words)+'\n')
            began=time.monotonic()
            try:
                result=subprocess.run([str(binary),str(pattern_file),str(inp),str(out)],check=True,capture_output=True,text=True,timeout=min(60,remaining()))
                summary=json.loads(result.stdout);data=out.read_bytes()
                p=dest/(ed+'_'+r['paragraph_id']+'.csv.gz');p.write_bytes(gzip.compress(data,mtime=0))
                row.update(summary,masks_path=str(p.relative_to(E)),masks_sha256=sha(p),uncompressed_sha256=hashlib.sha256(data).hexdigest())
            except subprocess.TimeoutExpired:row.update(status='UNKNOWN_SCANNER_BUDGET')
            row['elapsed_seconds']=round(time.monotonic()-began,6)
        output.append(row);write('SCANS.json',output)
        print(enc({k:v for k,v in row.items() if k not in ('masks_sha256','uncompressed_sha256')}),flush=True)
def completion(observed,mask,v):
    singles={c for i,c in enumerate(ALPHABET) if mask&(1<<i)}
    key={comp:code for code,comp in observed.items()}
    unused=sorted(singles-set(observed))
    unused += [a+b for a in ALPHABET if a not in singles for b in ALPHABET if a+b not in observed]
    for comp,code in zip((x for x in core.inventory(v) if x not in key),unused):key[comp]=code
    assert len(key)==len(set(key.values()))==27 and core.prefix_free(key.values())
    assert singles<=set(key.values())
    return key
class WitnessLimit(Exception):pass
def fit_one(ed,r,scan,ref,indexes):
    result=dict(edition=ed,paragraph_id=r['paragraph_id'],witnesses=[],cases=[],status='COMPLETE')
    if scan['status']!='COMPLETE':result['status']=scan['status'];return result
    if not scan['surviving_masks']:result['status']='UNSAT_LEXICAL_PATTERN';return result
    masks=list(csv.DictReader(io.StringIO(gzip.decompress((E/scan['masks_path']).read_bytes()).decode())))
    words=sorted(set(r['words']));groups={}
    for row in masks:
        mask=int(row['mask']);singles={c for i,c in enumerate(ALPHABET) if mask&(1<<i)}
        seg=tuple(core.segment(w,singles) for w in words);assert all(seg)
        key=(seg,int(row['inherent_bits']))
        groups.setdefault(key,[]).append(mask)
    result['segmentation_classes']=len(groups)
    deadline=time.monotonic()+min(20,max(0,remaining()))
    complete=True
    for (segs,bits),equivalent in groups.items():
        mask=equivalent[0];codewords=sorted({c for seq in segs for c in seq});ids={c:i for i,c in enumerate(codewords)}
        word_segs=dict(zip(words,segs))
        for vi,v in enumerate(core.VOWELS):
            if not bits&(1<<vi):continue
            if time.monotonic()>=deadline:complete=False;break
            parts=core.inventory(v);part_ids={p:i for i,p in enumerate(parts)};tables=[]
            for w,seg in zip(words,segs):
                unique=list(dict.fromkeys(seg));first=[seg.index(c) for c in unique]
                rows={tuple(part_ids[cs[i]] for i in first) for _,cs in indexes[v][core.pattern(seg)]}
                tables.append(dict(vars=[ids[c] for c in unique],rows=sorted(rows)))
            if time.monotonic()>=deadline:complete=False;break
            def accept(values):
                observed={c:parts[values[ids[c]]] for c in codewords};decoded={}
                for w,seg in word_segs.items():
                    plain=core.decode_components(tuple(observed[c] for c in seg),v)
                    assert plain in ref['analyses'];decoded[w]=plain
                plaintext=[decoded[w] for w in r['words']]
                analyses=[ref['analyses'][w] for w in plaintext]
                if not grammar.accepts(ref['grammar'],analyses):return False
                witness=dict(inherent=v,mask=mask,equivalent_masks=equivalent,observed_key=observed,complete_key=completion(observed,mask,v),plaintext=plaintext,analyses=analyses)
                result['witnesses'].append(witness)
                if len(result['witnesses'])>=64:raise WitnessLimit()
                return True
            try:
                solved=csp.solve_tables(tables,len(codewords),27,deadline,accept=accept)
                result['cases'].append(dict(mask=mask,equivalent_masks=equivalent,inherent=v,status=solved['status'],stats=solved['stats']))
                if solved['status']!='COMPLETE':complete=False;break
            except WitnessLimit:
                result['status']='UNKNOWN_WITNESS_LIMIT';return result
        if not complete:break
    result['status']=('COMPLETE_CANDIDATES' if result['witnesses'] else 'UNSAT_SHARED_KEY_OR_GRAMMAR') if complete else 'UNKNOWN_BUDGET'
    return result
def fits(cache):
    ref=reference(cache,True);indexes={}
    for v in core.VOWELS:
        with (cache/('patterns_'+v+'.pkl')).open('rb') as f:indexes[v]=pickle.load(f)
    sx={(x['edition'],x['paragraph_id']):x for x in read('SCANS.json')};output=[]
    for ed,r in selected(read('TARGET.json')):
        x=fit_one(ed,r,sx[ed,r['paragraph_id']],ref,indexes);output.append(x);write('CANDIDATES.json',output)
        print(enc(dict(edition=ed,paragraph_id=r['paragraph_id'],status=x['status'],witnesses=len(x['witnesses']))),flush=True)
    summary=dict(experiment_id='GDT905',paragraphs=len(output),statuses=dict(collections.Counter(x['status'] for x in output)),candidate_keys=sum(len(x['witnesses']) for x in output),candidate_paragraphs=sum(bool(x['witnesses']) for x in output),confirmed_meanings=0,claim_ceiling='Exploratory complete-passage constructions under the unvalidated fixed Latin/CV hypothesis; no held data or semantic validation.')
    write('RESULT.json',summary);print(enc(summary),flush=True)
def main():
    global STOP_AT
    ap=argparse.ArgumentParser();ap.add_argument('--cache-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True);ap.add_argument('--stage',choices=['intake','scan','fit'],required=True);ap.add_argument('--stop-at-utc');a=ap.parse_args()
    if a.stop_at_utc:STOP_AT=datetime.datetime.fromisoformat(a.stop_at_utc);assert STOP_AT.utcoffset()==datetime.timedelta(0)
    check_lock();a.work_dir.mkdir(parents=True,exist_ok=True)
    if a.stage=='intake':intake()
    elif a.stage=='scan':scans(a.cache_dir,a.work_dir)
    else:fits(a.cache_dir)
if __name__=='__main__':main()
