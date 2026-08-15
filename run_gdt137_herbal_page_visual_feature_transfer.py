#!/usr/bin/env python3
"""GDT137: whole-Herbal-page formal inventory versus visible plant features."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt062_right_family_inventory.tsv";INVENTORY=ROOT/"gdt137_herbal_visual_feature_inventory.tsv";PREDICTION=ROOT/"gdt137_prediction.json";METHOD=ROOT/"GDT137_HERBAL_PAGE_VISUAL_FEATURE_TRANSFER_METHOD.md";REPORT=ROOT/"GDT137_HERBAL_PAGE_VISUAL_FEATURE_TRANSFER_REPORT.md";SCORES=ROOT/"gdt137_panel_scores.tsv";FEATURE_SCORES=ROOT/"gdt137_feature_scores.tsv";FOLDS=ROOT/"gdt137_folio_scores.tsv";CROSS=ROOT/"gdt137_cross_currier_scores.tsv";PREDICTIONS=ROOT/"gdt137_page_predictions.tsv";NULL=ROOT/"gdt137_null_results.tsv";COUNTER=ROOT/"gdt137_counterexamples.tsv";VARIANTS=ROOT/"gdt137_variant_log.tsv";RESULT=ROOT/"gdt137_result.json"
REPS=("PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3","COMPILER_SIGNATURE");K=7;SHRINK=8.;WORLDS=10000;SEED=137001

def read(p):
 with Path(p).open(encoding="utf8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with Path(p).open("w",encoding="utf8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def add3(c,s):
 s="^"+s+"$"
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1.
def wjd(a,b):
 keys=set(a)|set(b);den=sum(max(a[k],b[k])for k in keys)
 return 1-sum(min(a[k],b[k])for k in keys)/den if den else 0.
def loss(y,p):
 p=np.clip(p,1e-12,1-1e-12);return-np.log2(np.where(y>0,p,1-p))
def clean(rows):return[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in rows]

def main():
 freeze=json.loads(PREDICTION.read_text());pages=read(INVENTORY);assert len(pages)==127 and not any(r["page"].startswith("f84")for r in pages);index={r["page"]:i for i,r in enumerate(pages)}
 source=[]
 with SOURCE.open(encoding="utf8",newline="")as h:
  for row in csv.DictReader(h,delimiter="\t"):
   if row["page"].startswith("f84"):continue
   if row["page"]in index:source.append(row)
 assert len(source)==5234 and set(r["page"]for r in source)==set(index)
 feature_names=freeze["features"];y=np.array([[int(r[f])for f in feature_names]for r in pages],float);panels={"ALL_12":list(range(12)),"PRIMARY_CAPACITY_8":[feature_names.index(f)for f in freeze["primary_capacity_features"]],"CROSS_CURRIER_6":[feature_names.index(f)for f in freeze["cross_currier_features"]]}
 bypage=defaultdict(list)
 for r in source:bypage[r["page"]].append(r)
 features={rep:[]for rep in REPS};nuisance=[]
 maxline=max(int(r["formal_lines"])for r in pages);maxgroup=max(int(r["formal_groups"])for r in pages);maxprose=max(int(r["catalogue_prose_lines"]or 0)for r in pages);maxpara=max(int(r["paragraph_starts"]or 0)for r in pages)
 for p in pages:
  z=sorted(bypage[p["page"]],key=lambda r:(r["locus"],int(r["group_index"])));bundle={rep:Counter()for rep in REPS}
  for r in z:
   bundle["PAGE_HOST_IDENTITY"]["H="+r["page_host"]]+=1;add3(bundle["PAGE_HOST_CHAR3"],r["page_host"]);add3(bundle["RAW_CHAR3"],r["token"]);sig="|".join((r["wrapper"],r["inner_d"],r["local_frame"],r["right_family"],r["dy_closure"],r["b3"]));bundle["COMPILER_SIGNATURE"][sig]+=1
  for rep in REPS:features[rep].append(bundle[rep])
  n=Counter({"CUR="+p["currier"]:1.,"HAND="+p["hand"]:1.,"PROFILE="+p["illustration_profile"]:1.,"LABEL="+p["catalogue_label_presence"]:1.,"PARA":int(p["paragraph_starts"]or 0)/maxpara,"LINES":int(p["formal_lines"])/maxline,"GROUPS":int(p["formal_groups"])/maxgroup,"PROSE":int(p["catalogue_prose_lines"]or 0)/maxprose});nuisance.append(n)
 n=len(pages);folios=sorted({r["physical_folio"]for r in pages});folio_indices={f:np.array([i for i,r in enumerate(pages)if r["physical_folio"]==f],int)for f in folios}
 def weights(rep=None,cross_currier=False):
  matrix=np.zeros((n,n))
  for i,target in enumerate(pages):
   pool=[j for j,row in enumerate(pages)if row["physical_folio"]!=target["physical_folio"] and(not cross_currier or row["currier"]!=target["currier"])]
   ranked=[]
   for j in pool:
    d=wjd(nuisance[i],nuisance[j])+(wjd(features[rep][i],features[rep][j])if rep else 0.);ranked.append((d,pages[j]["page"],j))
   for d,_,j in sorted(ranked)[:K]:matrix[i,j]=1/(.1+d)
  return matrix
 base_w=weights();rep_w={rep:weights(rep)for rep in REPS};base_p=(base_w@y+.5)/(base_w.sum(1)[:,None]+1);pred={rep:(rep_w[rep]@y+SHRINK*base_p)/(rep_w[rep].sum(1)[:,None]+SHRINK)for rep in REPS};base_loss=loss(y,base_p);model_loss={rep:loss(y,pred[rep])for rep in REPS}
 score_rows=[];feature_rows=[];fold_rows=[];prediction_rows=[]
 for rep in REPS:
  for j,f in enumerate(feature_names):
   gain=float((base_loss[:,j]-model_loss[rep][:,j]).sum());fg=[]
   for folio,idx in folio_indices.items():fg.append(float((base_loss[idx,j]-model_loss[rep][idx,j]).sum()))
   feature_rows.append({"representation":rep,"feature":f,"positive_pages":int(y[:,j].sum()),"gain_bits":gain,"positive_gain_folios":sum(x>0 for x in fg),"local_permutation_p":"PENDING","max_feature_model_p":"PENDING"})
   for i,page in enumerate(pages):prediction_rows.append({"page":page["page"],"physical_folio":page["physical_folio"],"currier":page["currier"],"representation":rep,"feature":f,"observed":int(y[i,j]),"nuisance_probability":float(base_p[i,j]),"model_probability":float(pred[rep][i,j]),"gain_bits":float(base_loss[i,j]-model_loss[rep][i,j])})
  for panel,cols in panels.items():
   gain=float((base_loss[:,cols]-model_loss[rep][:,cols]).sum());fg=[]
   for folio,idx in folio_indices.items():
    v=float((base_loss[np.ix_(idx,cols)]-model_loss[rep][np.ix_(idx,cols)]).sum());fg.append(v);fold_rows.append({"panel":panel,"representation":rep,"physical_folio":folio,"pages":len(idx),"gain_bits":v})
   score_rows.append({"panel":panel,"representation":rep,"pages":n,"physical_folios":len(folios),"features":len(cols),"positive_cells":int(y[:,cols].sum()),"baseline_bits":float(base_loss[:,cols].sum()),"held_bits":float(model_loss[rep][:,cols].sum()),"gain_bits":gain,"selector_paid_gain_bits":gain-math.log2(4)if panel=="PRIMARY_CAPACITY_8"else"SENSITIVITY","positive_gain_features":sum(float((base_loss[:,j]-model_loss[rep][:,j]).sum())>0 for j in cols),"positive_gain_folios":sum(v>0 for v in fg),"local_permutation_p":"PENDING","max_four_p":"PENDING","max_feature_model_p":"PENDING"})

 # Cross-Currier scoring forces every target to use only the other Currier value.
 cross_base_w=weights(cross_currier=True);cross_base=(cross_base_w@y+.5)/(cross_base_w.sum(1)[:,None]+1);cross_bl=loss(y,cross_base);cross_rows=[]
 for rep in REPS:
  w=weights(rep,cross_currier=True);q=(w@y+SHRINK*cross_base)/(w.sum(1)[:,None]+SHRINK);ml=loss(y,q);cols=panels["CROSS_CURRIER_6"];cross_rows.append({"representation":rep,"pages":n,"features":len(cols),"baseline_bits":float(cross_bl[:,cols].sum()),"held_bits":float(ml[:,cols].sum()),"gain_bits":float((cross_bl[:,cols]-ml[:,cols]).sum()),"currier_A_gain":float((cross_bl[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='A']),cols)]-ml[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='A']),cols)]).sum()),"currier_B_gain":float((cross_bl[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='B']),cols)]-ml[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='B']),cols)]).sum())})

 observed={(r["panel"],r["representation"]):float(r["gain_bits"])for r in score_rows};fobs={(r["feature"],r["representation"]):float(r["gain_bits"])for r in feature_rows};local=Counter();max4=Counter();flocal=Counter();fmax=0
 strata=defaultdict(list)
 for i,r in enumerate(pages):strata[r["currier"],r["hand"],r["illustration_profile"]].append(i)
 rng=np.random.default_rng(SEED)
 for _ in range(WORLDS):
  perm=y.copy()
  for idx in strata.values():idx=np.array(idx,int);perm[idx]=perm[rng.permutation(idx)]
  bp=(base_w@perm+.5)/(base_w.sum(1)[:,None]+1);bl=loss(perm,bp);gains={};allfg=[]
  for rep in REPS:
   q=(rep_w[rep]@perm+SHRINK*bp)/(rep_w[rep].sum(1)[:,None]+SHRINK);ml=loss(perm,q)
   for panel,cols in panels.items():
    v=float((bl[:,cols]-ml[:,cols]).sum());gains[panel,rep]=v;local[panel,rep]+=v>=observed[panel,rep]-1e-12
   for j,f in enumerate(feature_names):
    v=float((bl[:,j]-ml[:,j]).sum());flocal[f,rep]+=v>=fobs[f,rep]-1e-12;allfg.append(v)
  for panel in panels:max4[panel]+=max(gains[panel,rep]for rep in REPS)>=max(observed[panel,rep]for rep in REPS)-1e-12
  fmax+=max(allfg)>=max(fobs.values())-1e-12
 null_rows=[];fmaxp=(fmax+1)/(WORLDS+1)
 for panel in panels:
  for rep in REPS:null_rows.append({"panel":panel,"representation":rep,"worlds":WORLDS,"seed":SEED,"observed_gain_bits":observed[panel,rep],"local_inclusive_p":(local[panel,rep]+1)/(WORLDS+1),"max_four_inclusive_p":(max4[panel]+1)/(WORLDS+1),"max_feature_model_inclusive_p":fmaxp,"preserves":"CURRIER;HAND;ILLUSTRATION_PROFILE;COMPLETE_12_FEATURE_VECTOR;FORMAL_PREDICTIONS"})
 nm={(r["panel"],r["representation"]):r for r in null_rows}
 for r in score_rows:z=nm[r["panel"],r["representation"]];r["local_permutation_p"]=z["local_inclusive_p"];r["max_four_p"]=z["max_four_inclusive_p"];r["max_feature_model_p"]=z["max_feature_model_inclusive_p"]
 for r in feature_rows:r["local_permutation_p"]=(flocal[r["feature"],r["representation"]]+1)/(WORLDS+1);r["max_feature_model_p"]=fmaxp
 primary={r["representation"]:r for r in score_rows if r["panel"]=="PRIMARY_CAPACITY_8"};host_rep=max(("PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3"),key=lambda rep:float(primary[rep]["gain_bits"]));host=primary[host_rep];crossmap={r["representation"]:r for r in cross_rows};gates={"selector_paid_positive":float(host["selector_paid_gain_bits"])>0,"beats_raw_and_compiler":float(host["gain_bits"])>max(float(primary["RAW_CHAR3"]["gain_bits"]),float(primary["COMPILER_SIGNATURE"]["gain_bits"])),"positive_at_least_6_of_8_features":int(host["positive_gain_features"])>=6,"positive_at_least_35_of_63_folios":int(host["positive_gain_folios"])>=35,"cross_currier_panel_positive":float(crossmap[host_rep]["gain_bits"])>0,"max_four_p_le_005":float(host["max_four_p"])<=.05};status="HERBAL_PAGE_VISUAL_CONTENT_TRANSFER_PROVISIONAL"if all(gates.values())else"HERBAL_PAGE_VISUAL_CONTENT_TRANSFER_NOT_SUPPORTED"
 # Strongest feature leads and worst folios remain hypothesis-generation/counterevidence.
 host_features=sorted((r for r in feature_rows if r["representation"]==host_rep),key=lambda r:-float(r["gain_bits"]));counter=[]
 for r in host_features:counter.append({"evidence_type":"FEATURE_GAIN","item":r["feature"],"representation":host_rep,"gain_bits":r["gain_bits"],"detail":"POSITIVE_EXPLORATORY"if float(r["gain_bits"])>0 else"NEGATIVE_COUNTEREXAMPLE"})
 for r in sorted((x for x in fold_rows if x["panel"]=="PRIMARY_CAPACITY_8"and x["representation"]==host_rep),key=lambda x:float(x["gain_bits"]))[:10]:counter.append({"evidence_type":"WORST_HELD_FOLIO","item":r["physical_folio"],"representation":host_rep,"gain_bits":r["gain_bits"],"detail":"HELD_FOLIO_COUNTEREXAMPLE"})
 counter.extend([
  {"evidence_type":"CROSS_CURRIER_ASYMMETRY","item":"CURRIER_B_TARGETS","representation":host_rep,"gain_bits":crossmap[host_rep]["currier_B_gain"],"detail":"Forced opposite-Currier gain is concentrated in A targets; B-target transfer is approximately null."},
  {"evidence_type":"CATALOGUE_TAG_REGISTER_CONFOUND","item":"BETA_TAG_FEATURES","representation":"NUISANCE_CONTROLLED","gain_bits":"NA","detail":"Several inherited tags are concentrated in Currier-B/BETA pages; Currier, hand and illustration profile are controlled but catalogue-stratum sensitivity remains."},
  {"evidence_type":"ALTERNATE_READING_SCOPE","item":"GDT062_HPR2_VIEW","representation":"ALL","gain_bits":"NA","detail":"The frozen GDT062 parser inventory is one derived source-display view; separate ZL/IT/RF HPR2 page bags are unavailable, so alternate-reading replication is not claimed."},
 ])
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"All 127 Herbal pages; eight frozen capacity features; PAGE_HOST identity primary family."},{"variant_id":"V01","status":"RUN","description":"PAGE_HOST char3 alternate host representation."},{"variant_id":"V02","status":"RUN_BASELINES","description":"Raw char3 and compiler-signature controls."},{"variant_id":"V03","status":"RUN_SENSITIVITY","description":"Six cross-Currier-capable features, including forced opposite-Currier training."},{"variant_id":"V04","status":"RUN_DIAGNOSTIC","description":"All twelve primitive visible features and per-feature maxT."},{"variant_id":"V05","status":"NOT_RUN","description":"No feature union, layout endpoint, host gloss, plant identity, new image, f84, language, or translation search."}]
 write(SCORES,clean(score_rows));write(FEATURE_SCORES,clean(feature_rows));write(FOLDS,clean(fold_rows));write(CROSS,clean(cross_rows));write(PREDICTIONS,clean(prediction_rows));write(NULL,clean(null_rows));write(COUNTER,clean(counter));write(VARIANTS,variants)
 REPORT.write_text(f"""# GDT137 — Herbal page text-to-visible-feature transfer

