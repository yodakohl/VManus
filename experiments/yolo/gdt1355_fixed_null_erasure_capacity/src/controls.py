from pathlib import Path
import json,runpy
B=Path(__file__).resolve().parents[1]
def main():
    primary=runpy.run_path(str(B/'src/run.py'))['optimize'];independent=runpy.run_path(str(B/'src/validate.py'))['direct'];alpha=['a','b','c'];families=0
    for family in range(128):
        masks={s for s in range(1,8) if family>>(s-1)&1};supports=[frozenset(alpha[i] for i in range(3) if m>>i&1) for m in sorted(masks)]
        for ww in [[1,1,1],[3,5,7],[0,2,3]]:
            a=primary(alpha,ww,masks);b=independent(alpha,dict(zip(alpha,ww)),supports);assert a==b,(family,ww,a,b);families+=1
    pure=primary(['a'],[3],{1});assert pure['max_mass']['erased_tokens']==0
    out={'status':'PASS','support_family_weight_cases':families,'pure_run_support_case':1,'native_data_read':False};(B/'artifacts/PRETARGET_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
