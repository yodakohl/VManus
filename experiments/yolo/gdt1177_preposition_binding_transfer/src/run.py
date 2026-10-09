#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
P=ROOT/'experiments/yolo/gdt1176_natural_text_word_partition/src/run.py'
def execute():
 spec=importlib.util.spec_from_file_location('source_word_partition',P)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.D=D;m.A=A
 source,excluded,groups,r=m.execute();r['experiment']='GDT1177'
 r['design_collections']=['b4','w1'];r['transfer_collections']=['bs1','gr1']
 return source,excluded,groups,r

def main():
 source,excluded,groups,r=execute()
 for name,x in [('SOURCE_TEXTS',source),('EXCLUDED',excluded),('PARTITIONS',groups),('RESULT',r)]:
  (A/(name+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'scope':r['source_scope'],'metrics':r['metrics'],'passing_partitions':r['passing_partitions']},indent=2))
if __name__=='__main__':main()
