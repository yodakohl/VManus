from pathlib import Path
import json, hashlib
D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
def main():
    plan = json.loads((D / "src/AUTHOR_PLAN.json").read_text())
    checks = {"input_" + str(i): hashlib.sha256((ROOT / v["path"]).read_bytes()).hexdigest() == v["sha256"] for i,v in enumerate(plan["source_inputs"])}
    checks["raw_counts"] = plan["raw_counts"] == {"IT2a":97,"ZL3b":95,"RF1b":96}
    checks["complete_scope"] = plan["scope_loci"] == ["f68r2.6", "f68r2.31"] + ["f89v1." + str(i) for i in range(13,21)]
    checks["no_new_access"] = plan["no_new_access"] is True
    checks["no_confirmation"] = plan["independent_confirmation_leaves"] == []
    manifest = json.loads((D / "experiment.json").read_text())
    checks["sealed"] = manifest["sealed_data"] == {"f84":"FORBIDDEN", "f84r":"FORBIDDEN"}
    result = {"status":"PASS" if all(checks.values()) else "FAIL", "checks": checks, "claim_ceiling":"Input identity and registered scope only; no semantic or account validation."}
    (D / "artifacts/VALIDATION.json").write_text(json.dumps(result,indent=2) + "\n")
    print(json.dumps({"status":result["status"],"checks":len(checks),"semantic_validation":False}))
    return int(not all(checks.values()))
if __name__ == "__main__":
    raise SystemExit(main())
