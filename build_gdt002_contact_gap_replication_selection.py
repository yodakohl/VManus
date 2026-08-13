#!/usr/bin/env python3
import csv, hashlib, io
from pathlib import Path
R=Path(__file__).resolve().parent
spec=[]
inherited={'f100r.7':'CG8B5118853586','f100r.8':'CG8D116F0B9695','f100r.9':'CGF255D39AC5D6','f100r.10':'CG5A486DC157BB','f100r.11':'CG1BA8C54B160A','f99v.15':'CGF1A0593EF78D','f99v.17':'CG222DBE381C0D','f99v.18':'CGDB3398C41893','f99v.20':'CG47132E3DBB2B'}
for page,folio,array,loci,canvas,w,h,role in [
 ('f100r','f100','F100R_L2',[f'f100r.{i}' for i in range(6,12)],'1006248',2676,3756,'DISCOVERY'),
 ('f100v','f100','F100V_L1',[f'f100v.{i}' for i in range(1,5)],'1006249',7486,3715,'DISCOVERY'),
 ('f99v','f99','F99V_L1',[f'f99v.{i}' for i in range(2,10)],'1006247',2802,3697,'TRANSFER'),
 ('f99v','f99','F99V_L2',[f'f99v.{i}' for i in range(15,21)],'1006247',2802,3697,'TRANSFER'),
]:
 for i,locus in enumerate(loci,1):
  tid='CGR'+hashlib.sha256(('GDT002_CONTACT_GAP_COMPLETE_ARRAY_REPLICATION_V1|'+locus).encode()).hexdigest()[:12].upper()
  prior='INHERITED_FROZEN_CALL' if locus in inherited else 'NEW_CALL'
  spec.append({'target_id':tid,'inherited_from_target_id':inherited.get(locus,''),'page':page,'physical_folio':folio,'locus':locus,'array_id':array,'ordinal_in_complete_unit':i,'canvas_id':canvas,'width':w,'height':h,'official_image_url':f'https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg','panel_role':role,'call_source':prior})
out=io.StringIO(newline=''); w=csv.DictWriter(out,fieldnames=list(spec[0]),delimiter='\t',lineterminator='\n'); w.writeheader();w.writerows(spec)
(R/'gdt002_contact_gap_replication_selection.tsv').write_text(out.getvalue())
print({'rows':len(spec),'new':sum(r['call_source']=='NEW_CALL' for r in spec),'inherited':sum(r['call_source']=='INHERITED_FROZEN_CALL' for r in spec)})
