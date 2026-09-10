#!/usr/bin/env python3
"""Known complete morphological code preservation; no target data."""
from pathlib import Path
from source import load
from role_source import CASES,compile_case
from domains import build
BASE=Path(__file__).resolve().parents[1]
def main():
 source=load(BASE/'artifacts/SOURCE_INPUT.json')
 for case in CASES:
  compiled=compile_case(source,case)
  code={a:('r'+d['roleclass'].replace(':','')+'s'+d['root']+'e' if d['family'] else 'plain'+a) for a,d in compiled['forms'].items()}
  assert len(set(code.values()))==len(code)
  paragraphs=[{'words':[v for a in rec['sequence'] for v in [code[a],'background']]} for rec in compiled['records']]
  result=build(compiled,paragraphs)
  assert result['status']=='DOMAINS_NONEMPTY_MODEL_NOT_SOLVED'
  assert all(code[a] in result['domains'][a] for a in compiled['atoms'])
  assert build(compiled,paragraphs[:-1])['status']=='CAPACITY_STOP'
 print('PASS all ten complete known morphological keys preserved, capacity stops')
if __name__=='__main__':main()
