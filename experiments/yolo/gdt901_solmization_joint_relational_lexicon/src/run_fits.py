#!/usr/bin/env python3
"""Ten independently bounded complete role cases, 20 CPU workers in total."""
import concurrent.futures,json,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def run(case):
    output=BASE/'artifacts'/f'FIT_IT2a_{case:02}.json';started=time.monotonic()
    try:
        p=subprocess.run([sys.executable,str(BASE/'src/fit.py'),'--case-index',str(case),'--budget-seconds','1800','--workers','2','--output',str(output)],capture_output=True,text=True,timeout=1820)
        receipt={'case':case,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed_seconds':time.monotonic()-started}
    except subprocess.TimeoutExpired:
        receipt={'case':case,'status':'OUTER_TIMEOUT','elapsed_seconds':time.monotonic()-started,'partial_output_exists':output.exists()}
    print(json.dumps(receipt),flush=True);return receipt
def main():
    start=time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:receipts=list(pool.map(run,range(10)))
    (BASE/'artifacts/FIT_RUN_RECEIPT.json').write_text(json.dumps({'cases':receipts,'wall_seconds':time.monotonic()-start},indent=2)+'\n')
if __name__=='__main__':main()
