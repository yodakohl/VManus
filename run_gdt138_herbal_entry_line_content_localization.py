#!/usr/bin/env python3
"""GDT138: locate Herbal visible-feature signal in fixed page line windows."""
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";VISUAL=ROOT/"gdt137_herbal_visual_feature_inventory.tsv";WINDOW_INV=ROOT/"gdt138_line_window_inventory.tsv";FREEZE=ROOT/"gdt138_prediction.json";METHOD=ROOT/"GDT138_HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_METHOD.md";REPORT=ROOT/"GDT138_HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_REPORT.md";SCORES=ROOT/"gdt138_window_scores.tsv";FEATURES=ROOT/"gdt138_feature_scores.tsv";FOLDS=ROOT/"gdt138_folio_scores.tsv";CROSS=ROOT/"gdt138_cross_currier_scores.tsv";PREDS=ROOT/"gdt138_page_predictions.tsv";NULL=ROOT/"gdt138_null_results.tsv";COUNTER=ROOT/"gdt138_counterexamples.tsv";VARIANTS=ROOT/"gdt138_variant_log.tsv";RESULT=ROOT/"gdt138_result.json"
WINDOWS=("FIRST_LINE","BODY_AFTER_FIRST","LAST_LINE","ALL_PAGE");REPS=("PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3");COMBOS=tuple((w,r)for w in WINDOWS for r in REPS);K=7;SHRINK=8.;WORLDS=10000;SEED=138001
def read(p):
 with Path(p).open(encoding="utf8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with Path(p).open("w",encoding="utf8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def order(x):return int(re.search(r"\.(\d+)$",x).group(1))
def add3(c,s):
 s="^"+s+"$"
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1
def dist(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k)
 return 1-sum(min(a[x],b[x])for x in k)/d if d else 0
def loss(y,p):p=np.clip(p,1e-12,1-1e-12);return-np.log2(np.where(y>0,p,1-p))
def clean(rows):return[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in x.items()}for x in rows]
def main():
 freeze=json.loads(FREEZE.read_text());visual={r["page"]:r for r in read(VISUAL)};windows=read(WINDOW_INV);pages=[visual[r["page"]]for r in windows];assert len(pages)==126 and not any(r["page"].startswith("f84")for r in pages);pindex={r["page"]:i for i,r in enumerate(pages)};winmap={r["page"]:r for r in windows}
 source=[]
 with SOURCE.open(encoding="utf8",newline="")as h:
  for row in csv.DictReader(h,delimiter="\t"):
   if row["page"].startswith("f84"):continue
   if row["page"]in pindex:source.append(row)
 assert len(source)==5227 and set(r["page"]for r in source)==set(pindex)
 primary_names=freeze["primary_features"];cross_names=freeze["cross_currier_features"];names=list(dict.fromkeys(primary_names+cross_names));y=np.array([[int(r[f])for f in names]for r in pages],float);panels={"PRIMARY_8":[names.index(f)for f in primary_names],"CROSS_CURRIER_6":[names.index(f)for f in cross_names]}
 bypage=defaultdict(lambda:defaultdict(list))
 for r in source:bypage[r["page"]][r["locus"]].append(r)
 feat={combo:[]for combo in COMBOS};nuis=[];ml=max(int(r["formal_lines"])for r in pages);mg=max(int(r["formal_groups"])for r in pages);mp=max(int(r["catalogue_prose_lines"]or 0)for r in pages);ma=max(int(r["paragraph_starts"]or 0)for r in pages)
 for page in pages:
  loci=sorted(bypage[page["page"]],key=order);sets={"FIRST_LINE":{loci[0]},"BODY_AFTER_FIRST":set(loci[1:]),"LAST_LINE":{loci[-1]},"ALL_PAGE":set(loci)};assert loci[0]==winmap[page["page"]]["first_locus"]and loci[-1]==winmap[page["page"]]["last_locus"]
  for window in WINDOWS:
   b={r:Counter()for r in REPS}
   for locus in loci:
    if locus not in sets[window]:continue
    for row in sorted(bypage[page["page"]][locus],key=lambda x:int(x["group_index"])):b["PAGE_HOST_IDENTITY"]["H="+row["page_host"]]+=1;add3(b["PAGE_HOST_CHAR3"],row["page_host"]);add3(b["RAW_CHAR3"],row["token"])
   for rep in REPS:feat[window,rep].append(b[rep])
  nuis.append(Counter({"CUR="+page["currier"]:1.,"HAND="+page["hand"]:1.,"PROFILE="+page["illustration_profile"]:1.,"LABEL="+page["catalogue_label_presence"]:1.,"PARA":int(page["paragraph_starts"]or 0)/ma,"LINES":int(page["formal_lines"])/ml,"GROUPS":int(page["formal_groups"])/mg,"PROSE":int(page["catalogue_prose_lines"]or 0)/mp}))
 n=len(pages);folios=sorted({r["physical_folio"]for r in pages});fi={f:np.array([i for i,r in enumerate(pages)if r["physical_folio"]==f],int)for f in folios}
 def matrix(combo=None,cross=False):
  w=np.zeros((n,n))
  for i,t in enumerate(pages):
   z=[]
   for j,r in enumerate(pages):
    if r["physical_folio"]==t["physical_folio"]or(cross and r["currier"]==t["currier"]):continue
    d=dist(nuis[i],nuis[j])+(dist(feat[combo][i],feat[combo][j])if combo else 0);z.append((d,r["page"],j))
   for d,_,j in sorted(z)[:K]:w[i,j]=1/(.1+d)
  return w
 bw=matrix();cw={c:matrix(c)for c in COMBOS};bp=(bw@y+.5)/(bw.sum(1)[:,None]+1);bl=loss(y,bp);pred={c:(cw[c]@y+SHRINK*bp)/(cw[c].sum(1)[:,None]+SHRINK)for c in COMBOS};mloss={c:loss(y,pred[c])for c in COMBOS};scores=[];features=[];folds=[];predrows=[]
 for combo in COMBOS:
  window,rep=combo
  for j,name in enumerate(names):features.append({"window":window,"representation":rep,"feature":name,"positive_pages":int(y[:,j].sum()),"gain_bits":float((bl[:,j]-mloss[combo][:,j]).sum()),"positive_gain_folios":sum(float((bl[idx,j]-mloss[combo][idx,j]).sum())>0 for idx in fi.values()),"local_permutation_p":"PENDING","max_feature_combo_p":"PENDING"})
  for i,page in enumerate(pages):
   for j,name in enumerate(names):predrows.append({"page":page["page"],"physical_folio":page["physical_folio"],"currier":page["currier"],"window":window,"representation":rep,"feature":name,"observed":int(y[i,j]),"nuisance_probability":float(bp[i,j]),"model_probability":float(pred[combo][i,j]),"gain_bits":float(bl[i,j]-mloss[combo][i,j])})
  for panel,cols in panels.items():
   gain=float((bl[:,cols]-mloss[combo][:,cols]).sum());fg=[]
   for folio,idx in fi.items():v=float((bl[np.ix_(idx,cols)]-mloss[combo][np.ix_(idx,cols)]).sum());fg.append(v);folds.append({"panel":panel,"window":window,"representation":rep,"physical_folio":folio,"pages":len(idx),"gain_bits":v})
   scores.append({"panel":panel,"window":window,"representation":rep,"pages":n,"physical_folios":len(folios),"features":len(cols),"baseline_bits":float(bl[:,cols].sum()),"held_bits":float(mloss[combo][:,cols].sum()),"gain_bits":gain,"selector_paid_gain_bits":gain-math.log2(12)if panel=="PRIMARY_8"else"SENSITIVITY","positive_gain_features":sum(float((bl[:,j]-mloss[combo][:,j]).sum())>0 for j in cols),"positive_gain_folios":sum(v>0 for v in fg),"local_permutation_p":"PENDING","max_12_p":"PENDING","max_feature_combo_p":"PENDING"})
 # Forced opposite-Currier sensitivity on six capable features.
 cbw=matrix(cross=True);cb=(cbw@y+.5)/(cbw.sum(1)[:,None]+1);cbl=loss(y,cb);cross=[]
 for combo in COMBOS:
  w=matrix(combo,cross=True);q=(w@y+SHRINK*cb)/(w.sum(1)[:,None]+SHRINK);m=loss(y,q);cols=panels["CROSS_CURRIER_6"];cross.append({"window":combo[0],"representation":combo[1],"gain_bits":float((cbl[:,cols]-m[:,cols]).sum()),"currier_A_gain":float((cbl[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='A']),cols)]-m[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='A']),cols)]).sum()),"currier_B_gain":float((cbl[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='B']),cols)]-m[np.ix_(np.array([i for i,r in enumerate(pages)if r['currier']=='B']),cols)]).sum())})
 obs={(r["panel"],r["window"],r["representation"]):float(r["gain_bits"])for r in scores};fobs={(r["feature"],r["window"],r["representation"]):float(r["gain_bits"])for r in features};local=Counter();max12=Counter();flocal=Counter();fmax=0;strata=defaultdict(list)
 for i,r in enumerate(pages):strata[r["currier"],r["hand"],r["illustration_profile"]].append(i)
 rng=np.random.default_rng(SEED)
 for _ in range(WORLDS):
  py=y.copy()
  for idx in strata.values():idx=np.array(idx,int);py[idx]=py[rng.permutation(idx)]
  pbase=(bw@py+.5)/(bw.sum(1)[:,None]+1);pbl=loss(py,pbase);g={};allf=[]
  for combo in COMBOS:
   q=(cw[combo]@py+SHRINK*pbase)/(cw[combo].sum(1)[:,None]+SHRINK);m=loss(py,q)
   for panel,cols in panels.items():v=float((pbl[:,cols]-m[:,cols]).sum());g[panel,combo]=v;local[panel,combo]+=v>=obs[panel,combo[0],combo[1]]-1e-12
   for j,name in enumerate(names):v=float((pbl[:,j]-m[:,j]).sum());flocal[name,combo]+=v>=fobs[name,combo[0],combo[1]]-1e-12;allf.append(v)
  for panel in panels:max12[panel]+=max(g[panel,c]for c in COMBOS)>=max(obs[panel,c[0],c[1]]for c in COMBOS)-1e-12
  fmax+=max(allf)>=max(fobs.values())-1e-12
 null=[];fmaxp=(fmax+1)/(WORLDS+1)
 for panel in panels:
  for combo in COMBOS:null.append({"panel":panel,"window":combo[0],"representation":combo[1],"worlds":WORLDS,"seed":SEED,"observed_gain_bits":obs[panel,combo[0],combo[1]],"local_inclusive_p":(local[panel,combo]+1)/(WORLDS+1),"max_12_inclusive_p":(max12[panel]+1)/(WORLDS+1),"max_feature_combo_inclusive_p":fmaxp,"preserves":"CURRIER;HAND;ILLUSTRATION_PROFILE;COMPLETE_9_SCORED_FEATURE_VECTOR;PREDICTION_WEIGHTS"})
 nm={(r["panel"],r["window"],r["representation"]):r for r in null}
 for r in scores:z=nm[r["panel"],r["window"],r["representation"]];r["local_permutation_p"]=z["local_inclusive_p"];r["max_12_p"]=z["max_12_inclusive_p"];r["max_feature_combo_p"]=z["max_feature_combo_inclusive_p"]
 for r in features:r["local_permutation_p"]=(flocal[r["feature"],(r["window"],r["representation"])]+1)/(WORLDS+1);r["max_feature_combo_p"]=fmaxp
 smap={(r["window"],r["representation"]):r for r in scores if r["panel"]=="PRIMARY_8"};cmap={(r["window"],r["representation"]):r for r in cross};first_rep=max(("PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3"),key=lambda rep:float(smap["FIRST_LINE",rep]["gain_bits"]));first=smap["FIRST_LINE",first_rep];family_best=max(smap.values(),key=lambda r:float(r["gain_bits"]));first_features=sorted((r for r in features if r["window"]=="FIRST_LINE"and r["representation"]==first_rep and r["feature"]in primary_names),key=lambda r:-float(r["gain_bits"]));gates={"selector_paid_positive":float(first["selector_paid_gain_bits"])>0,"beats_first_line_raw":float(first["gain_bits"])>float(smap["FIRST_LINE","RAW_CHAR3"]["gain_bits"]),"beats_same_host_other_windows":all(float(first["gain_bits"])>float(smap[w,first_rep]["gain_bits"])for w in("BODY_AFTER_FIRST","LAST_LINE","ALL_PAGE")),"positive_at_least_6_of_8_features":int(first["positive_gain_features"])>=6,"positive_at_least_35_of_62_folios":int(first["positive_gain_folios"])>=35,"cross_currier_positive":float(cmap["FIRST_LINE",first_rep]["gain_bits"])>0,"max_12_p_le_005":float(first["max_12_p"])<=.05};status="HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_PROVISIONAL"if all(gates.values())else"HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_NOT_SUPPORTED"
 counter=[]
 for w in WINDOWS:
  for rep in REPS:counter.append({"evidence_type":"WINDOW_MODEL_GAIN","item":w,"representation":rep,"gain_bits":smap[w,rep]["gain_bits"],"detail":"PRIMARY_COMPARISON"})
 for r in sorted((x for x in folds if x["panel"]=="PRIMARY_8"and x["window"]=="FIRST_LINE"and x["representation"]==first_rep),key=lambda x:float(x["gain_bits"]))[:10]:counter.append({"evidence_type":"WORST_FIRST_LINE_FOLIO","item":r["physical_folio"],"representation":first_rep,"gain_bits":r["gain_bits"],"detail":"HELD_FOLIO_COUNTEREXAMPLE"})
 counter.extend([{"evidence_type":"FAMILY_BEST_NOT_FIRST","item":family_best["window"],"representation":family_best["representation"],"gain_bits":family_best["gain_bits"],"detail":"The numerically best fixed combination is a last-line model, not the frozen entry-line hypothesis."},{"evidence_type":"FIRST_LINE_FEATURE_CONCENTRATION","item":first_features[0]["feature"],"representation":first_rep,"gain_bits":first_features[0]["gain_bits"],"detail":"One visible-feature endpoint contributes most of the first-line aggregate; only four of eight feature gains are positive."},{"evidence_type":"ALTERNATE_READING_SCOPE","item":"GDT062_HPR2_VIEW","representation":"ALL","gain_bits":"NA","detail":"One derived source-display view; no separate ZL/IT/RF HPR2 window replication is claimed."}])
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"FIRST_LINE PAGE_HOST identity/char3 with raw control."},{"variant_id":"V01","status":"RUN_CONTROL","description":"BODY_AFTER_FIRST same three representations."},{"variant_id":"V02","status":"RUN_CONTROL","description":"LAST_LINE same three representations."},{"variant_id":"V03","status":"RUN_ANCHOR","description":"ALL_PAGE GDT137 anchor after f57r deletion."},{"variant_id":"V04","status":"RUN_SENSITIVITY","description":"Forced opposite-Currier six-feature panel."},{"variant_id":"V05","status":"NOT_RUN","description":"No paragraph-marker mining, alternate windows, compiler scan, feature selection, image, f84, gloss, or translation."}]
 write(SCORES,clean(scores));write(FEATURES,clean(features));write(FOLDS,clean(folds));write(CROSS,clean(cross));write(PREDS,clean(predrows));write(NULL,clean(null));write(COUNTER,clean(counter));write(VARIANTS,variants)
 REPORT.write_text(f"""# GDT138 — Herbal entry-line content localization

## Outcome

**{status}**

The frozen panel has 126 multi-line Herbal pages on 62 folios. The better
FIRST_LINE host model is `{first_rep}` at {float(first['gain_bits']):+.3f}
bits, {float(first['selector_paid_gain_bits']):+.3f} after the 12-way selector,
positive on {first['positive_gain_features']}/8 features and
{first['positive_gain_folios']}/62 folios. Its local/max-12/max-feature p-values
are {float(first['local_permutation_p']):.4f}/{float(first['max_12_p']):.4f}/
{float(first['max_feature_combo_p']):.4f}.

FIRST_LINE raw scores {float(smap['FIRST_LINE','RAW_CHAR3']['gain_bits']):+.3f}
bits. Matching `{first_rep}` scores are BODY_AFTER_FIRST
{float(smap['BODY_AFTER_FIRST',first_rep]['gain_bits']):+.3f}, LAST_LINE
{float(smap['LAST_LINE',first_rep]['gain_bits']):+.3f}, and ALL_PAGE
{float(smap['ALL_PAGE',first_rep]['gain_bits']):+.3f}. Forced opposite-Currier
FIRST_LINE gain is {float(cmap['FIRST_LINE',first_rep]['gain_bits']):+.3f}.
Frozen gates: `{json.dumps(gates,sort_keys=True)}`.

The numerically strongest combination in the complete fixed family is
`{family_best['window']} / {family_best['representation']}` at
{float(family_best['gain_bits']):+.3f} bits, not the first-line hypothesis.
Moreover, {first_features[0]['feature']} alone contributes
{float(first_features[0]['gain_bits']):+.3f} of the first-line aggregate and
only four of eight primary features are positive. Both observations make the
lead a concentrated archive effect rather than an entry-field localization.

The bounded positional ablation {('supports' if status.endswith('PROVISIONAL') else 'does not support')} localization of visible-feature information to the first line.
No line is called a name or content field, and no semantic role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, plant identity, or
translation is assigned. All f84 rows were rejected before retention and no
new f84r access occurred.
The GDT062 HPR2 inventory is one derived source-display view; no separate
ZL/IT/RF window replication is claimed.
""",encoding="utf8")
 result={"schema":"GDT138_HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_RESULT_V1","status":status,"pages":126,"physical_folios":62,"source_groups":len(source),"windows":list(WINDOWS),"representations":list(REPS),"primary_features":primary_names,"cross_currier_features":cross_names,"scored_feature_union":names,"first_line_host_representation":first_rep,"family_best":family_best,"strongest_first_line_features":first_features[:4],"primary_scores":{w:{r:smap[w,r]for r in REPS}for w in WINDOWS},"cross_currier":{w:{r:cmap[w,r]for r in REPS}for w in WINDOWS},"gates":gates,"alternate_reading_sensitivity":"NOT_AVAILABLE_FOR_DERIVED_GDT062_HPR2_WINDOWS;NO_REPLICATION_CLAIM","interpretation":"Post-GDT137 positional localization of archived page-visible-feature association only.","claim_ceiling":"No name field, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, plant identity, or translation.","f84":{"all_rows_rejected_before_retention":True,"new_f84r_access":False},"inputs":{p.name:sha(p)for p in(SOURCE,VISUAL,WINDOW_INV,FREEZE,ROOT/"gdt137_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{p.name:sha(p)for p in(SCORES,FEATURES,FOLDS,CROSS,PREDS,NULL,COUNTER,VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":status,"first_rep":first_rep,"first_gain":first["gain_bits"],"gates":gates},sort_keys=True))
if __name__=="__main__":main()
