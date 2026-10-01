from pathlib import Path
import json, hashlib
D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
def main():
    plan = json.loads((D / "src/AUTHOR_PLAN.json").read_text())
    checks = {"input_" + str(i): hashlib.sha256((ROOT / v["path"]).read_bytes()).hexdigest() == v["sha256"] for i,v in enumerate(plan["source_inputs"])}
    source = json.loads((D / "src/SOURCE.json").read_text())
    rows = source["rows"]
    checks["counts"] = {e:sum(r["edition"]==e for r in rows) for e in plan["raw_counts"]} == plan["raw_counts"]
    checks["native_fields"] = all(set(r)==set(plan["columns"]) for r in rows)
    checks["scope"] = sorted(set(r["locus"] for r in rows)) == sorted(plan["scope_loci"])
    checks["unique_native_keys"] = len({(r["edition"],r["source_group_id"]) for r in rows}) == len(rows)
    checks["primary_counts"] = all(sum(r["edition"]==e and r["block"]==b for r in rows)==n for e in plan["raw_counts"] for b,n in [("N",19),("E",27)])
    checks["no_new_access"] = plan["no_new_access"] and source["prior_exposure"] and not plan["independent_confirmation_leaves"]
    hist = json.loads((D / "src/HISTORICAL_RECEIPT.json").read_text())
    checks["historical_bytes"] = hashlib.sha256((D / "src/HISTORICAL_PRIMARY.html").read_bytes()).hexdigest()==hist["sha256"]
    m = json.loads((D / "experiment.json").read_text())
    checks["sealed"] = m["sealed_data"] == {"f84":"FORBIDDEN", "f84r":"FORBIDDEN"}
    result = {"status":"PASS" if all(checks.values()) else "FAIL", "checks":checks, "claim_ceiling":"Registered input identity and scope only; neither semantic nor account validation."}
    (D / "artifacts/VALIDATION.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"], "checks":len(checks), "semantic_validation":False}))
    return int(not all(checks.values()))
if __name__ == "__main__":
    raise SystemExit(main())
