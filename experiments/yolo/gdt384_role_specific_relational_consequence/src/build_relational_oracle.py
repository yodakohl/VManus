#!/usr/bin/env python3
"""Build hidden role-independent relation gold from CoReMA/PCEEC2 sources."""
from __future__ import annotations
import csv,gzip,hashlib,html,io,json,os,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt384_role_specific_relational_consequence"
ART=BASE/"artifacts"
ENC=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz"
COREMA=ROOT/"gdt176_corema_role_oracle.tsv"
FREEZE=ART/"gdt384_stage_a_freeze.json"
ROLES=["COORDINATOR","ALTERNATIVE_OR","REF_ANAPHORA","UNTIL_STATE_GATE","POLARITY_EXCLUSION","FUNCTION_WORD"]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def bundle(paths,root):
 h=hashlib.sha256()
 for p in sorted(paths,key=lambda q:str(q.relative_to(root))):h.update(str(p.relative_to(root)).encode());h.update(b"\0");h.update(p.read_bytes());h.update(b"\0")
 return h.hexdigest()
def read_tsv(p):
 op=gzip.open if p.suffix==".gz" else open
 with op(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write_gz(p,rows):
 raw=p.open("wb");gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0);f=io.TextIOWrapper(gz,encoding="utf-8",newline="")
 with f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def write(p,rows):
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def canon(token):
 token=html.unescape(token).lower().replace("[th]","þ").replace("[gh]","ȝ").replace("þ","th").replace("ð","th").replace("ȝ","y")
 token=unicodedata.normalize("NFKD",token);return "".join(ch for ch in token if ch.isalpha())
def sexprs(text):
 stack=[]
 for m in re.finditer(r"\(|\)|[^\s()]+",text):
  tok=m.group()
  if tok=="(":stack.append([])
  elif tok==")":
   if not stack:continue
   node=stack.pop()
   if stack:stack[-1].append(node)
   else:yield node
  elif stack:stack[-1].append(tok)
def label(node):return node[0] if isinstance(node,list) and node and isinstance(node[0],str) else ""
def terminals(node,anc=(),out=None):
 if out is None:out=[]
 if not isinstance(node,list) or not node:return out
 tag=label(node)
 if len(node)==2 and isinstance(node[1],str):out.append({"pos":tag,"token":node[1],"ancestors":anc,"node":node})
 else:
  for c in node[1:] if tag else node:
   if isinstance(c,list):terminals(c,anc+(tag,),out)
 return out
def base(tag):return re.split(r"[-=]",tag)[0]
def coarse(tag):
 b=base(tag)
 if b.startswith("NP"):return "NP"
 if b.startswith("PP"):return "PP"
 if b.startswith("ADJP"):return "ADJP"
 if b.startswith("ADVP"):return "ADVP"
 if b.startswith("IP"):return "IP"
 if b.startswith("CP"):return "CP"
 if b in {"VP","RRC","QP"}:return b
 return ""
def annotate_nodes(roots,visible):
 visible_ids={id(x["node"]):i for i,x in enumerate(visible)};nodes=[];parent={};spans={};tags={}
 def walk(n,par=None,depth=0):
  if not isinstance(n,list) or not n:return []
  nid=id(n);parent[nid]=id(par) if par is not None else None;tags[nid]=label(n);idx=[]
  if nid in visible_ids:idx=[visible_ids[nid]]
  else:
   for c in n[1:] if label(n) else n:
    if isinstance(c,list):idx.extend(walk(c,n,depth+1))
  if idx:spans[nid]=(min(idx),max(idx),depth);nodes.append(nid)
  return idx
 for r in roots:walk(r)
 return nodes,parent,spans,tags
def dist_to_lca(a,b,parent):
 aa={};x=a;d=0
 while x is not None:aa[x]=d;x=parent.get(x);d+=1
 x=b;db=0
 while x is not None:
  if x in aa:return aa[x]+db,x
  x=parent.get(x);db+=1
 return 999,None
