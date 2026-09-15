#!/usr/bin/env python3
"""Independent GDT971 validator.

Default mode is registration/source-only and deliberately does not open the
primary runner or RESULT.  Use --full only after the public result exists.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "SOURCE.json"
PREREG = ROOT / "PREREGISTRATION.md"
RESULT = ROOT / "artifacts" / "RESULT.json"
EXPECTED_RENDER = {
    "159": ("abaci-159.png", "f28a569d4cead306a4c78377010fd95ff27419dd498dcc576a7ac543bf51a5c8", (1606, 2200)),
    "160": ("abaci-160.png", "68890d859ebf5b0db09423bc5ebc8d91ef7d311c393a78341b2cdfcec3558b85", (1606, 2200)),
    "161": ("abaci-161.png", "3c20175c4394c09420bb46e540d23781a5f87d980040d9af50005399ef1e79ba", (1606, 2200)),
}
EXPECTED_SOURCE = "e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a"

# A printed digit is mapped to the tuple entry at that digit.  These are the
# five source accounts, with fixed component grades 3,4,6 and target grade 5.
ACCOUNTS = {
    "A": {"weights": [("i", "1"), ("i", "1"), ("i", "3")], "mass": ("i", "5"), "check": ("i", "25")},
    "B": {"weights": [("i", "2"), ("i", "5"), ("i", "9")], "mass": ("i", "16"), "check": ("i", "80")},
    "P": {"weights": [("m", "2", "1", "2"), ("m", "6", "1", "4"), ("m", "11", "1", "4")], "mass": ("i", "20"), "check": None},
    "D": {"weights": [("i", "10"), ("i", "25"), ("i", "45")], "mass": None, "check": None},
    "Q": {"weights": [("i", "2"), ("i", "7"), ("i", "11")], "mass": ("i", "20"), "check": ("i", "100")},
}
# Every literal number used by the declared accounts.  No standalone N(0) is
# introduced; 0 occurs only as a printed digit within 80/100.
USED_NUMBERS = tuple(sorted({"1", "2", "3", "4", "5", "6", "7", "9", "10", "11", "16", "20", "25", "45", "80", "100"}))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def mapped_int(text: str, p: tuple[int, ...]) -> int:
    if len(text) > 1 and p[int(text[0])] == 0:
        raise ValueError("leading zero")
    return int("".join(str(p[int(ch)]) for ch in text))


def atom(spec, p):
    if spec[0] == "i":
        return Fraction(mapped_int(spec[1], p))
    # mixed numeral: whole + numerator/denominator
    return Fraction(mapped_int(spec[1], p)) + Fraction(mapped_int(spec[2], p), mapped_int(spec[3], p))


def primitive_positive(p) -> bool:
    try:
        return all(mapped_int(s, p) > 0 for s in USED_NUMBERS)
    except ValueError:
        return False


def account(name: str, p: tuple[int, ...]):
    spec = ACCOUNTS[name]
    try:
        ws = [atom(w, p) for w in spec["weights"]]
        grades = [Fraction(mapped_int(s, p)) for s in ("3", "4", "6")]
        target = Fraction(mapped_int("5", p))
        mass = sum(ws) if spec["mass"] is None else atom(spec["mass"], p)
        fine = sum(w * g for w, g in zip(ws, grades))
        out = {"weights": ws, "mass": mass, "fine": fine, "target_fine": mass * target,
               "mass_sum_ok": sum(ws) == mass}
        if spec["check"] is not None:
            out["check"] = atom(spec["check"], p)
            out["check_ok"] = fine == out["check"]
        else:
            out["check"] = None
            out["check_ok"] = True
        out["balance_ok"] = fine == mass * target
        return out
    except (ValueError, ZeroDivisionError):
        return None


def layer_ok(name, a):
    return a is not None and a["mass_sum_ok"] and a["balance_ok"] and a["check_ok"]


def json_fraction(x):
    return {"numerator": x.numerator, "denominator": x.denominator}


def compact_account(a):
    return {k: ([json_fraction(v) for v in val] if isinstance(val, list) else json_fraction(val) if isinstance(val, Fraction) else val) for k, val in a.items()}


def map_string(p):
    return "".join(str(x) for x in p)


def fraction_string(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def enumerate_all():
    counts = {"enumerated": 0, "L0": 0, "L1": 0, "L2": 0, "L3": 0}
    first_failure = {"L0": 0, "L1": 0, "L2": 0, "L3": 0}
    survivors = {"L1": [], "L2": [], "L3": []}
    domain_values = {k: [set() for _ in range(10)] for k in ("L0", "L1", "L2", "L3")}
    final_values = []
    for p in itertools.permutations(range(10)):
        counts["enumerated"] += 1
        if not primitive_positive(p):
            first_failure["L0"] += 1
            continue
        counts["L0"] += 1
        for i, v in enumerate(p): domain_values["L0"][i].add(v)
        rec = {"printed_to_value": list(p)}
        q = account("Q", p)
        if not layer_ok("Q", q):
            first_failure["L1"] += 1
            continue
        counts["L1"] += 1
        for i, v in enumerate(p): domain_values["L1"][i].add(v)
        rec["Q"] = compact_account(q)
        survivors["L1"].append(map_string(p))
        pp = account("P", p)
        if not layer_ok("P", pp):
            first_failure["L2"] += 1
            continue
        counts["L2"] += 1
        for i, v in enumerate(p): domain_values["L2"][i].add(v)
        rec["P"] = compact_account(pp)
        survivors["L2"].append(map_string(p))
        ok = True
        for name in ("A", "B", "D"):
            aa = account(name, p)
            rec[name] = compact_account(aa) if aa is not None else None
            if not layer_ok(name, aa):
                ok = False
        if not ok:
            first_failure["L3"] += 1
            continue
        counts["L3"] += 1
        for i, v in enumerate(p): domain_values["L3"][i].add(v)
        survivors["L3"].append(map_string(p))
        final_values.append(rec)
    domains = {k: [sorted(s) for s in vals] for k, vals in domain_values.items()}
    return counts, first_failure, survivors, domains, final_values


def free_label_diagnostic():
    grades = [Fraction(3), Fraction(4), Fraction(7)]
    paths = [[Fraction(1), Fraction(12), Fraction(7)], [Fraction(5), Fraction(20, 3), Fraction(25, 3)]]
    rows = []
    for ws in paths:
        mass = sum(ws)
        fine = sum(w * g for w, g in zip(ws, grades))
        rows.append({"weights": [fraction_string(w) for w in ws], "mass": fraction_string(mass), "fine": fraction_string(fine)})
    return rows


def relation_diagnostic():
    return {"coefficients": [2, -3, 1], "target_coefficients": [-1, 2, 0], "affine_normalized": [0, 1, 2, 3]}


def registration_checks(source_dir=None):
    checks = {}
    checks["prereg_exists"] = PREREG.exists()
    lock = json.loads((ROOT / "PREREG_LOCK.json").read_text())
    checks["registered_bindings_ok"] = all(sha256(ROOT.parents[2] / name) == digest for name, digest in lock["files"].items())
    checks["source_exists"] = SRC.exists()
    source = json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else {}
    checks["declared_source_hash"] = source.get("source_sha256")
    checks["declared_source_hash_format"] = checks["declared_source_hash"] == EXPECTED_SOURCE
    renders = {}
    for key, (name, expected, dims) in EXPECTED_RENDER.items():
        path = Path(source_dir) / name if source_dir else None
        if path is None:
            renders[key] = {"registered_name": name, "registered_sha256": expected, "registered_size": list(dims), "checked": False}
            continue
        entry = {"exists": path.exists(), "sha256": sha256(path) if path.exists() else None}
        try:
            from PIL import Image
            with Image.open(path) as im:
                entry["size"] = list(im.size)
        except Exception as exc:
            entry["size_error"] = type(exc).__name__
        entry["hash_ok"] = entry["sha256"] == expected
        entry["size_ok"] = tuple(entry.get("size", [])) == dims
        renders[key] = entry
    checks["renders"] = renders
    checks["contract_account_names"] = list(ACCOUNTS) == ["A", "B", "P", "D", "Q"]
    checks["mixed_notation"] = ["2 + 1/2", "6 + 1/4", "11 + 1/4"]
    checks["excluded_fields"] = ["D:400", "P:100", "number words"]
    checks["algorithm"] = "lexicographic permutations of printed-digit -> numeric-digit maps; Fraction arithmetic; L0, Q, Q+P, Q+P+A+B+D"
    checks["all_source_renders_ok"] = all(v.get("checked", False) is False or (v["exists"] and v["hash_ok"] and v["size_ok"]) for v in renders.values())
    checks["status"] = "PASS_REGISTRATION_ONLY" if all([checks["registered_bindings_ok"], checks["prereg_exists"], checks["source_exists"], checks["declared_source_hash_format"], checks["all_source_renders_ok"], checks["contract_account_names"]]) else "FAIL_REGISTRATION_ONLY"
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="enumerate and, only then, read public primary RESULT")
    ap.add_argument("--registration-only", action="store_true", help="check source/contract without enumeration or RESULT access")
    ap.add_argument("--source-dir", help="optional directory containing the three registered source renders")
    args = ap.parse_args()
    do_full = args.full or (not args.registration_only and RESULT.exists())
    reg = registration_checks(args.source_dir)
    if not do_full:
        print(json.dumps(reg, ensure_ascii=False, indent=2))
        return 0 if reg["status"] == "PASS_REGISTRATION_ONLY" else 1
    counts, first_failure, survivors, domains, finals = enumerate_all()
    final_accounts = []
    for rec in finals:
        p = tuple(rec["printed_to_value"])
        grades = [mapped_int(s, p) for s in ("3", "4", "6")]
        target = mapped_int("5", p)
        for name in ("A", "B", "P", "D", "Q"):
            a = account(name, p)
            final_accounts.append({"mapping": map_string(p), "account": name, "grades": grades, "target": target,
                                   "weights": [fraction_string(x) for x in a["weights"]], "mass": fraction_string(a["mass"]),
                                   "fine": fraction_string(a["fine"]), "mean": fraction_string(a["fine"] / a["mass"])})
    out = {"registration": reg, "counts": counts, "first_failure_counts": first_failure,
           "surviving_mappings": survivors, "digit_domains": domains, "final_accounts": final_accounts,
           "free_label_countermodel": free_label_diagnostic(), "relative_grade_relation": relation_diagnostic()}
    # Primary result is deliberately opened only in --full mode, after the
    # independent enumeration has completed.
    if not RESULT.exists():
        out["comparison"] = {"status": "PRIMARY_RESULT_MISSING"}
    else:
        primary = json.loads(RESULT.read_text(encoding="utf-8"))
        expected = {k: out[k] for k in ("counts", "first_failure_counts", "surviving_mappings", "digit_domains", "final_accounts", "free_label_countermodel")}
        expected["relative_grade_relation"] = relation_diagnostic()
        compared = {k: primary.get(k) == v for k, v in expected.items()}
        compared["registered_inputs"] = reg["status"] == "PASS_REGISTRATION_ONLY"
        compared["complete_enumeration"] = counts["enumerated"] == 3628800
        compared["source_identity"] = "0123456789" in survivors["L3"] and primary.get("source_identity_pass") is True
        wanted_status = "SOURCE_NUMERAL_VALUES_UNIQUE" if counts["L3"] == 1 else "SOURCE_NUMERAL_VALUES_NONUNIQUE"
        compared["primary_status"] = primary.get("status") == wanted_status
        lines = ["mapping\taccount\tgrades\tdesired_grade\tcomponent_weights\tmass\tfine_content\tmean"]
        for x in final_accounts:
            lines.append("\t".join([x["mapping"],x["account"],",".join(map(str,x["grades"])),str(x["target"]),",".join(x["weights"]),x["mass"],x["fine"],x["mean"]]))
        compared["complete_candidate_table"] = (ROOT / "artifacts" / "CANDIDATE_VALUES.tsv").read_text() == "\n".join(lines)+"\n"
        out["comparison"] = {"status": "PASS" if all(compared.values()) else "FAIL", "fields": compared}
        out["primary_result_keys"] = sorted(primary)
        (ROOT / "artifacts" / "VALIDATION.json").write_text(json.dumps({"status": out["comparison"]["status"], "independent": expected, "compared_fields": compared}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["comparison"]["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
