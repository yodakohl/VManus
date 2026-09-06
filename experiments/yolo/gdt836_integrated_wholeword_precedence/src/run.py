#!/usr/bin/env python3
"""Build the integrated engine or enforce the stopped historical source gate."""
import argparse,json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);m=p.add_mutually_exclusive_group(required=True);m.add_argument('--build',action='store_true');m.add_argument('--fit',action='store_true');a=p.parse_args()
    if a.build:
        output=E/'runtime/decoder';output.parent.mkdir(exist_ok=True)
        subprocess.run(['g++','-std=c++17','-O3','-DNDEBUG',str(E/'src/decoder.cpp'),'-o',str(output)],check=True)
        print('ENGINE_BUILT; no source plaintext, ciphertext, key or fit used');return 0
    cap=json.loads((E/'prepared/CAPACITY.json').read_text())
    if cap['status']=='SOURCE_CAPACITY_STOP':
        print(json.dumps({'status':'SOURCE_CAPACITY_STOP','historical_fits':0,'keys_generated':0,'reason':'Fixed source prerequisites failed; implementation is engineering-validated only'}));return 2
    raise RuntimeError('GDT836 is a frozen source-stop experiment; any fresh data/fit needs its own registered experiment')
if __name__=='__main__':raise SystemExit(main())