def pceec_relations(roots,visible):
 nodes,parent,spans,tags=annotate_nodes(roots,visible);n=len(visible);out=[]
 verb_pos=("VB","VAN","VAG","VBN","VBI","MD","BE","BEP","BED","BEN","BAG","HV","HVP","HVD","HVN","DO","DOP","DOD")
 for p in range(n):
  left=[x for x in nodes if spans[x][1]==p-1 and coarse(tags[x])]
  right=[x for x in nodes if spans[x][0]==p+1 and coarse(tags[x])]
  same=False;cross=False;arity=0
  for a in left:
   for b in right:
    distance,lca=dist_to_lca(a,b,parent)
    if distance<=4:
     ca,cb=coarse(tags[a]),coarse(tags[b]);same|=ca==cb;cross|=ca!=cb
     if lca:
      children=[x for x in nodes if parent.get(x)==lca and coarse(tags[x])]
      arity=max(arity,len(children))
  # Smallest hidden scope container with material after its right edge.
  containing=[x for x in nodes if spans[x][0]<=p<=spans[x][1] and base(tags[x]) in {"PP","CP","IP"} and spans[x][1]>p and spans[x][1]<n-1]
  if containing:
   scope=min(containing,key=lambda x:(spans[x][1]-spans[x][0],-spans[x][2]));scope_y=1;horizon=spans[scope][1]-p
  else:scope_y=0;horizon=0
  # Clause attachment is independent of whether the pivot itself is NEG.
  clause=[x for x in nodes if spans[x][0]<=p<=spans[x][1] and base(tags[x]) in {"IP","VP"}]
  attached=0
  for c in clause:
   if any(spans[x][0]>=spans[c][0] and spans[x][1]<=spans[c][1] and any(visible[k]["pos"].startswith(verb_pos) for k in range(spans[x][0],spans[x][1]+1)) for x in nodes):attached=1;break
  out.append({"COORDINATOR":int(same),"ALTERNATIVE_OR":int(same),"UNTIL_STATE_GATE":scope_y,"POLARITY_EXCLUSION":attached,"FUNCTION_WORD":int(cross),"scope_horizon":horizon,"sibling_arity":arity})
 return out

def build_corema(keys):
 rows=read_tsv(COREMA);byrec=defaultdict(list);byconcept=defaultdict(list)
 for r in rows:byrec[(r["collection_id"],r["recipe_id"])].append(r);c=r["concept_id"];byconcept[(r["collection_id"],c)].append(r)
 out={}
 for (col,rec),rr in byrec.items():
  rr.sort(key=lambda x:int(x["element_ordinal"]));instruction={};ino=0;children=defaultdict(list)
  for r in rr:
   if r["role"]=="INSTRUCTION":ino+=1;instruction[ino]=int(r["element_ordinal"])
   if int(r["parent_instruction_ordinal"])>0:children[int(r["parent_instruction_ordinal"])].append(r)
  for j,r in enumerate(rr):
   key=f'COREMA:{col}:{rec}:{r["element_ordinal"]}'
   if key not in keys:continue
   p=int(r["parent_instruction_ordinal"]);concept=r["concept_id"]
   distinct={x["concept_id"] for x in children[p] if x["concept_id"] not in {"","NONE"}} if p else set()
   alt=int(p>0 and len(distinct)>=2)
   ref=int(p in instruction and instruction[p]<int(r["element_ordinal"]))
   horizon=0
   if p:
    for k in range(j+1,len(rr)):
     if int(rr[k]["parent_instruction_ordinal"])!=p:horizon=k-j;break
   gate=int(horizon>0)
   contexts={(x["recipe_id"],int(x["parent_instruction_ordinal"])) for x in byconcept[(col,concept)]} if concept not in {"","NONE"} else set()
   parented={int(x["parent_instruction_ordinal"])>0 for x in byconcept[(col,concept)]} if concept not in {"","NONE"} else set()
   polarity=int(bool(concept not in {"","NONE"} and (len(parented)>=2 or len(contexts)>=2)))
   out[key]={"COORDINATOR":None,"ALTERNATIVE_OR":alt,"REF_ANAPHORA":ref,"UNTIL_STATE_GATE":gate,"POLARITY_EXCLUSION":polarity,"FUNCTION_WORD":None,"scope_horizon":horizon,"sibling_arity":len(children[p]) if p else 0,"gold_source":"COREMA_EDITOR_GRAPH"}
 return out

