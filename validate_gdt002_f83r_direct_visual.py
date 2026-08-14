#!/usr/bin/env python3
"""Independent record, source-join, image-hash, and arithmetic validation."""
import csv,hashlib,itertools,json,subprocess,sys,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
web_cache={}
def websha(url):
 if url not in web_cache:web_cache[url]=hashlib.sha256(urllib.request.urlopen(url,timeout=60).read()).hexdigest()
 return web_cache[url]
o=read(R/'gdt002_f83r_direct_visual_observations.tsv');a={x['locus']:x for x in read(S/'existing_human_exact_locus_annotations.tsv')};f={x['locus']:x for x in read(S/'source_sta_family_consensus_loci.tsv')};r=json.loads((R/'gdt002_f83r_direct_visual_result.json').read_text());led=read(R/'GDT002_YOLO_LEDGER.tsv')
coords=True;urls=True;joins=True
for x in o:
 cw,ch=map(int,(x['canvas_width'],x['canvas_height']))
 for k in ('context_xywh','target_xywh'):
  q=list(map(int,x[k].split(',')));coords &= len(q)==4 and q[0]>=0 and q[1]>=0 and q[2]>0 and q[3]>0 and q[0]+q[2]<=cw and q[1]+q[3]<=ch
 urls &= x['full_image_url']==f"https://collections.library.yale.edu/iiif/2/1006224/full/full/0/default.jpg" and x['context_xywh'] in x['context_url'] and x['target_xywh'] in x['target_url']
 joins &= x['prior_human_tags']==a[x['locus']]['object_tags'] and x['prior_human_certainty']==a[x['locus']]['certainty'] and x['formal_family_expression']==f[x['locus']]['family_sequence'] and int(x['contains_ACA'])==int('ACA' in f[x['locus']]['family_sequence'])
network=all(websha(x[u])==x[h] for x in o for u,h in [('full_image_url','full_image_sha256'),('context_url','context_sha256'),('target_url','target_sha256')])
lower=[x for x in o if x['normalized_geometry_class'].startswith('LOWER_')];arch=[x for x in o if x['normalized_geometry_class'].startswith('ARCH_')];effect=sum(int(x['contains_ACA']) for x in lower)/2-sum(int(x['contains_ACA']) for x in arch)/2
worlds=list(set(itertools.permutations([int(x['contains_ACA']) for x in o])));tail=sum((sum(w[:2])/2-sum(w[2:])/2)>=effect-1e-12 for w in worlds)
checks={'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='yolo/gdt002-visual-grammar-constraints','loci_exact':{x['locus'] for x in o}=={'f83r.45','f83r.46','f83r.50','f83r.51'},'ai_provenance':all(x['provenance']=='AI_DIRECT_VISUAL_OBSERVATION' for x in o),'coordinates_in_bounds':coords,'official_urls':urls,'network_image_hashes':network,'source_joins':joins,'class_counts':len(lower)==len(arch)==2,'arithmetic':abs(effect-.5)<1e-12 and len(worlds)==4 and tail==2 and abs(r['comparison']['one_sided_exact_p']-.5)<1e-12,'tag_scope_correction':'must not be treated' in r['provenance_correction'],'holdout_sealed':r['holdout']=={'page':'f84r','formal_payload_opened':False,'formal_payload_joined':False,'used':False},'ledger_row':sum(x['checkpoint_id']=='GDT002_CKPT012' for x in led)==1,'input_hashes':all(sha(R/k)==v for k,v in r['inputs'].items()),'document_hashes':all(sha(R/k)==v for k,v in r['documents'].items()),'claim_ceiling':all(q in r['claim_ceiling'] for q in ('PROXIMITY_ONLY','no semantic role','translation'))}
failed=[k for k,v in checks.items() if not v];out={'artifact':'GDT002_F83R_DIRECT_VISUAL_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'result_sha256':sha(R/'gdt002_f83r_direct_visual_result.json'),'scope':'Independent source joins, exact arithmetic, coordinate bounds, official IIIF byte hashes, ledger/doc/input hashes, holdout and claim ceiling. Visual descriptions remain AI observations, not independently reproduced judgments.'}
(R/'gdt002_f83r_direct_visual_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed});sys.exit(bool(failed))
