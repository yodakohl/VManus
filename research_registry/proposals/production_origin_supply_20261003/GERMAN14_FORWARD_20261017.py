#!/usr/bin/env python3
"""Partial source-writing demonstration only; never a native decoder."""
import json
from pathlib import Path
D=Path(__file__).resolve().parent

def encode(word):
 out=[];i=0
 while i<len(word):
  c=word[i];final=i==len(word)-1
  if word.startswith('ei',i):out.append('o');i+=2;continue
  if c in 'dr':out.append(c)
  elif c=='e':out.append('y' if final else 'a')
  elif c=='s' and i==0:out.append('q')
  elif c=='s' and final:out.append('l')
  elif c=='n':out.extend(['i','n'] if final else ['k'])
  elif c=='m' and final:out.extend(['i','i','n'])
  else:raise ValueError('Unassigned source letter/position: '+repr(c))
  i+=1
 return ''.join(out)

def main():
 source=json.loads((D/'GERMAN14_RAW_TABLE_20261017.json').read_text())
 checks=[]
 for row in source['source_word_output_pairs']:
  out=encode(row['source_word']);assert out==row['output_raw_form']
  checks.append({'source_word':row['source_word'],'output':out})
 extra=[{'source_word':w,'output':encode(w)} for w in ['ein','sein','deine','deiner','deines','deinen','deinem']]
 partial=[{'source_word':w,'core_output':encode(w)} for w in ['eis','eir','em','en']]
 not_licensed=[]
 for w in ['desde','deseir','desdem']:
  try:encode(w)
  except ValueError:not_licensed.append(w)
  else:raise AssertionError('No silent medial-s extension allowed')
 print(json.dumps({'status':'PASS_PARTIAL_SOURCE_WRITER_ACCOUNTING_ONLY','fitted_14':checks,'additional_outputs_without_new_rules':extra,'offered_partial_core_preimages':partial,'unlicensed_medial_s_expansions':not_licensed,'limits':'No inverse uniqueness, full German alphabet, historical writer, native word meaning or translated passage.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
