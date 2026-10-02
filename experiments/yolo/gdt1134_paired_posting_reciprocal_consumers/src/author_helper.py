"""Frozen GDT1134 declarative-entry / actual-mark author accounting.

Reads only source and author-owned inventory. It does not post Ledger entries.
Each run is a finite application of frozen whole values, never a decoder.
"""
from pathlib import Path
from copy import deepcopy
import collections
import datetime
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]


def world(roles=("A", "B")):
    # Hypothetical background assertions, separate from written FRAME/ENTRY_CERT.
    return {"roles": list(roles), "transaction": "T", "value": "V", "date": "D",
            "entries": [{"id": "external-entry-" + r, "transaction": "T", "role": r,
                         "value": "V", "date": "D", "ledger": "L", "completed": True}
                        for r in roles]}


def evaluate(native, fixed, dictionary, background, intervention=None):
    intervention = intervention or {}
    ctx = {"marks": [], "certs": [], "props": [], "counters": [], "reads": []}
    objects, rows = {}, []
    stopped = None
    shared_done = {"value": True}

    def make(row, typ, value, **links):
        oid = row["source_group_id"] + "#" + str(len(row["returns"]) + 1)
        obj = {"id": oid, "type": typ, "value": value, **links}
        objects[oid] = obj
        row["returns"].append(oid)
        return (obj, row["source_group_id"])

    def arg(row, handle):
        if handle is None:
            raise ValueError("MISSING_ACTUAL_WRITTEN_RETURN")
        obj, source_id = handle
        row["arguments"].append({"value_id": obj["id"], "type": obj["type"],
                                 "from_return_source_id": source_id})
        return obj

    def returned(row, handle):
        obj = arg(row, handle)
        row["returns"].append(obj["id"])
        return obj, row["source_group_id"]

    def need(key):
        if key not in ctx:
            raise ValueError("MISSING_" + key.upper())
        return ctx[key]

    def proposition(row, kind, inputs, truth, text):
        for h in inputs:
            arg(row, h)
        p = make(row, "Proposition", {"kind": kind, "truth": truth, "text": text},
                 inputs=[h[0] for h in inputs])
        ctx["props"].append(p)
        row["world_statement"] = text
        row["statement_truth"] = truth
        return p

    def collect(row, handles):
        if len(handles) != 2:
            raise ValueError("MISSING_TWO_ACTUAL_RETURNS")
        members = [arg(row, h) for h in handles]
        return make(row, "Collection", {"member_ids": [o["id"] for o in members]},
                    members=members, member_sources=[h[1] for h in handles])

    def check_certificate(row, handle):
        cert = arg(row, handle)
        f = arg(row, need("frame"))
        e = cert["entry"]
        valid = (any(x is e for x in background["entries"]) and e["completed"]
                 and e["transaction"] == f["value"]["transaction"]
                 and e["role"] == cert["role"]["value"]["label"])
        return proposition(row, "ENTRY_CERTIFICATE", [handle], valid,
                           "The supplied completed Ledger record for " + e["role"]
                           + " belongs to T; this is certification, not a new posting.")

    def counter(row, function_handle, selector_handle):
        op = arg(row, function_handle)
        sel = arg(row, selector_handle)
        f = arg(row, need("frame"))
        if op["value"]["operation"] != "COUNTER":
            raise ValueError("WRONG_FROZEN_COUNTER_CALLABLE")
        if sel["transaction"] is not f:
            raise ValueError("COUNTER_TRANSACTION_MISMATCH")
        origin = sel["role"]
        if not any(origin is r for r in f["roles"]):
            raise ValueError("COUNTER_SOURCE_ROLE_NOT_IN_WRITTEN_FRAME")
        other = next(r for r in f["roles"] if r is not origin)
        c = make(row, "CounterResult", {"source_role": origin["value"]["label"],
                                       "returned_role": other["value"]["label"],
                                       "transaction": f["value"]["transaction"]},
                 transaction=f, source_role=origin, returned_role=other,
                 origin_mark=sel["mark"], selector=sel)
        # Explicit counterfactual output changes, never a baseline role map.
        if intervention.get("wrong_counter") == len(ctx["counters"]) + 1:
            if intervention.get("wrong_kind") == "transaction":
                c[0]["transaction"] = {"id": "external-T2", "value": {"transaction": "T2"}}
                c[0]["value"]["transaction"] = "T2"
            else:
                c[0]["returned_role"] = {"id": "external-X", "type": "AccountRole",
                                            "value": {"label": "X"}}
                c[0]["value"]["returned_role"] = "X"
        ctx["counters"].append(c)
        if "collect_counter_pending" in ctx:
            first, collection_row = ctx.pop("collect_counter_pending")
            pair = collect(collection_row, [first, c])
            ctx["counter_pair"] = pair
            collection_row["completed_at_source_id"] = row["source_group_id"]
        return c

    def project(row, collection_handle, ordinal):
        coll = arg(row, collection_handle)
        if coll["type"] != "Collection" or len(coll["members"]) != 2:
            raise ValueError("MISSING_FIXED_TWO_MEMBER_COLLECTION")
        # Literal actual returned object; no copy/rebuilt account dictionary.
        obj = coll["members"][ordinal]
        row["returns"].append(obj["id"])
        return obj, row["source_group_id"]

    for n in native:
        raw = n["ivtff_group_raw"]
        d = dictionary.get(raw)
        row = dict(n, fixed_units=deepcopy(fixed[n["source_group_id"]]),
                   entry_id=d["entry_id"] if d else None,
                   interpretation=d["meaning"] if d else None,
                   status="ACCOUNTED" if d else "UNKNOWN", arguments=[], returns=[],
                   consumer_source_ids=[], errors=[], world_statement=None,
                   cost=d["cost"] if d else {"unresolved_exact_whole": 1})
        rows.append(row)
        if stopped:
            row["status"] = "UNEXECUTED_AFTER_BARRIER" if d else "UNKNOWN_UNEXECUTED"
            row["first_barrier"] = stopped
            continue
        if d is None:
            row["errors"] = ["UNASSIGNED_LITERAL_NO_NORMALIZATION_OR_CARRY"]
            stopped = n["source_group_id"]
            continue
        op = d["rule"]
        try:
            if op == "FRAME":
                labels = background["roles"]
                if len(labels) != 2 or labels[0] == labels[1]:
                    raise ValueError("FRAME_REQUIRES_TWO_DISTINCT_WRITTEN_ROLES")
                roles = [make(row, "AccountRole", {"label": x, "ordinal": i})[0]
                         for i, x in enumerate(labels)]
                ctx["frame"] = make(row, "Frame", {"transaction": background["transaction"],
                                      "value": background["value"], "date": background["date"],
                                      "journal": "J", "ledger": "L"}, roles=roles)
                for r in roles:
                    row["arguments"].append({"value_id": r["id"], "type": r["type"],
                                             "from_return_source_id": row["source_group_id"]})
                row["world_statement"] = "For transaction T introduce ordered distinct roles, Journal J and Ledger L, and uninterpreted common V/D; no transfer or marking has occurred in this program yet."
            elif op in ("ENTRY_FIRST_FIELD", "ENTRY_LAST_FIELD"):
                f = arg(row, need("frame"))
                role = f["roles"][0 if op == "ENTRY_FIRST_FIELD" else -1]
                matches = [e for e in background["entries"] if e["transaction"] == f["value"]["transaction"]
                           and e["role"] == role["value"]["label"] and e["value"] == f["value"]["value"]
                           and e["date"] == f["value"]["date"] and e["ledger"] == "L" and e["completed"]]
                if len(matches) != 1:
                    raise ValueError("MISSING_OR_AMBIGUOUS_PREEXISTING_LEDGER_RECORD")
                cert = make(row, "EntryCertificate", {"entry_id": matches[0]["id"],
                              "role": role["value"]["label"], "transaction": f["value"]["transaction"]},
                            entry=matches[0], transaction=f, role=role)
                ctx["certs"].append(cert)
                ctx["field"] = make(row, "PostingField", cert[0]["value"].copy(),
                                   certificate=arg(row, cert), role=role, transaction=f)
                row["background_inputs"] = [deepcopy(matches[0])]
                row["world_statement"] = "Certify the already completed Ledger transfer for this actual role and expose its marking field."
            elif op == "MARK":
                if intervention.get("remove_mark") == len(ctx["marks"]) + 1:
                    row["status"] = "OMITTED_MARK_COUNTERFACTUAL"
                    intervention["remove_mark"] = None
                    continue
                field = arg(row, need("field"))
                f = arg(row, need("frame"))
                cert = field["certificate"]
                if field["transaction"] is not f or not any(e is cert["entry"] for e in background["entries"]):
                    raise ValueError("MARK_HAS_NO_ACTUAL_LEDGER_ENTRY_DEPENDENCY")
                if not cert["entry"]["completed"]:
                    raise ValueError("MARK_REQUIRES_COMPLETED_LEDGER_RECORD")
                value = True
                mark = make(row, "JournalMark", {"transaction": f["value"]["transaction"],
                                  "owner": field["role"]["value"]["label"], "recorded_completed": value},
                            transaction=f, owner=field["role"], certificate=cert,
                            recorded_completed=value)
                if intervention.get("status_representation") == "shared_DONE":
                    mark[0]["shared_status"] = shared_done
                elif intervention.get("status_representation") == "shared_SCALAR":
                    mark[0]["shared_status"] = {"value": background["value"]}
                ctx["marks"].append(mark)
                if intervention.get("false_mark") == len(ctx["marks"]):
                    mark[0]["recorded_completed"] = False
                    mark[0]["value"]["recorded_completed"] = False
                    if "shared_status" in mark[0] and intervention.get("status_representation") == "shared_DONE":
                        mark[0]["shared_status"]["value"] = False
                row["world_statement"] = "Write the Journal's distinct recorded-completion mark for this certified role; create no Ledger entry."
            elif op in ("CHECK_FIRST_CERT", "CHECK_LAST_CERT"):
                if not ctx["certs"]:
                    raise ValueError("MISSING_ENTRY_CERTIFICATE")
                check_certificate(row, ctx["certs"][0 if op == "CHECK_FIRST_CERT" else -1])
            elif op == "COLLECT_CERT_PROPS":
                pair = collect(row, ctx["props"][-2:])
                ctx["cert_props"] = pair
            elif op == "CHECK_CERT_PAIR":
                coll = arg(row, need("cert_props"))
                certs = [prop["inputs"][0] for prop in coll["members"]]
                f = arg(row, need("frame"))
                truth = (len({x["role"]["id"] for x in certs}) == 2
                         and all(x["transaction"] is f for x in certs)
                         and all(x["entry"]["value"] == f["value"]["value"]
                                 and x["entry"]["date"] == f["value"]["date"] for x in certs))
                proposition(row, "CERTIFICATE_PAIR", [need("cert_props")], truth,
                            "The two actual entry certificates retain distinct owners and common T/V/D.")
            elif op == "ASSERT_LAST_PROP":
                if not ctx["props"]:
                    raise ValueError("MISSING_PROPOSITION_TO_ASSERT")
                prev = ctx["props"][-1]
                proposition(row, "ASSERTION", [prev], prev[0]["value"]["truth"],
                            "Retain the actual tested content: " + prev[0]["value"]["text"])
            elif op == "COUNTER_PREFIX":
                if "counter_function" in ctx:
                    raise ValueError("COUNTER_FUNCTION_MISSING_PREVIOUS_RIGHT_ARGUMENT")
                ctx["counter_function"] = make(row, "CounterFunction", {"operation": "COUNTER"})
                row["status"] = "AWAITING_WRITTEN_RIGHT_ARGUMENT"
            elif op in ("SELECT_FIRST_MARK_ROLE", "SELECT_LAST_MARK_ROLE"):
                if not ctx["marks"]:
                    raise ValueError("MISSING_ACTUAL_MARK_OUTPUT_FOR_ROLE_SELECTION")
                ordinal = 0 if op == "SELECT_FIRST_MARK_ROLE" else -1
                if intervention.get("swap_first_selector") and ordinal == 0:
                    ordinal = -1
                mh = ctx["marks"][ordinal]
                mark = arg(row, mh)
                f = arg(row, need("frame"))
                owner = mark["owner"]
                if intervention.get("unrelated_selector") and op == "SELECT_FIRST_MARK_ROLE":
                    owner = {"id": "external-X", "type": "AccountRole", "value": {"label": "X"}}
                selection = make(row, "RoleSelection", {"owner": owner["value"]["label"],
                                  "transaction": f["value"]["transaction"], "origin_mark_id": mark["id"]},
                                 role=owner, mark=mark, transaction=mark["transaction"])
                fn = need("counter_function")
                del ctx["counter_function"]
                counter(row, fn, selection)
                prefix_row = next(r for r in rows if r["source_group_id"] == fn[1])
                prefix_row["completed_at_source_id"] = row["source_group_id"]
                prefix_row["status"] = "ACCOUNTED"
            elif op == "COLLECT_COUNTER_INFIX":
                if not ctx["counters"]:
                    raise ValueError("MISSING_FIRST_ACTUAL_COUNTER_RESULT")
                ctx["collect_counter_pending"] = (ctx["counters"][-1], row)
                row["status"] = "AWAITING_NEXT_COUNTER_RESULT"
            elif op == "CHECK_COUNTER_PAIR":
                coll = arg(row, need("counter_pair"))
                f = arg(row, need("frame"))
                cs = coll["members"]
                if not all(c["transaction"] is f for c in cs):
                    raise ValueError("COUNTER_PAIR_TRANSACTION_MISMATCH")
                if not all(any(c["source_role"] is a and c["returned_role"] is b and a is not b
                               for a in f["roles"] for b in f["roles"])
                           and c["origin_mark"]["owner"] is c["source_role"] for c in cs):
                    raise ValueError("COUNTER_PAIR_OPPOSITE_OWNER_OR_ORIGIN_MISMATCH")
                if len({c["returned_role"]["id"] for c in cs}) != 2:
                    raise ValueError("MISSING_TWO_DISTINCT_COUNTERACCOUNTS")
                proposition(row, "COUNTER_PAIR", [need("counter_pair")], True,
                            "The two actual counterreturns retain T and distinct opposite owners with their original mark origins.")
            elif op in ("PROJECT_FIRST_COUNTER", "PROJECT_LAST_COUNTER"):
                ctx["projected_counter"] = project(row, need("counter_pair"),
                                                     0 if op == "PROJECT_FIRST_COUNTER" else -1)
            elif op == "READ_RETURNED_MARK":
                counter_obj = arg(row, need("projected_counter"))
                f = arg(row, need("frame"))
                if counter_obj["transaction"] is not f:
                    raise ValueError("READ_COUNTER_TRANSACTION_MISMATCH")
                owner = counter_obj["returned_role"]
                if not any(owner is x for x in f["roles"]):
                    raise ValueError("READ_RETURNED_OWNER_NOT_IN_FRAME")
                matches = [h for h in ctx["marks"] if h[0]["owner"] is owner
                           and h[0]["transaction"] is counter_obj["transaction"]]
                if len(matches) != 1:
                    raise ValueError("MISSING_OR_AMBIGUOUS_ACTUAL_RETURNED_OWNER_MARK")
                mark = arg(row, matches[0])
                value = mark.get("shared_status", {}).get("value", mark["recorded_completed"])
                read = make(row, "MarkRead", {"transaction": f["value"]["transaction"],
                            "owner": owner["value"]["label"], "mark_id": mark["id"],
                            "counter_result_id": counter_obj["id"], "recorded_completed": value},
                            transaction=f, owner=owner, mark=mark, counter=counter_obj)
                ctx["reads"].append(read)
                row["world_statement"] = "Read " + str(value) + " from the actual retained mark owned by returned account " + owner["value"]["label"] + "."
            elif op == "COLLECT_MARK_READS":
                ctx["read_pair"] = collect(row, ctx["reads"][-2:])
            elif op == "CHECK_READ_PAIR":
                coll = arg(row, need("read_pair"))
                values = [x["value"]["recorded_completed"] for x in coll["members"]]
                same = all(x["transaction"] is ctx["frame"][0] for x in coll["members"])
                distinct = len({x["owner"]["id"] for x in coll["members"]}) == 2
                certified = arg(row, need("cert_props"))
                prior_certs = [prop["inputs"][0] for prop in certified["members"]]
                source_dependencies = all(any(read["mark"]["certificate"] is cert
                                               for cert in prior_certs) for read in coll["members"])
                same = same and source_dependencies
                truth = all(values) and same and distinct if all(type(x) is bool for x in values) else None
                proposition(row, "RECORDED_COMPLETION_PAIR", [need("read_pair"), need("cert_props")], truth,
                            "Returned-owner recorded statuses are " + str(values) + "; common T and distinct owners: " + str(same and distinct) + ".")
                if truth is None:
                    raise ValueError("MISSING_SCALAR_TO_COMPLETION_FUNCTION")
            elif op == "REFERENCE_READ_PAIR":
                ctx["referred_reads"] = returned(row, need("read_pair"))
            elif op in ("PROJECT_FIRST_READ", "PROJECT_LAST_READ"):
                h = project(row, need("referred_reads"), 0 if op == "PROJECT_FIRST_READ" else -1)
                ctx.setdefault("final_reads", []).append(h)
            elif op == "COLLECT_ASSERT_READS":
                pair = collect(row, ctx.get("final_reads", [])[-2:])
                reads = pair[0]["members"]
                values = [x["value"]["recorded_completed"] for x in reads]
                truth = all(values) if all(type(x) is bool for x in values) else None
                ctx["terminal"] = proposition(row, "TERMINAL_OWNER_MARKS", [pair], truth,
                            "Retain the separate actual returned-owner Journal mark reads " + str(values) + "; this is recorded copying completion, not payment or settlement.")
            else:
                raise ValueError("UNIMPLEMENTED_FROZEN_RULE:" + op)
            if row["status"] == "AWAITING_NEXT_COUNTER_RESULT" and "completed_at_source_id" in row:
                row["status"] = "ACCOUNTED"
        except ValueError as error:
            row["status"] = "BLOCKED"
            row["errors"].append(str(error))
            stopped = row["source_group_id"]
    for row in rows:
        if row["status"] == "AWAITING_NEXT_COUNTER_RESULT" and "completed_at_source_id" in row:
            row["status"] = "ACCOUNTED"
    for row in rows:
        consumers = [r["source_group_id"] for r in rows for a in r["arguments"]
                     if a["from_return_source_id"] == row["source_group_id"]]
        row["consumer_source_ids"] = sorted(set(consumers), key=lambda x: next(i for i, r in enumerate(rows) if r["source_group_id"] == x))
    def snapshot(o):
        links = {k: ([x["id"] for x in v] if isinstance(v, list) else v["id"])
                 for k, v in o.items() if k not in ("id", "type", "value", "shared_status")
                 and ((isinstance(v, dict) and "id" in v) or (isinstance(v, list) and all(isinstance(x, dict) and "id" in x for x in v)))}
        return {"id": o["id"], "type": o["type"], "value": deepcopy(o["value"]), "actual_object_links": links}
    terminal = ctx.get("terminal")
    return {"status": "COMPLETE_C0" if stopped is None and terminal else "PARTIAL_OR_CONTRADICTED_FIXED_ACCOUNT",
            "first_barrier": stopped, "rows": rows,
            "objects": {oid: snapshot(o) for oid, o in objects.items()},
            "read_values": [h[0]["value"] for h in ctx["reads"]],
            "terminal": snapshot(terminal[0]) if terminal else None,
            "background_world": deepcopy(background),
            "no_ledger_entries_created": True,
            "intervention": deepcopy(intervention),
            "initial_entry_count": len(background["entries"]),
            "final_entry_count": len(background["entries"])}


