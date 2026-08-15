#!/usr/bin/env python3
"""GDT104: exact decomposition of GDT103 active-only axis scores."""
import csv,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt103_external_layer_scores.tsv";METHOD=ROOT/"GDT104_HPR2_TWO_CHANNEL_DECOMPOSITION_METHOD.md";REPORT=ROOT/"GDT104_HPR2_TWO_CHANNEL_DECOMPOSITION_REPORT.md";AXOUT=ROOT/"gdt104_axis_contributions.tsv";CHANNEL=ROOT/"gdt104_channel_decomposition.tsv";NULL=ROOT/"gdt104_partition_null.tsv";PRED=ROOT/"gdt104_frozen_predictions.tsv";RESULT=ROOT/"gdt104_result.json"
OBJECT=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS");REL=("REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP");LAYERS=("PAGE_HOST_CHAR3","HOST_PLUS_WRAPPER","HOST_PLUS_FRAME","HOST_PLUS_RIGHT","HOST_PLUS_DY","HOST_PLUS_B3")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 src=[x for x in read(SOURCE) if x["encoding"]=="ACTIVE_ONLY"];assert len(src)==72;p={(x["external_axis"],x["representation"]):x for x in src};axes=OBJECT+REL;axis_rows=[]
 for axis in axes:
  for layer in LAYERS:
   x=p[axis,layer];value=float(x["gain_vs_nuisance_bits"] if layer=="PAGE_HOST_CHAR3" else x["increment_vs_page_host_bits"]);axis_rows.append({"axis_class":"OBJECT_AXIS" if axis in OBJECT else "RELATION_AXIS","external_axis":axis,"layer":layer,"contribution_definition":"GAIN_VS_NUISANCE" if layer=="PAGE_HOST_CHAR3" else "INCREMENT_VS_PAGE_HOST","contribution_bits":value,"semantic_role":"UNASSIGNED"})
 write(AXOUT,[{**x,"contribution_bits":f"{x['contribution_bits']:.12g}"} for x in axis_rows],list(axis_rows[0]));channel=[]
 for layer in LAYERS:
  obj=sum(x["contribution_bits"] for x in axis_rows if x["layer"]==layer and x["axis_class"]=="OBJECT_AXIS");rel=sum(x["contribution_bits"] for x in axis_rows if x["layer"]==layer and x["axis_class"]=="RELATION_AXIS")
  channel.append({"layer":layer,"object_axis_bits":obj,"relation_axis_bits":rel,"relation_minus_object_bits":rel-obj,"interpretation":"HOST_PRIMARY" if layer=="PAGE_HOST_CHAR3" else ("RELATION_LAYOUT_INCREMENT" if layer in {"HOST_PLUS_DY","HOST_PLUS_RIGHT"} else "CONTROL_OR_DILUTION"),"semantic_role":"UNASSIGNED"})
 write(CHANNEL,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in channel],list(channel[0]));host=lambda a:float(p[a,"PAGE_HOST_CHAR3"]["gain_vs_nuisance_bits"]);inc=lambda a,l:float(p[a,l]["increment_vs_page_host_bits"])
 def statistic(group):
  A=set(group);B=set(axes)-A;return sum(host(a) for a in A)-sum(host(a) for a in B)+sum(inc(a,"HOST_PLUS_DY")+inc(a,"HOST_PLUS_RIGHT") for a in B)-sum(inc(a,"HOST_PLUS_DY")+inc(a,"HOST_PLUS_RIGHT") for a in A)
 null=[]
 for group in itertools.combinations(axes,4):null.append({"channel_a_axes":";".join(group),"architecture_score":statistic(group),"is_preexisting_object_partition":int(set(group)==set(OBJECT))})
 null.sort(key=lambda x:(-x["architecture_score"],x["channel_a_axes"]));
 for i,x in enumerate(null,1):x["rank"]=i
 write(NULL,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in null],list(null[0]));fixed=next(x for x in null if x["is_preexisting_object_partition"]==1);pval=sum(x["architecture_score"]>=fixed["architecture_score"]-1e-15 for x in null)/len(null)
 preds=[{"prediction_id":"HPR2_TWOCHANNEL_P01","future_scope":"GENUINELY_NEW_NON_F84_EXTERNAL_PANEL","prediction":"PAGE_HOST beats RAW and COMPILER_ONLY primarily on OBJECT_AXIS outcomes","failure":"object-axis PAGE_HOST margin <= 0 or relation axes carry equal/larger margin","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},{"prediction_id":"HPR2_TWOCHANNEL_P02","future_scope":"GENUINELY_NEW_NON_F84_EXTERNAL_PANEL","prediction":"DY and RIGHT additions improve RELATION_AXIS more than OBJECT_AXIS","failure":"either layer has relation-minus-object increment <= 0","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},{"prediction_id":"HPR2_TWOCHANNEL_P03","future_scope":"GENUINELY_NEW_NON_F84_EXTERNAL_PANEL","prediction":"B3 adds less than 1 bit per axis family after PAGE_HOST","failure":"absolute B3 increment >= 4 bits in either four-axis family under active-only encoding","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},{"prediction_id":"HPR2_TWOCHANNEL_P04","future_scope":"GENUINELY_NEW_NON_F84_EXTERNAL_PANEL","prediction":"WRAPPER and O_OT_FRAME do not improve OBJECT_AXIS over PAGE_HOST","failure":"selector-paid object-axis increment > 0 for either","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"}];write(PRED,preds,list(preds[0]));by={x["layer"]:x for x in channel};status="PAGE_HOST_OBJECT_AXIS_DY_RIGHT_RELATION_AXIS_DECOMPOSITION_EXPLORATORY"
 REPORT.write_text(f"""# GDT104 — HPR2 object-axis versus relation-axis decomposition

## Outcome

**{status}**

The GDT103 PAGE_HOST signal separates sharply under the pre-existing axis
schema. PAGE_HOST contributes {by['PAGE_HOST_CHAR3']['object_axis_bits']:+.3f}
bits on the four object/content axes and
{by['PAGE_HOST_CHAR3']['relation_axis_bits']:+.3f} on the four relation/layout
axes. DY adds only {by['HOST_PLUS_DY']['object_axis_bits']:+.3f} on object axes
but {by['HOST_PLUS_DY']['relation_axis_bits']:+.3f} on relation axes.
RIGHT_FAMILY adds {by['HOST_PLUS_RIGHT']['object_axis_bits']:+.3f} and
{by['HOST_PLUS_RIGHT']['relation_axis_bits']:+.3f}, respectively. B3 is near
zero in both channels.

The exact four-versus-four partition diagnostic ranks the pre-existing object
partition {fixed['rank']}/70 (inclusive p={pval:.5f}). This is interesting but
post-hoc: the axes are correlated, scores come from an exposed archive, and
REL_ARRAY_OR_GROUP behaves partly like an object/page-ecology axis. It is not
a confirmation p-value.

The most coherent current generator is therefore two-channel: PAGE_HOST is a
candidate object/content address, while DY and RIGHT_FAMILY carry smaller
relation/layout rendering information. This remains a layer-level hypothesis;
no individual PAGE_HOST, DY, or RIGHT_FAMILY value receives a semantic role or
gloss. Four exact future non-f84 predictions are frozen in
`gdt104_frozen_predictions.tsv`. f84r receives none and remains untouched.
""",encoding="utf-8")
 result={"schema":"GDT104_HPR2_TWO_CHANNEL_DECOMPOSITION_RESULT_V1","status":status,"axes":len(axes),"object_axes":list(OBJECT),"relation_axes":list(REL),"channel_decomposition":{x["layer"]:x for x in channel},"partition_worlds":len(null),"object_partition_rank":fixed["rank"],"partition_diagnostic_p":pval,"frozen_predictions":len(preds),"interpretation":"Exploratory two-channel HPR2 lead: PAGE_HOST aligns with object/content axes, DY/RIGHT with relation/layout increments, B3 with neither.","semantic_role":"UNASSIGNED","claim_ceiling":"Layer-level archived association and frozen future predictions only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False,"prediction_made":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt103_result.json":sha(ROOT/"gdt103_result.json"),"gdt068_result.json":sha(ROOT/"gdt068_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{AXOUT.name:sha(AXOUT),CHANNEL.name:sha(CHANNEL),NULL.name:sha(NULL),PRED.name:sha(PRED)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"object_host":by['PAGE_HOST_CHAR3']['object_axis_bits'],"relation_host":by['PAGE_HOST_CHAR3']['relation_axis_bits'],"dy_relation":by['HOST_PLUS_DY']['relation_axis_bits'],"rank":fixed['rank'],"p":pval},sort_keys=True))
if __name__=="__main__":main()