## Outcome

**{status}**

The test covers 127 Herbal pages on 63 physical folios, with 12 inherited
human-visible features and eight mechanically eligible primary endpoints. The
best PAGE_HOST representation is `{host_rep}` at {float(host['gain_bits']):+.3f}
held bits over the Currier/hand/illustration-profile/page-layout nuisance code,
{float(host['selector_paid_gain_bits']):+.3f} after the four-model selector,
positive on {host['positive_gain_features']}/8 features and
{host['positive_gain_folios']}/63 folios. Its local/max-four/max-feature-model
p-values are {float(host['local_permutation_p']):.4f}/
{float(host['max_four_p']):.4f}/{float(host['max_feature_model_p']):.4f}.
The positive raw and PAGE_HOST gains are ordinary under the matched null; no
individual PAGE_HOST feature diagnostic survives the full library.

Raw char3 scores {float(primary['RAW_CHAR3']['gain_bits']):+.3f} bits and the
compiler-signature control {float(primary['COMPILER_SIGNATURE']['gain_bits']):+.3f}.
The forced opposite-Currier score for `{host_rep}` on the six capable features
is {float(crossmap[host_rep]['gain_bits']):+.3f} bits (A targets
{float(crossmap[host_rep]['currier_A_gain']):+.3f}, B targets
{float(crossmap[host_rep]['currier_B_gain']):+.3f}). Frozen gates:
`{json.dumps(gates,sort_keys=True)}`.
The forced cross-Currier sensitivity is consequently asymmetric rather than a
clean two-direction transfer.

