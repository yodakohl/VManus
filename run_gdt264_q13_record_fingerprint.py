#!/usr/bin/env python3
"""GDT264: retrieve held halves of q13 records within physical page."""
import csv, hashlib, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SRC = "gdt227_q13_abstract_interlinear.tsv"
ACCESS = "gdt257_result.json"
METHOD = "GDT264_Q13_RECORD_FINGERPRINT_METHOD.md"
REPS = ["STRUCTURE_ONLY", "COMPILER_COARSE", "RAW_EXACT", "PAGE_HOST_EXACT", "RAW_CHAR3", "PAGE_HOST_CHAR3"]
SEEDS = ["GDT264-S0", "GDT264-S1", "GDT264-S2", "GDT264-S3"]
NWORLD = 4096
COMPONENTS = ["WRAPPER", "FRAME_INNERD", "RIGHT", "CLOSURE", "JOINT_CELL"]

def sha(path):
    return hashlib.sha256((R/path).read_bytes()).hexdigest()

def read(path):
    with (R/path).open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def write(path, rows):
    with (R/path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def locus_num(s):
    return int(s.split(".")[-1])

def trigrams(s):
    z = "^" + s + "$"
    return [z[i:i+3] for i in range(max(0, len(z)-2))]

def features(rows, rep):
    out = Counter()
    for x in rows:
        toks = x["source_tokens"].split("|") if x["source_tokens"] else []
        hosts = x["page_hosts"].split("|") if x["page_hosts"] else []
        cells = x["compiler_cells"].split("|") if x["compiler_cells"] else []
        assert len(toks) == len(hosts) == len(cells) == int(x["field_group_count"])
        if rep == "STRUCTURE_ONLY":
            n = int(x["field_group_count"])
            out["SIZE:" + (str(n) if n <= 4 else "5+")] += 1
            out["END:" + x["line_field_end"]] += 1
            out["CLASS:" + x["abstract_role_like"]] += 1
        elif rep == "COMPILER_COARSE":
            for c in cells:
                p = c.split(":"); assert len(p) == 6
                labels = ["WRAP", "FRAME", "INNERD", "RIGHT", "DY", "B3"]
                for k,v in zip(labels,p): out[k+":"+v] += 1
                out["CELL:"+c] += 1
        elif rep == "RAW_EXACT":
            for t in toks: out["RAW:"+t] += 1
        elif rep == "PAGE_HOST_EXACT":
            for h in hosts: out["HOST:"+h] += 1
        elif rep == "RAW_CHAR3":
            for t in toks:
                for g in trigrams(t): out["R3:"+g] += 1
        elif rep == "PAGE_HOST_CHAR3":
            for h in hosts:
                for g in trigrams(h): out["H3:"+g] += 1
        else: raise AssertionError(rep)
    return out

def component_features(rows, block):
    out=Counter()
    for x in rows:
        cells=x["compiler_cells"].split("|") if x["compiler_cells"] else []
        for c in cells:
            w,fr,ind,ri,dy,b3=c.split(":")
            if block=="WRAPPER": out["WRAP:"+w]+=1
            elif block=="FRAME_INNERD": out["FRAME:"+fr]+=1; out["INNERD:"+ind]+=1
            elif block=="RIGHT": out["RIGHT:"+ri]+=1
            elif block=="CLOSURE": out["DY:"+dy]+=1; out["B3:"+b3]+=1
            elif block=="JOINT_CELL": out["CELL:"+c]+=1
            else: raise AssertionError(block)
    return out

def cosine(a,b,idf):
    keys=set(a)|set(b); dot=aa=bb=0.0
    for k in keys:
        w=idf.get(k,0.0); x=a.get(k,0)*w; y=b.get(k,0)*w
        dot+=x*y; aa+=x*x; bb+=y*y
    return dot/math.sqrt(aa*bb) if aa and bb else 0.0

def split_loci(loci, seed):
    q=sorted(loci,key=lambda z:hashlib.sha256((seed+"|"+z).encode()).hexdigest())
    cut=len(q)//2
    assert cut>=2 and len(q)-cut>=2
    return set(q[:cut]),set(q[cut:])

def main():
    src=read(SRC)
    assert src and all(not x["page"].startswith("f84") for x in src)
    access=json.loads((R/ACCESS).read_text())
    assert access["access"]["pristine_access_seal"] is False
    rec=defaultdict(list); loci=defaultdict(set)
    for x in src:
        rec[(x["page"],x["record_id"])].append(x); loci[(x["page"],x["record_id"])].add(x["locus"])
    bypage=defaultdict(list)
    for key,ls in loci.items():
        if len(ls)>=4: bypage[key[0]].append(key[1])
    pages={p:sorted(v) for p,v in bypage.items() if len(v)==2}
    assert len(pages)==9 and sum(len(v) for v in pages.values())==18

    views={}; meta={}
    for p,rs in pages.items():
        for rid in rs:
            for si,seed in enumerate(SEEDS):
                A,B=split_loci(loci[(p,rid)],seed)
                for vn,keep in [("A",A),("B",B)]:
                    rows=[x for x in rec[(p,rid)] if x["locus"] in keep]
                    k=(p,rid,si,vn); meta[k]=(len(keep),len(rows),";".join(sorted(keep,key=locus_num)))
                    for rep in REPS: views[(rep,)+k]=features(rows,rep)

    idfs={}
    for rep in REPS:
        vv=[v for k,v in views.items() if k[0]==rep]; n=len(vv); df=Counter()
        for v in vv:
            for z in v: df[z]+=1
        idfs[rep]={z:math.log((1+n)/(1+d))+1 for z,d in df.items()}

    preds=[]
    for rep in REPS:
        for p,rs in sorted(pages.items()):
            for si,seed in enumerate(SEEDS):
                for srcv,dstv in [("A","B"),("B","A")]:
                    for rid in rs:
                        q=views[(rep,p,rid,si,srcv)]
                        scores=[]
                        for cand in rs:
                            s=cosine(q,views[(rep,p,cand,si,dstv)],idfs[rep]); scores.append((s,cand))
                        scores.sort(key=lambda x:(-x[0],x[1])); rank=1+[x[1] for x in scores].index(rid)
                        top=scores[0][1]
                        preds.append({"representation":rep,"page":p,"record_id":rid,"split_index":si,"split_seed":seed,"direction":srcv+"_TO_"+dstv,"query_loci":meta[(p,rid,si,srcv)][2],"target_loci":meta[(p,rid,si,dstv)][2],"candidate_count":2,"true_score":f"{dict((b,a) for a,b in scores)[rid]:.12f}","competitor_score":f"{dict((b,a) for a,b in scores)[[x for x in rs if x!=rid][0]]:.12f}","rank":rank,"top1":int(rank==1),"reciprocal_rank":f"{1/rank:.12f}"})

    score=[]
    for rep in REPS:
        z=[x for x in preds if x["representation"]==rep]
        top=sum(int(x["top1"]) for x in z); mrr=sum(float(x["reciprocal_rank"]) for x in z)/len(z)
        margins=[float(x["true_score"])-float(x["competitor_score"]) for x in z]
        pagewins=sum(sum(float(x["true_score"])-float(x["competitor_score"]) for x in z if x["page"]==p)>0 for p in pages)
        score.append({"representation":rep,"predictions":len(z),"top1_correct":top,"top1_accuracy":f"{top/len(z):.12f}","chance_accuracy":"0.500000000000","mean_reciprocal_rank":f"{mrr:.12f}","mean_true_minus_competitor":f"{sum(margins)/len(margins):.12f}","positive_aggregate_pages":pagewins,"eligible_pages":len(pages)})

    # Shared within-page/split destination swaps, preserving every opportunity.
    rng=random.Random(26420260817)
    obs={x["representation"]:int(x["top1_correct"]) for x in score}
    nulltops={r:[] for r in REPS}; maxstats=[]
    # Precompute raw scored choices, then relabel destination identity by a flip.
    lookup=defaultdict(dict)
    for rep in REPS:
        for p,rs in pages.items():
            for si in range(len(SEEDS)):
                for srcv,dstv in [("A","B"),("B","A")]:
                    for rid in rs:
                        q=views[(rep,p,rid,si,srcv)]
                        lookup[(rep,p,si,srcv,dstv,rid)]={c:cosine(q,views[(rep,p,c,si,dstv)],idfs[rep]) for c in rs}
    nullrows=[]
    for w in range(NWORLD):
        flips={(p,si):rng.randrange(2) for p in pages for si in range(len(SEEDS))}
        vals={}
        for rep in REPS:
            top=0
            for p,rs in pages.items():
                for si in range(len(SEEDS)):
                    perm={rs[0]:rs[1],rs[1]:rs[0]} if flips[(p,si)] else {rs[0]:rs[0],rs[1]:rs[1]}
                    for srcv,dstv in [("A","B"),("B","A")]:
                        for rid in rs:
                            sc=lookup[(rep,p,si,srcv,dstv,rid)]
                            ranked=sorted(rs,key=lambda c:(-sc[c],c))
                            # Candidate destination c now bears identity perm[c].
                            predicted_identity=perm[ranked[0]]
                            top += int(predicted_identity==rid)
            vals[rep]=top; nulltops[rep].append(top)
        maxstats.append(max((vals[r]-72)/math.sqrt(36) for r in REPS))
        if w<64: nullrows.append({"world":w,**{r:vals[r] for r in REPS},"max_standardized_top1":f"{maxstats[-1]:.12f}"})
    for x in score:
        rep=x["representation"]; o=obs[rep]
        x["local_inclusive_p"] = f"{(1+sum(v>=o for v in nulltops[rep]))/(1+NWORLD):.12f}"
        st=(o-72)/math.sqrt(36)
        x["max_six_inclusive_p"] = f"{(1+sum(v>=st for v in maxstats))/(1+NWORLD):.12f}"
        x["null_mean_top1"] = f"{sum(nulltops[rep])/NWORLD:.12f}"

    # Post-hoc compiler decomposition nominated only after the primary
    # COMPILER_COARSE result was visible.
    cviews={}; cidfs={}
    for p,rs in pages.items():
        for rid in rs:
            for si,seed in enumerate(SEEDS):
                A,B=split_loci(loci[(p,rid)],seed)
                for vn,keep in [("A",A),("B",B)]:
                    rr=[x for x in rec[(p,rid)] if x["locus"] in keep]
                    for b in COMPONENTS:cviews[(b,p,rid,si,vn)]=component_features(rr,b)
    for b in COMPONENTS:
        vv=[v for k,v in cviews.items() if k[0]==b]; n=len(vv); df=Counter()
        for v in vv:
            for z in v:df[z]+=1
        cidfs[b]={z:math.log((1+n)/(1+d))+1 for z,d in df.items()}
    cpred=[]; clook=defaultdict(dict)
    for b in COMPONENTS:
        for p,rs in sorted(pages.items()):
            for si in range(len(SEEDS)):
                for sv,dv in [("A","B"),("B","A")]:
                    for rid in rs:
                        q=cviews[(b,p,rid,si,sv)]
                        sc={c:cosine(q,cviews[(b,p,c,si,dv)],cidfs[b]) for c in rs}
                        clook[(b,p,si,sv,dv,rid)]=sc
                        ranked=sorted(rs,key=lambda c:(-sc[c],c)); other=[c for c in rs if c!=rid][0]
                        cpred.append((b,p,int(ranked[0]==rid),sc[rid]-sc[other]))
    cscore=[]
    for b in COMPONENTS:
        z=[x for x in cpred if x[0]==b]; top=sum(x[2] for x in z)
        cscore.append({"component":b,"analysis_status":"POSTHOC_DECOMPOSITION","predictions":len(z),"top1_correct":top,"top1_accuracy":f"{top/len(z):.12f}","mean_true_minus_competitor":f"{sum(x[3] for x in z)/len(z):.12f}","positive_aggregate_pages":sum(sum(x[3] for x in z if x[1]==p)>0 for p in pages),"eligible_pages":len(pages)})
    rng2=random.Random(26420260817); allvals={b:[] for b in COMPONENTS}; maxvals=[]
    for _ in range(NWORLD):
        flips={(p,si):rng2.randrange(2) for p in pages for si in range(len(SEEDS))}; vals={}
        for b in COMPONENTS:
            top=0
            for p,rs in pages.items():
                for si in range(len(SEEDS)):
                    perm={rs[0]:rs[1],rs[1]:rs[0]} if flips[(p,si)] else {rs[0]:rs[0],rs[1]:rs[1]}
                    for sv,dv in [("A","B"),("B","A")]:
                        for rid in rs:
                            sc=clook[(b,p,si,sv,dv,rid)]; ranked=sorted(rs,key=lambda c:(-sc[c],c))
                            top+=int(perm[ranked[0]]==rid)
            vals[b]=top; allvals[b].append(top)
        maxvals.append(max((vals[b]-72)/math.sqrt(36) for b in COMPONENTS))
    for x in cscore:
        b=x["component"];o=int(x["top1_correct"]);st=(o-72)/math.sqrt(36)
        x["local_inclusive_p"]=f"{(1+sum(v>=o for v in allvals[b]))/(1+NWORLD):.12f}"
        x["max_five_inclusive_p"]=f"{(1+sum(v>=st for v in maxvals))/(1+NWORLD):.12f}"
        x["null_mean_top1"]=f"{sum(allvals[b])/NWORLD:.12f}"

    write("gdt264_record_fingerprint_predictions.tsv",preds)
    write("gdt264_record_fingerprint_scores.tsv",score)
    write("gdt264_compiler_component_scores.tsv",cscore)
    write("gdt264_record_fingerprint_null.tsv",nullrows)
    best=max(score,key=lambda x:(int(x["top1_correct"]),float(x["mean_true_minus_competitor"])))
    host=next(x for x in score if x["representation"]=="PAGE_HOST_EXACT")
    raw=next(x for x in score if x["representation"]=="RAW_EXACT")
    counters=[
      {"counterexample":"PAGE_HOST_VS_RAW","value":f"host {host['top1_correct']}/144; raw {raw['top1_correct']}/144","consequence":"HPR2 stripping must beat rather than merely resemble visible groups to localize a content channel"},
      {"counterexample":"WITHIN_PAGE_ONLY","value":"nine pages with exactly two eligible records","consequence":"retrieval cannot establish a manuscript-wide dictionary or cross-page topic"},
      {"counterexample":"MECHANICAL_RECORDS","value":"GDT227 record scaffold rather than complete authorial paragraph census","consequence":"record identity is a formal segmentation endpoint, not a translated paragraph"},
      {"counterexample":"EXPOSED_EXPLORATORY_PANEL","value":"all records and representations were already available","consequence":"p-values quantify a fixed retrieval diagnostic but are not pristine confirmation"},
    ]
    write("gdt264_counterexamples.tsv",counters)
    status = "Q13_RECORD_LOCAL_FINGERPRINT_EXPLORATORY" if float(best["max_six_inclusive_p"])<=0.1 else "Q13_RECORD_FINGERPRINT_NOT_ABOVE_WITHIN_PAGE_NULL"
    cbest=max(cscore,key=lambda x:int(x["top1_correct"]))
    result={"experiment":"GDT264_Q13_RECORD_FINGERPRINT","status":status,"eligible_pages":len(pages),"eligible_records":18,"split_seeds":len(SEEDS),"predictions_per_representation":144,"representations":REPS,"best_representation":best["representation"],"best_top1":int(best["top1_correct"]),"best_local_p":float(best["local_inclusive_p"]),"best_max_six_p":float(best["max_six_inclusive_p"]),"page_host_top1":int(host["top1_correct"]),"raw_exact_top1":int(raw["top1_correct"]),"posthoc_compiler_decomposition":{"best_component":cbest["component"],"top1":int(cbest["top1_correct"]),"max_five_p":float(cbest["max_five_inclusive_p"])},"semantic_assignments":0,"interpretation":"Tests whether q13 mechanical records have a within-page formal fingerprint; it does not identify a topic or translate content.","claim_ceiling":"Within-page record-mate retrieval only; no paragraph topic label object procedure word language plaintext or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{SRC:sha(SRC),ACCESS:sha(ACCESS)},"documents":{METHOD:sha(METHOD)},"outputs":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
    # Report is generated before its hash is inserted into result.
    lines=["# GDT264 — q13 within-page record fingerprint", "", f"Status: **{status}**.", "", "## Result", "", "Each half-record had to retrieve its mate from the two eligible records on the same physical page. Page, section, hand, and broad illustration/register ecology are therefore fixed.", "", "| representation | top-1 / 144 | accuracy | local p | max-six p | positive pages |", "|---|---:|---:|---:|---:|---:|"]
    for x in sorted(score,key=lambda z:-int(z["top1_correct"])):
        lines.append(f"| {x['representation']} | {x['top1_correct']} | {float(x['top1_accuracy']):.3f} | {float(x['local_inclusive_p']):.4f} | {float(x['max_six_inclusive_p']):.4f} | {x['positive_aggregate_pages']}/9 |")
    lines += ["", f"The strongest representation is **{best['representation']}** at {best['top1_correct']}/144 top-1 retrievals (max-six p={float(best['max_six_inclusive_p']):.4f}). PAGE_HOST exact identity scores {host['top1_correct']}/144 and raw exact groups {raw['top1_correct']}/144.", "", "## Post-hoc compiler decomposition", "", "| compiler block | top-1 / 144 | local p | max-five p | positive pages |", "|---|---:|---:|---:|---:|"]
    for x in sorted(cscore,key=lambda z:-int(z["top1_correct"])):
        lines.append(f"| {x['component']} | {x['top1_correct']} | {float(x['local_inclusive_p']):.4f} | {float(x['max_five_inclusive_p']):.4f} | {x['positive_aggregate_pages']}/9 |")
    lines += ["", f"The post-hoc lead is **{cbest['component']}** at {cbest['top1_correct']}/144. Because this block search was nominated after seeing the primary compiler result, it localizes the descriptive mechanism but is not preregistered confirmation.", "", "This is a prerequisite test for a latent topic/address scale. A positive record fingerprint means only that nonadjacent pieces of the same mechanical record share formal inventory beyond a random within-page mate assignment. It does not say what that inventory denotes. Raw strings and PAGE_HOST character texture both retrieve records, but exact PAGE_HOST identity is weak; the strongest signal lies in record rendering, especially wrapper ecology. That favors a record-template explanation over a simple paragraph-local dictionary.", "", "## Limits", "", "The panel contains nine pages and eighteen GDT227 mechanical records, not a complete authorial paragraph census. The split and feature family are exploratory and exposed. The test is within-page by design and cannot establish a global lexicon. All semantic values remain unassigned.", "", "No f84r row was opened, queried, retained, or scored in this experiment. The earlier process-level transient-parse breach remains disclosed; no further f84r access was authorized or performed.", ""]
    (R/"GDT264_Q13_RECORD_FINGERPRINT_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    result["outputs"]={x:sha(x) for x in ["gdt264_record_fingerprint_predictions.tsv","gdt264_record_fingerprint_scores.tsv","gdt264_compiler_component_scores.tsv","gdt264_record_fingerprint_null.tsv","gdt264_counterexamples.tsv","GDT264_Q13_RECORD_FINGERPRINT_REPORT.md"]}
    result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    (R/"gdt264_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"best":best["representation"],"top1":best["top1_correct"],"maxp":best["max_six_inclusive_p"]},sort_keys=True))

if __name__=="__main__": main()