def build_pceec(pceec,keys):
 out={};parsed=pceec/"data/parsed"
 for path in sorted(parsed.glob("*.psd")):
  kept=0;ordinal=0
  for form in sexprs(path.read_text(encoding="utf-8",errors="replace")):
   roots=[x for x in form if isinstance(x,list) and label(x) not in {"CODE","METADATA","ID"}]
   if not roots:continue
   ts=[]
   for root in roots:terminals(root,(),ts)
   visible=[x for x in ts if x["pos"] not in {"PUNC","CODE","ID"} and canon(x["token"]) and not x["token"].startswith("*") and x["token"]!="0"]
   if len(visible)<3:continue
   ordinal+=1;kept+=1;rels=pceec_relations(roots,visible)
   for j,z in enumerate(rels):
    if len(visible)>180:
     chunk=j//180+1;within=j%180+1;record=f"{path.stem}:{ordinal}:C{chunk}"
    else:record=f"{path.stem}:{ordinal}";within=j+1
    key=f"PCEEC2:{path.stem}:{record}:{within}"
    if key not in keys:continue
    out[key]={**z,"REF_ANAPHORA":None,"gold_source":"PCEEC2_PARSE"}
   if kept>=12:break
 return out

def main():
 freeze=json.loads(FREEZE.read_text());assert freeze["status"]=="FROZEN_BEFORE_RELATION_CONSTRUCTION_OR_SCORING"
 pceec_env=os.environ.get("GDT384_PCEEC2_DIR")
 if not pceec_env:raise SystemExit("set GDT384_PCEEC2_DIR to exact PCEEC2 checkout")
 pceec=Path(pceec_env);parsed=list((pceec/"data/parsed").glob("*.psd"));assert len(parsed)==84
 commit=os.popen(f"git -C {pceec!s} rev-parse HEAD").read().strip();assert commit=="bf79d1c46e8ef983a7347b0664d0d80243f32831"
 bsha=bundle(parsed,pceec);assert bsha=="c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714"
 enc=read_tsv(ENC);selected={x["element_key"] for x in enc if x["domain"] in {"COREMA","PCEEC2"}};assert len(selected)==54867
 rel=build_corema(selected);rel.update(build_pceec(pceec,selected));assert set(rel)==selected
 rows=[]
 for x in enc:
  if x["element_key"] not in selected:continue
  z=rel[x["element_key"]];row={"element_key":x["element_key"],"domain":x["domain"],"collection_id":x["collection_id"],"record_id":x["record_id"],"element_ordinal":x["element_ordinal"],"gold_source":z["gold_source"]}
  for role in ROLES:row[role+"_available"]=int(z.get(role) is not None);row[role+"_relation_y"]="" if z.get(role) is None else int(z[role])
  row["scope_horizon"]=z["scope_horizon"];row["sibling_arity"]=z["sibling_arity"];rows.append(row)
 path=ART/"gdt384_hidden_relational_oracle.tsv.gz";write_gz(path,rows)
 caps=[]
 for role in ROLES:
  for domain in ["COREMA","PCEEC2"]:
   q=[r for r in rows if r["domain"]==domain and r[role+"_available"]==1]
   caps.append({"role":role,"domain":domain,"available_rows":len(q),"positives":sum(int(r[role+"_relation_y"]) for r in q),"negatives":len(q)-sum(int(r[role+"_relation_y"]) for r in q),"gold_source":q[0]["gold_source"] if q else "UNAVAILABLE"})
 cap=ART/"gdt384_relation_capacity.tsv";write(cap,caps)
 result={"schema":"GDT384_RELATION_ORACLE_BUILD_V1","status":"HIDDEN_RELATION_LAYER_BUILT_AFTER_FREEZE","rows":len(rows),"domains":{"COREMA":sum(r["domain"]=="COREMA" for r in rows),"PCEEC2":sum(r["domain"]=="PCEEC2" for r in rows)},"pceec_commit":commit,"pceec_bundle_sha256":bsha,"inputs":{str(FREEZE.relative_to(ROOT)):sha(FREEZE),str(ENC.relative_to(ROOT)):sha(ENC),str(COREMA.relative_to(ROOT)):sha(COREMA)},"outputs":{str(path.relative_to(ROOT)):sha(path),str(cap.relative_to(ROOT)):sha(cap)},"implementation":{str((BASE/"src/build_relational_oracle.py").relative_to(ROOT)):sha(BASE/"src/build_relational_oracle.py")},"contains_source_words":False,"contains_pos_or_parse_labels":False,"voynich_rows_read":0,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"HIDDEN_COMPARATOR_RELATION_GOLD_ONLY"};result["content_hash"]=content(result);(ART/"gdt384_relation_oracle_build.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"rows":len(rows),"capacity":caps},sort_keys=True))
if __name__=="__main__":main()
