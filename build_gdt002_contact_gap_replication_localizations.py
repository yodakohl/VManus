#!/usr/bin/env python3
"""Bind source-aware localizations and create source-free randomized review packets."""
import argparse,csv,hashlib,io,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parent
FULL={'1006247':('111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5',2802,3697),'1006248':('6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429',2676,3756),'1006249':('72637b9770f40f7a8ff6b96a551e64775e88994ae69bafec0b43d48974364c33',7486,3715)}
# locus: context xywh, target xywh, confidence, neutral note
NEW={
'f100r.6':('80,450,650,750','135,720,195,120','HIGH','First inscription in the source-count-matched second illustrated row.'),
'f100v.1':('850,350,850,800','1145,740,250,140','HIGH','First inscription beside a plant base in the bounded four-unit row.'),
'f100v.2':('1350,300,850,800','1705,685,225,120','HIGH','Second inscription beside a plant base in the bounded four-unit row.'),
'f100v.3':('1750,250,850,850','2040,630,225,135','HIGH','Third inscription beside a plant base in the bounded four-unit row.'),
'f100v.4':('2150,300,750,850','2350,680,230,125','HIGH','Fourth inscription beside a plant base in the bounded four-unit row.'),
'f99v.2':('350,100,500,350','490,160,230,125','HIGH','First inscription in the bounded eight-unit upper row.'),
'f99v.3':('650,100,550,400','760,160,350,150','HIGH','Second inscription unit; target box includes its drawing-interrupted components.'),
'f99v.4':('950,80,450,400','1100,145,170,130','HIGH','Third inscription in the bounded eight-unit upper row.'),
'f99v.5':('1200,150,600,500','1260,250,370,175','HIGH','Fourth inscription unit; target box includes its drawing-interrupted components.'),
'f99v.6':('1450,50,500,350','1670,110,230,125','HIGH','Fifth inscription in the bounded eight-unit upper row.'),
'f99v.7':('1700,60,500,350','1830,115,200,130','HIGH','Sixth inscription in the bounded eight-unit upper row.'),
'f99v.8':('1950,60,500,350','2070,120,190,120','HIGH','Seventh inscription in the bounded eight-unit upper row.'),
'f99v.9':('2200,50,500,400','2320,110,240,150','HIGH','Eighth inscription in the bounded eight-unit upper row.'),
'f99v.16':('800,650,700,850','1025,955,225,125','HIGH','Second inscription in the source-count-matched lower illustrated row.'),
'f99v.19':('1770,580,650,850','2070,830,225,140','HIGH','Fifth inscription in the source-count-matched lower illustrated row.'),
}
CENSUS={'F100R_L2':'EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_ANNOTATED_UNIT','F100V_L1':'EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_ANNOTATED_UNIT','F99V_L1':'EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_ANNOTATED_UNIT','F99V_L2':'EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_ANNOTATED_UNIT'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(s):return tuple(map(int,s.split(',')))
def table(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def emit(path,rs):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs);path.write_text(out.getvalue())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--packet-dir',required=True);a=ap.parse_args();d=Path(a.packet_dir);d.mkdir(parents=True,exist_ok=False)
 sel=table(R/'gdt002_contact_gap_replication_selection.tsv'); old={r['target_id']:r for r in table(R/'gdt002_contact_gap_localizations.tsv')}
 images={}
 for canvas,(digest,w,h) in FULL.items():
  p=d/f'{canvas}.jpg';urllib.request.urlretrieve(f'https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg',p)
  assert sha(p)==digest; im=Image.open(p);assert im.size==(w,h);images[canvas]=im.convert('RGB')
 rows=[]; review=[]
 for r in sel:
  if r['call_source']=='INHERITED_FROZEN_CALL':
   prior=old[r['inherited_from_target_id']]; context,target=prior['context_xywh'],prior['target_xywh'];conf=prior['localizer_confidence'];note='Inherited frozen source-aware localization; visual state is not re-reviewed.'
  else: context,target,conf,note=NEW[r['locus']]
  im=images[r['canvas_id']];cx,cy,cw,ch=xy(context);tx,ty,tw,th=xy(target)
  assert 0<=cx<cx+cw<=im.width and 0<=cy<cy+ch<=im.height and cx<=tx<tx+tw<=cx+cw and cy<=ty<ty+th<=cy+ch
  c=im.crop((cx,cy,cx+cw,cy+ch));t=im.crop((tx,ty,tx+tw,ty+th));marked=c.copy();draw=ImageDraw.Draw(marked);draw.rectangle((tx-cx,ty-cy,tx-cx+tw-1,ty-cy+th-1),outline=(255,0,255),width=5)
  blind='RV'+hashlib.sha256(('GDT002_REVIEW_PACKET_V1|'+r['target_id']).encode()).hexdigest()[:14].upper()
  cp=d/f'{blind}_context.png';tp=d/f'{blind}_target.png';mp=d/f'{blind}_marked.png';c.save(cp);t.save(tp);marked.save(mp)
  rows.append({**r,'full_image_sha256':FULL[r['canvas_id']][0],'array_census_state':CENSUS[r['array_id']],'array_census_confidence':'HIGH','context_xywh':context,'target_xywh':target,'context_png_sha256':sha(cp),'target_png_sha256':sha(tp),'marked_png_sha256':sha(mp),'localizer_confidence':conf,'localizer_note':note,'localizer_state_judgment':'CONTACT_GAP_NOT_JUDGED','blind_review_id':blind})
  if r['call_source']=='NEW_CALL':review.append({'blind_review_id':blind,'marked_file':mp.name,'target_file':tp.name})
 emit(R/'gdt002_contact_gap_replication_localizations.tsv',rows)
 review.sort(key=lambda z:z['blind_review_id']);emit(d/'review_manifest.tsv',review)
 (d/'RUBRIC.txt').write_text('CONTACT: at least one target-writing stroke visibly touches or overlaps a drawn non-writing contour.\nCLEAR_GAP: visible background separates every target-writing stroke from nearby drawn non-writing contours.\nUNCERTAIN: localization, fading, overlap, damage, or geometry prevents a secure binary call.\nJudge only the magenta-box target. Do not infer object identity, ownership, word, or meaning.\n')
 print({'localizations':len(rows),'new_review_targets':len(review),'packet_dir':str(d)})
if __name__=='__main__':main()
