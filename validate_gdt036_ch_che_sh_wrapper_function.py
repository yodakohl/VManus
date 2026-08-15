#!/usr/bin/env python3
"""Independent reconstruction validator for GDT036."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
RESULT = ROOT / "gdt036_result.json"
VALIDATION = ROOT / "gdt036_validation.json"
WRAPPERS = ("ch", "che", "sh")
FEATURES = (
    "record_state", "line_position", "field_position", "previous_state", "next_state",
    "own_dy_closure", "dy_adjacency", "field_index", "section", "currier", "hand", "register",
)
FORMAL_FEATURES = FEATURES[:8]
ALPHA = 0.5
SHRINK = 5.0
PERMUTATIONS = 5000
SEED = 36036


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tol=2e-8):
    return abs(float(a) - float(b)) <= tol


def cmi(h, f, y, nh, nf, n):
    joint = np.bincount((h * nf + f) * 3 + y, minlength=nh * nf * 3)
    hf = np.bincount(h * nf + f, minlength=nh * nf)
    hw = np.bincount(h * 3 + y, minlength=nh * 3)
    hc = np.bincount(h, minlength=nh)
    answer = 0.0
    for code in np.flatnonzero(joint):
        count = float(joint[code]); wrapper = code % 3; pair = code // 3; host = pair // nf
        answer += count * math.log2(count * float(hc[host]) / (float(hf[pair]) * float(hw[host * 3 + wrapper])))
    return answer / n


def derive_expected(source):
    lines = defaultdict(list)
    for row in source:
        assert not row["locus"].startswith("f84r")
        lines[row["locus"]].append(row)
    candidates = []
    for locus, line in lines.items():
        line.sort(key=lambda x: int(x["group_index"])); n = len(line); field = 1
        for i, row in enumerate(line):
            if row["stripped_prefix"] in WRAPPERS:
                if n == 1: pos = "SINGLE"
                elif i == 0: pos = "FIRST"
                elif i == n - 1: pos = "LAST"
                elif i < n / 3: pos = "EARLY"
                elif i >= 2 * n / 3: pos = "LATE"
                else: pos = "MIDDLE"
                prev = "BOS" if i == 0 else line[i-1]["record_state"]
                nxt = "EOS" if i == n-1 else line[i+1]["record_state"]
                if row["record_state"] == "DY_RESOLUTION": fp = "CLOSE"
                elif i == 0 or prev == "DY_RESOLUTION": fp = "FIELD_START"
                elif i == n-1: fp = "OPEN_TAIL_END"
                else: fp = "FIELD_INTERNAL"
                x = dict(row)
                x.update(wrapper=row["stripped_prefix"], line_position=pos, field_position=fp,
                         previous_state=prev, next_state=nxt, own_dy_closure=str(int(row["dy_closure"])),
                         dy_adjacency=f"PREV{int(prev=='DY_RESOLUTION')}_NEXT{int(nxt=='DY_RESOLUTION')}",
                         field_index=str(min(3, field)), register=f'{row["section"]}|{row["currier"]}|{row["hand"]}')
                candidates.append(x)
            if row["record_state"] == "DY_RESOLUTION": field += 1
    stats = defaultdict(lambda: [0, set(), set()])
    for x in candidates:
        s = stats[x["residual_host"]]; s[0] += 1; s[1].add(x["wrapper"]); s[2].add(x["physical_folio"])
    hosts = {h for h, x in stats.items() if x[0] >= 10 and len(x[1]) >= 2 and len(x[2]) >= 3}
    rows = [x for x in candidates if x["residual_host"] in hosts]
    rows.sort(key=lambda x: (x["locus"], int(x["group_index"]), x["wrapper"]))
    return rows, hosts


def transfer(rows, feature, unit_key, base_mode):
    units = defaultdict(list)
    for i, row in enumerate(rows): units[row[unit_key]].append(i)
    total = 0.0; positive = 0
    for unit in sorted(units):
        test = set(units[unit]); bc = Counter()
        for i, row in enumerate(rows):
            if i in test: continue
            if base_mode=="host_register":key=(row["residual_host"],row["register"])
            elif base_mode=="register":key=row["register"]
            elif base_mode=="host":key=row["residual_host"]
            else:key="_GLOBAL"
            bc[(key,row["wrapper"])]+=1
        obs = Counter(); exp = Counter()
        for i, row in enumerate(rows):
            if i in test: continue
            if base_mode=="host_register":key=(row["residual_host"],row["register"])
            elif base_mode=="register":key=row["register"]
            elif base_mode=="host":key=row["residual_host"]
            else:key="_GLOBAL"
            den=sum(bc[(key,w)]for w in WRAPPERS)+3*ALPHA
            for w in WRAPPERS:
                q=(bc[(key,w)]+ALPHA)/den
                exp[(row[feature],w)] += q
            obs[(row[feature],row["wrapper"])] += 1
        fold = 0.0
        for i in units[unit]:
            row=rows[i]
            if base_mode=="host_register":key=(row["residual_host"],row["register"])
            elif base_mode=="register":key=row["register"]
            elif base_mode=="host":key=row["residual_host"]
            else:key="_GLOBAL"
            den=sum(bc[(key,w)]for w in WRAPPERS)+3*ALPHA
            base=[]; adjusted=[]
            for w in WRAPPERS:
                q=(bc[(key,w)]+ALPHA)/den
                base.append(q); adjusted.append(q*(obs[(row[feature],w)]+SHRINK)/(exp[(row[feature],w)]+SHRINK))
            a=WRAPPERS.index(row["wrapper"]); fold += math.log2((adjusted[a]/sum(adjusted))/base[a])
        total += fold; positive += int(fold > 1e-12)
    return total, positive, len(units)


def host_gain(rows):
    units=defaultdict(list)
    for i,r in enumerate(rows):units[r["physical_folio"]].append(i)
    total=0.;positive=0
    for u in sorted(units):
        test=set(units[u]);hc=Counter();gc=Counter()
        for i,r in enumerate(rows):
            if i in test:continue
            hc[(r["residual_host"],r["wrapper"])]+=1;gc[r["wrapper"]]+=1
        n=len(rows)-len(test);fold=0.
        for i in units[u]:
            r=rows[i];h=r["residual_host"];hd=sum(hc[(h,w)]for w in WRAPPERS)+3*ALPHA
            ph=(hc[(h,r["wrapper"])]+ALPHA)/hd;pg=(gc[r["wrapper"]]+ALPHA)/(n+3*ALPHA)
            fold+=math.log2(ph/pg)
        total+=fold;positive+=int(fold>1e-12)
    return total,positive,len(units)


def main():
    checks=[]; result=json.loads(RESULT.read_text()); body=dict(result); digest=body.pop("result_content_sha256")
    checks += [("schema",result["schema"]=="GDT036_CH_CHE_SH_WRAPPER_FUNCTION_RESULT_V1"),("content_hash",digest==csha(body)),("status",result["status"]=="HOST_LICENSED_WRAPPERS_WITH_WEAK_SHARED_POSITIONAL_TRANSFER_REGISTER_DOMINANT")]
    for section in ("inputs","implementation","outputs","documents"):
        for name,d in result[section].items(): checks.append((f"hash:{section}:{name}",sha(ROOT/name)==d))
    source=read(SOURCE); expected,hosts=derive_expected(source); actual=read(ROOT/"gdt036_wrapper_occurrences.tsv")
    checks += [("eligible_hosts",len(hosts)==49),("rows",len(expected)==len(actual)==3104),("folios",len({r['physical_folio']for r in actual})==94),("f84_excluded",not any(r['locus'].startswith('f84r')for r in actual)),("wrappers",Counter(r['wrapper']for r in actual)==Counter({'sh':1098,'ch':1006,'che':1000}))]
    compare_fields=("locus","group_index","token","wrapper","residual_host","record_state","line_position","field_position","previous_state","next_state","own_dy_closure","dy_adjacency","field_index","register")
    checks.append(("occurrences_exact",all(all(a[k]==e[k]for k in compare_fields)for a,e in zip(actual,expected))))
    tests={r["feature"]:r for r in read(ROOT/"gdt036_feature_tests.tsv")}
    hvals=sorted(hosts);hm={v:i for i,v in enumerate(hvals)};h=np.array([hm[r['residual_host']]for r in actual],dtype=np.int32);ym={v:i for i,v in enumerate(WRAPPERS)};y=np.array([ym[r['wrapper']]for r in actual],dtype=np.int8);groups=[np.flatnonzero(h==i)for i in range(len(hvals))]
    encoded={};observed=[]
    for feat in FEATURES:
        vals=sorted({r[feat]for r in actual});vm={v:i for i,v in enumerate(vals)};f=np.array([vm[r[feat]]for r in actual],dtype=np.int32);encoded[feat]=(f,len(vals));observed.append(cmi(h,f,y,len(hvals),len(vals),len(actual)))
    null=np.empty((PERMUTATIONS,len(FEATURES)));rng=np.random.default_rng(SEED)
    for p in range(PERMUTATIONS):
        yp=y.copy()
        for idx in groups:yp[idx]=rng.permutation(yp[idx])
        for j,feat in enumerate(FEATURES):
            f,nf=encoded[feat];null[p,j]=cmi(h,f,yp,len(hvals),nf,len(actual))
    means=null.mean(axis=0);stds=null.std(axis=0,ddof=1);zs=(np.asarray(observed)-means)/stds;maxz=((null-means)/stds).max(axis=1)
    for j,feat in enumerate(FEATURES):
        row=tests[feat];local=(1+np.count_nonzero(null[:,j]>=observed[j]))/(PERMUTATIONS+1);maxt=(1+np.count_nonzero(maxz>=zs[j]))/(PERMUTATIONS+1)
        lofo,pf,nf=transfer(actual,feat,"physical_folio","host");loho,ph,nh=transfer(actual,feat,"residual_host","global")
        checks += [(f"cmi:{feat}",close(row['cmi_bits_per_row'],observed[j])),(f"permutation:{feat}",close(row['null_mean'],means[j])and close(row['null_sd'],stds[j])and close(row['local_p'],local)and close(row['maxT_p'],maxt)),(f"lofo:{feat}",close(row['lofo_gain_bits'],lofo)and int(row['positive_lofo_folds'])==pf and int(row['lofo_folds'])==nf),(f"loho:{feat}",close(row['loho_gain_bits'],loho)and int(row['positive_loho_folds'])==ph and int(row['loho_folds'])==nh)]
    strata=sorted({(r['residual_host'],r['register'])for r in actual});sm={v:i for i,v in enumerate(strata)};hs=np.array([sm[(r['residual_host'],r['register'])]for r in actual],dtype=np.int32);sgroups=[np.flatnonzero(hs==i)for i in range(len(strata))]
    senc={};sobs=[]
    for feat in FORMAL_FEATURES:
        vals=sorted({r[feat]for r in actual});vm={v:i for i,v in enumerate(vals)};f=np.array([vm[r[feat]]for r in actual],dtype=np.int32);senc[feat]=(f,len(vals));sobs.append(cmi(hs,f,y,len(strata),len(vals),len(actual)))
    snull=np.empty((PERMUTATIONS,len(FORMAL_FEATURES)));rng=np.random.default_rng(SEED+1)
    for p in range(PERMUTATIONS):
        yp=y.copy()
        for idx in sgroups:yp[idx]=rng.permutation(yp[idx])
        for j,feat in enumerate(FORMAL_FEATURES):
            f,nf=senc[feat];snull[p,j]=cmi(hs,f,yp,len(strata),nf,len(actual))
    smeans=snull.mean(axis=0);sstd=snull.std(axis=0,ddof=1);sz=(np.asarray(sobs)-smeans)/sstd;smax=((snull-smeans)/sstd).max(axis=1)
    for j,feat in enumerate(FORMAL_FEATURES):
        row=tests[feat];local=(1+np.count_nonzero(snull[:,j]>=sobs[j]))/(PERMUTATIONS+1);maxt=(1+np.count_nonzero(smax>=sz[j]))/(PERMUTATIONS+1)
        lofo,pf,_=transfer(actual,feat,'physical_folio','host_register');loho,ph,_=transfer(actual,feat,'residual_host','register')
        checks += [(f"register_adjusted_permutation:{feat}",close(row['register_adjusted_cmi_bits_per_row'],sobs[j])and close(row['register_adjusted_local_p'],local)and close(row['register_adjusted_maxT_p'],maxt)),(f"register_adjusted_lofo:{feat}",close(row['register_adjusted_lofo_gain_bits'],lofo)and int(row['register_adjusted_positive_lofo_folds'])==pf),(f"register_adjusted_loho:{feat}",close(row['register_adjusted_loho_gain_bits'],loho)and int(row['register_adjusted_positive_loho_folds'])==ph)]
    hg,hp,hn=host_gain(actual);checks.append(("host_baseline",close(result['host_dependence']['lofo_exact_host_vs_global_gain_bits'],hg)and result['host_dependence']['positive_lofo_folds']==hp and result['host_dependence']['lofo_folds']==hn))
    report=" ".join((ROOT/"GDT036_CH_CHE_SH_WRAPPER_FUNCTION_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text()
    checks += [("claims",all(x in report for x in("host-licensed renderers","no meanings","f84r was not opened"))),("ceiling",all(not result['f84r'][k]for k in result['f84r'])),("ledger",ledger.count("GDT036_CKPT001")==1)]
    failures=[n for n,ok in checks if not ok]
    validation={"schema":"GDT036_CH_CHE_SH_WRAPPER_FUNCTION_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of the 49-host/3104-row selection, every derived construction feature, all 5000 host-stratified permutation distributions and maxT values, all 12 LOFO/LOHO gains, host baseline, hashes, ledger, claim ceiling, and f84r exclusion."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n")
    print(json.dumps(validation,sort_keys=True))
    if failures: raise SystemExit(1)


if __name__ == "__main__": main()
