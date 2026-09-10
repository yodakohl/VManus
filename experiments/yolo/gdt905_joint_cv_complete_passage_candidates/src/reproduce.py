#!/usr/bin/env python3
"""Run unchanged construction, lossless packing, and independent validation."""
import argparse,subprocess,sys
from pathlib import Path
S=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--cache-dir',required=True);p.add_argument('--work-dir',required=True);a=p.parse_args()
    for stage in ['intake','scan','fit']:
        subprocess.run([sys.executable,str(S/'run.py'),'--cache-dir',a.cache_dir,'--work-dir',a.work_dir,'--stage',stage],check=True)
    subprocess.run([sys.executable,str(S/'explain_lexical_keys.py'),'--cache-dir',a.cache_dir],check=True)
    subprocess.run([sys.executable,str(S/'pack_artifacts.py')],check=True)
    subprocess.run([sys.executable,str(S/'validate_independent.py'),'--cache-dir',a.cache_dir],check=True)
    subprocess.run([sys.executable,str(S/'validate.py'),'--cache-dir',a.cache_dir],check=True)
if __name__=='__main__':main()
