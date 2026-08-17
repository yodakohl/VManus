#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt251_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
r=list(csv.DictReader((R/'gdt251_okal_renderer_cluster.tsv').open(),delimiter='\t'));v=list(csv.DictReader((R/'gdt251_okal_variant_summary.tsv').open(),delimiter='\t'));s=list(csv.DictReader((R/'gdt251_section_confounds.tsv').open(),delimiter='\t'));c=list(csv.DictReader((R/'gdt251_counterexamples.tsv').open(),delimiter='\t'))
ck(len(r)==20);ck(len(v)==10);ck(len({x['physical_folio'] for x in r})==7);ck(all(x['token'].startswith('okal') for x in r));ck(all(x['transferred_prefix']=='AQAB' for x in r));ck(sum(x['figure_tag']=='1' for x in r)==18);ck(sum(x['figure_tag']=='1' or x['star_or_sky_tag']=='1' for x in r)==19);ck([(x['section'],int(x['all_annotated_groups']),int(x['all_figure_positive']),int(x['okal_prefix_groups']),int(x['okal_figure_positive'])) for x in s]==[('Z',178,178,14,14),('B',73,55,4,4)]);ck(len(c)==6);ck(z['active_semantic_assignments']==0);ck(z['gdt250_okaly_hypothesis_state']=='DEMOTED_LIKELY_RENDERER_AND_SECTION_CONFOUND');ck(z['status']=='OKALY_FIGURE_GLOSS_DEMOTED_AQAB_RENDERER_CLUSTER_SECTION_CONFOUNDED');ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt251_result.json')};(R/'gdt251_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')
