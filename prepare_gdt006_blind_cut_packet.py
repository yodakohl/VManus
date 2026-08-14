#!/usr/bin/env python3
"""Create an opaque crop-only packet from a source-aware GDT006 localization."""
import argparse,csv,hashlib,os,shutil
from pathlib import Path

p=argparse.ArgumentParser(); p.add_argument('localization_tsv'); p.add_argument('output_dir'); p.add_argument('--nonce-file',required=True); a=p.parse_args()
src=Path(a.localization_tsv); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True); (out/'images').mkdir(exist_ok=True)
nonce=Path(a.nonce_file).read_text().strip(); assert len(nonce)>=32
with src.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f,delimiter='\t'))
resolved=[r for r in rows if r['localization_state']=='LOCALIZED']
joined=[]
for r in resolved:
    key='|'.join(r[k] for k in ('pair_id','arm','cut_ordinal','locus','group_index','display_cut_offset'))
    blind='BC'+hashlib.sha256((nonce+'|'+key).encode()).hexdigest()[:14].upper()
    image=Path(r['marked_crop_path']); assert image.is_file()
    dst=out/'images'/f'{blind}.png'; shutil.copyfile(image,dst)
    joined.append({**r,'blind_id':blind,'delivered_image_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
joined.sort(key=lambda r:r['blind_id'])
with (out/'worklist.tsv').open('w',newline='',encoding='utf-8') as f:
    fields=['blind_id','image_path','image_sha256','marker_instruction','allowed_states']
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n'); w.writeheader()
    for r in joined:w.writerow({'blind_id':r['blind_id'],'image_path':str(Path('images')/(r['blind_id']+'.png')),'image_sha256':r['delivered_image_sha256'],'marker_instruction':'Classify manuscript geometry at red vertical marker; ignore marker overlay','allowed_states':'INK_TOUCH_OR_CROSSING|NARROW_VISIBLE_GAP|ORDINARY_VISIBLE_GAP|WIDE_VISIBLE_GAP|UNRESOLVED'})
private=out.parent/(out.name+'_private_join.tsv')
with private.open('w',newline='',encoding='utf-8') as f:
    fields=list(joined[0]) if joined else ['blind_id']; w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(joined)
print(f'resolved={len(joined)} unresolved={len(rows)-len(joined)} worklist={out/"worklist.tsv"} private_join={private}')
