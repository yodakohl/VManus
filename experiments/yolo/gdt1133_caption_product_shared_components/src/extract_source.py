#!/usr/bin/env python3
"""Reproduce only the already exposed f19r body and owned C2 caption packet."""
from pathlib import Path
import csv, gzip, hashlib, io, json, subprocess
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=ROOT/'experiments/yolo/gdt1109_fixed_units_joint_botanical_graph/artifacts/CARRIERS.json.gz'
    records=json.loads(gzip.decompress(source.read_bytes()))
    selected=[r for r in records if r['page']=='f19r']
    assert len(selected)==3 and {r['edition'] for r in selected}=={'IT2a','ZL3b','RF1b'}
    captions=ROOT/'experiments/yolo/gdt1128_native_owned_label_reading_binding/artifacts/CACHED_LABELS.tsv'
    columns='source_group_id,edition,locus,page,section,currier,hand,code,kind,grammar_scope,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw,clean_ascii_fragments,clean_ascii_fragment_count,legacy_surface_positions_1based,legacy_interlinear_row_present,legacy_mapping_status'
    q=subprocess.run([str(ROOT/'vmanus-exp'),'query-tsv','--selector','locus','--allow','f102v1.17','--columns',columns,str(captions.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True,check=True)
    rows=list(csv.DictReader(io.StringIO(q.stdout),delimiter='\t'));assert len(rows)==3
    result={'source_path':str(source.relative_to(ROOT)),'source_sha256':sha(source),'selector':'page','allow':['f19r'],'selection_after_contract':True,'readers':selected,'caption':{'locus':'f102v1.17','object':'240/C2','IT2a':{'raw':'loralody','fixed_units':['l','or','al','ody']},'ZL3b':{'raw':'loralody','fixed_units':['l','or','al','ody']},'RF1b':{'raw':'losalody','fixed_units':['l','os','al','ody']},'native_status':'conditional compatibility only','source':'experiments/yolo/gdt1128_native_owned_label_reading_binding/REPORT.md','coidentity':'Paid hypothetical source relation between object240 and f19r; not independently established botanical identity'},'caption_source_path':str(captions.relative_to(ROOT)),'caption_source_sha256':sha(captions),'caption_native_rows':rows,'caption_guard':q.stderr.strip(),'seals':['f84','f84r'],'new_access':False}
    (BASE/'src/SOURCE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'readers':len(selected),'body_groups':{r['edition']:sum(l['source_group_count'] for l in r['lines']) for r in selected},'caption_rows':len(rows),'sha256':sha(BASE/'src/SOURCE.json')}))
if __name__=='__main__':main()