def main():
    ext = json.loads((BASE / "src/EXTENSIONS.json").read_text())
    src = json.loads((BASE / "src/SOURCE.json").read_text())
    assert hashlib.sha256((BASE / "src/CORE.json").read_bytes()).hexdigest() == ext["core_sha256"]
    assert hashlib.sha256((BASE / "src/SOURCE.json").read_bytes()).hexdigest() == ext["source_sha256"]
    for name in ("AUTHOR_ACCOUNT.json", "AUTHOR_READING.md", "FINAL_FREEZE_RECEIPT.json"):
        if (BASE / "artifacts" / name).exists():
            raise SystemExit("Existing final author freeze preserved: " + name)
    fixed = {sid: c["fixed_units"] for line in src["lines"] for c in line["chunks"] for sid in c["source_ids"]}
    dictionary = {d["raw_form"]: d for d in ext["dictionary"]}
    accounts = {}
    for edition in ("IT2a", "ZL3b", "RF1b"):
        native = [r for r in src["native_rows"] if r["edition"] == edition]
        accounts[edition] = evaluate(native, fixed, dictionary, world())
    it = [r for r in src["native_rows"] if r["edition"] == "IT2a"]
    fixtures = []
    for name, change in [("FALSE_FIRST_MARK", {"false_mark": 1}),
                         ("FALSE_LAST_MARK", {"false_mark": 2}),
                         ("REMOVE_FIRST_MARK", {"remove_mark": 1}),
                         ("REMOVE_LAST_MARK", {"remove_mark": 2}),
                         ("UNRELATED_SAME_VALUE_SELECTOR", {"unrelated_selector": True}),
                         ("PARTIAL_SELECTOR_SWAP", {"swap_first_selector": True}),
                         ("WRONG_RETURNED_OWNER", {"wrong_counter": 1, "wrong_kind": "owner"}),
                         ("WRONG_RETURNED_TRANSACTION", {"wrong_counter": 1, "wrong_kind": "transaction"}),
                         ("COMMON_DONE_FALSE_FIRST", {"status_representation": "shared_DONE", "false_mark": 1}),
                         ("COMMON_SCALAR", {"status_representation": "shared_SCALAR"})]:
        out = evaluate(it, fixed, dictionary, world(), change)
        fixtures.append({"name": name, "engineering_or_declared_counterfactual_only": True,
                         "status": out["status"], "first_barrier": out["first_barrier"],
                         "read_values": out["read_values"], "terminal": out["terminal"],
                         "failed_row": next((r for r in out["rows"] if r["errors"]), None),
                         "entry_count": out["final_entry_count"]})
    for ordinal in (0, 1):
        w = world()
        deleted = w["entries"].pop(ordinal)
        out = evaluate(it, fixed, dictionary, w)
        fixtures.append({"name": "DELETE_ACTUAL_LEDGER_ENTRY_" + str(ordinal + 1),
                         "question": "Declarative certificate-dependency failure; no physical posting event was performed.",
                         "deleted_background_record": deleted, "status": out["status"],
                         "first_barrier": out["first_barrier"],
                         "failed_row": next(r for r in out["rows"] if r["errors"]),
                         "entry_count": out["final_entry_count"], "ledger_entry_invented": False})
    swapped = evaluate(it, fixed, dictionary, world(("B", "A")))
    fixtures.append({"name": "GLOBAL_ROLE_LABEL_RENAMING", "status": swapped["status"],
                     "read_values": swapped["read_values"], "terminal": swapped["terminal"],
                     "interpretation": "All role identities, entries and labels renamed consistently; no cardinal orientation selected."})
    # Internal required scientific conservation checks before final receipt.
    assert accounts["IT2a"]["status"] == "COMPLETE_C0"
    for e, a in accounts.items():
        original = [r for r in src["native_rows"] if r["edition"] == e]
        assert [{k: r[k] for k in src["native_columns"]} for r in a["rows"]] == original
        assert len(a["rows"]) == 30
    vals = {f["name"]: [r["recorded_completed"] for r in f["read_values"]] for f in fixtures if "read_values" in f}
    assert vals["FALSE_FIRST_MARK"] == [True, False]
    assert vals["FALSE_LAST_MARK"] == [False, True]
    assert vals["COMMON_DONE_FALSE_FIRST"] == [False, False]
    assert swapped["status"] == "COMPLETE_C0"
    # Release metadata typo is disclosed; frozen EXTENSIONS bytes are preserved.
    public = json.loads((BASE / "artifacts/PUBLIC_REGISTRATION.json").read_text())
    result = {"experiment": "GDT1134", "status": "IT_COMPLETE_CONDITIONAL_C0_ZL_RF_PARTIAL",
              "freeze_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "accounts": accounts, "all_native_rows": 90, "fixed_source_lines": src["lines"],
              "core_sha256": ext["core_sha256"],
              "extensions_sha256": hashlib.sha256((BASE / "src/EXTENSIONS.json").read_bytes()).hexdigest(),
              "source_sha256": ext["source_sha256"], "public_registration": public,
              "frozen_metadata_typo": {"field": "EXTENSIONS.public_go_commit", "bad_literal": ext["public_go_commit"],
                                       "meaning": "Accidental source-hash suffix appended; actual immutable public release is the separate PUBLIC_REGISTRATION packet. No scientific rule changed."},
              "cost_inventory": ext, "counterfactuals": fixtures,
              "rival_limits": ["Strict common-DONE status loses the mixed false/true result while retaining all current role interfaces; a wider numeric bit-code can preserve it with extra rules.",
                               "Shared scalar V alone supplies no completion function; missing that interface is partial, not a refutation of numerical meaning.",
                               "Two scalars plus separate role/status relations, and a copied content/reference implementation, remain legitimate unrestricted rivals."],
              "confirmation_capacity": 0, "confirmed_translated_words": 0,
              "new_target_access": False, "physical_ledger_posting_performed": False}
    ap = BASE / "artifacts/AUTHOR_ACCOUNT.json"
    ap.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    text = ["# GDT1134 single-author paired recorded-posting account", "",
            "IT: complete conditional C0 for all30 raw groups. ZL/RF: partial at native .5G008; their remaining rows and fixed representations are preserved, not silently executed. Zero confirmed meanings and independent confirmation.", "",
            "Connected IT reading: For transaction T, introduce two distinct ordered account roles, a Journal and Ledger, and a shared unspecified value/date. Certify the supplied completed Ledger transfer for the first role and write its Journal completion mark; certify the supplied completed Ledger transfer for the other role and write its separate mark. Retain both entry certificates, their common transaction/date/value and distinct owners. Reassert those entry obligations. Take the account owner from the first actual written mark and obtain its opposite account under this frame; then take the account owner from the last actual written mark and obtain its opposite. Keep both returned accounts and their mark origins. Check that they retain one transaction and opposite distinct owners. Read the actual earlier mark owned by each returned account. Collect these two reads, state their respective recorded statuses, retain this very collection, return each of its two members and state their separate recorded-completion values together.", "",
            "No physical Ledger posting is executed: two preexisting completed-transfer facts are disclosed background inputs and are charged separately from the written certificates. The first word supplies only transaction/frame/role/value/date structure. The marking function checks the actual certificate/entry dependency and never invents an entry. Two Journal marks record copying completion; they do not certify payment, settlement or correct historical amounts. V/D are uninterpreted metadata, not40 or a named date.", "",
            "Live dataflow: MARK outputs at .5G003/.5G005 feed role selectors aiin/ar at .6G005/.6G008. The same COUNTER callable stored at both dar sites returns the actual opposite frame-role object, keeping its original selected mark. al collects those actual returned objects. otedy/ytaiin return those very members. The two actual owner-mark reads occur at oteody(.6G011) and g(.6G013), with the CounterResult returned by the immediately preceding projection as their input. Neither read substitutes A/B or a global DONE. ycheeo and the complete .7 continuation consume both actual MarkRead values, finishing with lchedr's collection and terminal assertion.", "",
            "All primitive and reference/whole/scope licenses were frozen before the first complete derivation. The core has12 families and7 opaque constants; the extension has28 paid exact whole values, two explicit prefix/collection syntax rules and paid selectors/aliases. Every fixed ordered formal unit is preserved. Meanings are exact-whole assignments with separately counted formal-unit residuals; no productive prefix, universal daiin predicate, transparent null part or inherited gloss is claimed. dar remains the one paid atomic lexicalized COUNTER operator. opchedaiin is separately priced rather than assigned a free daN rule. Repeated certificate assertions are deliberate redundant terminal propositions, not concealed dead words.", "",
            "Counterfactuals: changing only the first stored mark produces read values[True,False]; changing only the last gives[False,True]. The dependent opposite-account owner and exact mark IDs remain visible. Removing a marking output makes the two-counter pair obligation unavailable. An unrelated same-value selector fails COUNTER source-role membership; a partial first-selector swap makes both returned owners identical and fails the written pair check. Wrong returned transaction or owner fails the actual written counter-pair consumer; downstream mark reads remain unexecuted in those changed worlds. Deleting either background Ledger entry fails its actual written certification site and creates no substitute entry. Consistent global A/B renaming preserves completion and swaps only labels.", "",
            "Keeping all role/reference interfaces but using one shared DONE status makes a single changed mark affect both late reads[False,False], losing the mixed result of this fixed account. A shared amount V by itself has no recorded-completion function at the written status check, so that strict replacement is partial; this is not a semantic type refutation of scalar quantities. Numeric Boolean coding, two quantities with separately paid status/role relations and a copied complete implementation remain fair wider rivals. No meaning is selected by these program consequences.", "",
            "ZL[o:y]pcheo and RF@221;pcheo are not substituted for ITopcheo; both readers stop there. Their subsequent ykaiin/[g:m], fcheeojy and lche@152;r variants remain visible with no dictionary aliases. RF is the corresponding spatial union, not an independent flagged paragraph. The three readers describe the same exposed leaf.", "",
            "Frozen extension metadata has an erroneous concatenated public_go_commit string. It is disclosed in AUTHOR_ACCOUNT; the actual public registration packet is retained separately. The immutable core/extension scientific rules were not edited.", "",
            "Every native IT contribution:", ""]
    for row in accounts["IT2a"]["rows"]:
        text.append("- `" + row["source_group_id"] + "` `" + row["ivtff_group_raw"] + "`: "
                    + row["interpretation"] + (" " + row["world_statement"] if row["world_statement"] else ""))
    text += ["", "Per-reader first barriers:", ""]
    for e, a in accounts.items():
        text.append("- " + e + ": " + a["status"] + "; first barrier " + str(a["first_barrier"]) + ".")
    text += ["", "No independent source owns these word meanings or consumers. Pacioli1494/Geijsbeek1914 is a historical mechanism prior after1450, not an identified manuscript source. The claim is an expensive conditional whole IT construction; prior partial failures, closed universal attachment routes, sealed material and reserve restrictions are unchanged.", ""]
    rp = BASE / "artifacts/AUTHOR_READING.md"
    rp.write_text("\n".join(text) + "\n")
    paths = [BASE / "src/CORE.json", BASE / "src/EXTENSIONS.json", Path(__file__), ap, rp]
    receipt = {"phase": "FINAL_AUTHOR_FREEZE", "freeze_utc": result["freeze_utc"],
               "files": {str(q.relative_to(BASE)): hashlib.sha256(q.read_bytes()).hexdigest() for q in paths},
               "statuses": {e: a["status"] for e, a in accounts.items()},
               "source_sha256": ext["source_sha256"], "native_rows": 90,
               "physical_ledger_posting_performed": False, "counterfactuals": len(fixtures),
               "immutable": True, "new_target_access": False}
    (BASE / "artifacts/FINAL_FREEZE_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
