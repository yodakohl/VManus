#!/usr/bin/env python3
"""Verify registered existing sources without parsing manuscript rows."""
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def main():
 source=json.loads((BASE/'src/SOURCE.json').read_text())
 for x in source['sources']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
 print('REGISTERED_SOURCE_PINS_PASS; not a reading or meaning test')
if __name__=='__main__':main()
