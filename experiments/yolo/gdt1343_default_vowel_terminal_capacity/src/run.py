from pathlib import Path
from collections import Counter
import gzip,hashlib,json,itertools
B=Path(__file__).resolve().parents[1];R=B.parents[2]
P=R/'research_registry/proposals/production_origin_supply_20261003'
INPUT='experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz'
CLEAR={'DEFINITE_SPACE','LINE_START','LINE_END'}
def save(name,x):(B/'artifacts'/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def proof():
    C={'C0','C1'};V={'V0','V1'}
    def encode(w):
        out=[];i=0
        while i<len(w):
            x=w[i]
            if x in V:out.append(x);i+=1
            elif i+1<len(w) and w[i+1] in V:
                out.append(x)
                if w[i+1]!='V0':out.append(w[i+1])
                i+=2
            else:out.extend([x,x]);i+=1
        return out
    cases=0
    for n in range(1,6):
        for w in itertools.product(sorted(C|V),repeat=n):
            out=encode(w)
            if w[-1] in C:assert len(out)>=2 and out[-1]==out[-2]
            cases+=1
    assert encode(['C0'])==encode(['C0','V0','C0','V0'])==['C0','C0']
    return {'source_free_cases':cases,'necessary_implication':'PASS','converse_counterexample':{'source':['C0','V0','C0','V0'],'output':['C0','C0']}}
def main():
    for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    save('PROOF_CHECK.json',proof())
    signs=json.loads((P/'DEFAULT_VOWEL_DOUBLING_WRITER_RAW_20261011.json').read_text())['design']['working_inventory'];assert len(set(signs))==22
    ordered=sorted(signs,key=lambda s:(-len(s),s))
    def parse(w):
        i=0;out=[]
        while i<len(w):
            a=next((a for a in ordered if w.startswith(a,i)),None)
            if a is None:return None
            out.append(a);i+=len(a)
        return out or None
    source=json.loads(gzip.decompress((R/INPUT).read_bytes()));assert len(source)==94855
    assert len({r['id'] for r in source})==len(source)
    assert all(not r['page'].startswith('f84') and r['page'] not in {'f1r','f116v'} for r in source)
    classes=[];witness=[];summaries={}
    for ed in ['ZL3b','IT2a','RF1b']:
        rows=[r for r in source if r['edition']==ed];counts=Counter({s:0 for s in signs});reasons=Counter();N=0
        for r in rows:
            units=parse(r['raw']);clear=r['left'] in CLEAR and r['right'] in CLEAR
            reason='STRICT' if units and clear else 'PARSE_AND_SEAM_UNCERTAIN' if not units and not clear else 'PARSE_UNCERTAIN' if not units else 'SEAM_UNCERTAIN'
            reasons[reason]+=1;double=bool(reason=='STRICT' and len(units)>1 and units[-1]==units[-2])
            classes.append([r['id'],reason,units[-1] if reason=='STRICT' else None,double])
            if reason=='STRICT':N+=1
            if double:counts[units[-1]]+=1;witness.append(dict(source=r,units=units))
        U=len(rows)-N;D=sum(counts.values());M=sum(sorted(counts.values(),reverse=True)[:17])
        summaries[ed]={'total_P_groups':len(rows),'strict_N':N,'excluded_U':U,'exclusion_account':dict(reasons),'final_doubles_D':D,'final_double_counts':dict(sorted(counts.items())),'seventeen_body_max_M':M,'strict_upper_fraction':M/N,'all_raw_upper_fraction_if_one_word_per_raw_group':(M+U)/len(rows)}
    (B/'artifacts/CLASSIFICATION.json.gz').write_bytes(gzip.compress(json.dumps(classes,separators=(',',':')).encode(),mtime=0))
    save('WITNESSES.json',witness);save('RESULT.json',{'status':'CONDITIONAL_TERMINAL_CODA_CAPACITY_BOUND','readers':summaries,'claim_ceiling':'Conditional source-ending capacity only; no source selected, model fit, phoneme mapping or semantic word value.'})
    print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