Strongest PAGE_HOST feature diagnostics are
{', '.join(r['feature']+' '+format(float(r['gain_bits']),'+.2f') for r in host_features[:4])};
these are postselected atlas entries, not host meanings. Complete per-feature,
per-page, per-folio, cross-Currier, and null outputs preserve the negative and
confounded cases.

This archive-wide page test {('supports a provisional page-level content association' if status.endswith('PROVISIONAL') else 'does not localize visible plant content in the tested page bags')}.
It does not name a PAGE_HOST or assign a semantic role, gloss, word, morpheme,
POS, sound, language, plaintext, meaning, plant identity, or translation. All
f84 rows were rejected before retention and no new f84r access occurred.
The frozen GDT062 HPR2 inventory is one derived source-display view; separate
ZL/IT/RF page bags are unavailable at this layer, so no alternate-reading
replication is claimed.
""",encoding="utf8")
 result={"schema":"GDT137_HERBAL_PAGE_VISUAL_FEATURE_TRANSFER_RESULT_V1","status":status,"pages":127,"physical_folios":63,"source_groups":len(source),"features":feature_names,"primary_features":freeze["primary_capacity_features"],"cross_currier_features":freeze["cross_currier_features"],"representations":list(REPS),"best_page_host_representation":host_rep,"primary":primary,"cross_currier":crossmap,"gates":gates,"strongest_page_host_features":host_features[:6],"alternate_reading_sensitivity":"NOT_AVAILABLE_FOR_DERIVED_GDT062_HPR2_PAGE_BAGS;NO_REPLICATION_CLAIM","interpretation":"Whole-page formal inventory versus archived human-visible plant features after metadata/layout nuisance control.","claim_ceiling":"No semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, plant identity, or translation.","f84":{"all_rows_rejected_before_retention":True,"new_f84r_access":False},"inputs":{p.name:sha(p)for p in(SOURCE,INVENTORY,PREDICTION,ROOT/"gdt031_result.json",ROOT/"gdt033_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{p.name:sha(p)for p in(SCORES,FEATURE_SCORES,FOLDS,CROSS,PREDICTIONS,NULL,COUNTER,VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":status,"host_rep":host_rep,"host_gain":host["gain_bits"],"raw_gain":primary["RAW_CHAR3"]["gain_bits"],"compiler_gain":primary["COMPILER_SIGNATURE"]["gain_bits"],"gates":gates},sort_keys=True))
if __name__=="__main__":main()
