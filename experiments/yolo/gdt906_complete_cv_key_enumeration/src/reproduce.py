#!/usr/bin/env python3
"""Run the full fixed experiment; external cache paths are CLI inputs only."""
import argparse,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True);a=ap.parse_args()
    common=['--work-dir',str(a.work_dir/'primary'),'--cache-dir',str(a.cache_dir)]
    for stage in ('prepare','fit','collect'):
        subprocess.run([sys.executable,str(E/'src/run.py'),'--stage',stage,*common],check=True)
    subprocess.run([sys.executable,str(E/'src/explain_keys.py'),'--cache-dir',str(a.cache_dir)],check=True)
    subprocess.run([sys.executable,str(E/'src/validate_complete.py'),'--cache-dir',str(a.cache_dir),'--primary-work-dir',str(a.work_dir/'primary'),'--work-dir',str(a.work_dir/'independent'),'--workers','32'],check=True)
    subprocess.run([sys.executable,str(E/'src/pack_independent.py'),'--work-dir',str(a.work_dir/'independent')],check=True)
    subprocess.run([sys.executable,str(E/'src/validate.py')],check=True)
if __name__=='__main__':main()
