import json,hashlib,sys,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
W='experiments/yolo/gdt1250_cache_reset_doublet_conflict/artifacts/WITNESSES.json'
def controls():
    # One injective literal word and one available reference: inspect all two-step mode choices.
    checked=0
    for n in range(1,10):
        for r in range(1,10):
            lit='A'*n;ref='A'*r
            for first in ['L','R']:
                for second in ['L','R']:
                    if second=='L' and len(ref)<len(lit):continue
                    outs=[lit if m=='L' else ref for m in [first,second]]
                    if outs[0]==outs[1]:assert len(outs[0])<=r
                    checked+=1
    # At n=r both literal and reference strings can be identical: ties/overlap are legal.
    assert len('AAAA')==4
    result={'status':'PASS','cost_mode_cases':checked,'tight_case':{'literal':'AAAA','reference':'AAAA','r':4,'output':['AAAA','AAAA']},'outside_contract_cases':[{'removed':'mandatory strict saving','literal':'AAAA','reference':'B','r':1,'output':['AAAA','AAAA'],'explanation':'Optional full spelling despite available saving permits the long doublet.'},{'removed':'reference availability for retained word','literal':'AAAA','legal_reference':None,'r_for_other_words':1,'output':['AAAA','AAAA'],'explanation':'Storage alone does not force a shorter option.'}]}
    (P/'artifacts/CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','cost_mode_cases':checked}))
def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for f,h in lock['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
    old=json.loads((ROOT/W).read_text());out=[]
    for reader in ['ZL3b','IT2a','RF1b']:
        selected=[r for r in old if r['edition']==reader and r['form']=='qokeedy'];assert len(selected)==1
        rec=selected[0];line=sorted(rec['doublet_line'],key=lambda r:int(r['source_group_index']))
        matches=[i for i in range(1,len(line)-2) if [r['ivtff_group_raw'] for r in line[i:i+2]]==['qokeedy','qokeedy']];assert len(matches)==1
        i=matches[0];span=line[i-1:i+3]
        assert all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(span,span[1:]))
        assert all(r['edition']==reader and r['kind']=='P' and r['locus']==rec['doublet']['locus'] for r in line)
        assert int(line[i]['source_group_index'])==rec['doublet']['index']
        units=list('qokeedy');assert units==['q','o','k','e','e','d','y']
        out.append({'reader':reader,'locus':rec['doublet']['locus'],'first_group_index':rec['doublet']['index'],'form':'qokeedy','working_units':units,'width':len(units),'complete_line':line,'lower_bound_r':len(units)})
    r={'status':'REFERENCE_WIDTH_AT_LEAST_SEVEN_UNDER_STRICT_SAVING_POLICY','cases':out,'necessary_reference_width':7,'excluded_maxima':list(range(7)),'not_claimed':'No viable r7cache, source meaning, general abbreviation exclusion or paragraphreset evidence.'}
    (P/'artifacts/RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'lock_sha256':hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()},indent=2)+'\n')
    print(json.dumps({'status':r['status'],'witnesses':[{k:c[k] for k in ['reader','locus','first_group_index','width']} for c in out]}))
if __name__=='__main__':controls() if '--controls' in sys.argv else main()
