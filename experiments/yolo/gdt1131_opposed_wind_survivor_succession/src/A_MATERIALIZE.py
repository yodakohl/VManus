"""Replay author A's exact, exploratory dictionary on the frozen shared packet.

This is an accounting materializer, not a decoder or source selector. It never
reads another author's files. Existing final freezes are not overwritten.
"""
from pathlib import Path
import collections
import datetime
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "src/SOURCE.json"
CORE = BASE / "src/A_CONSTRUCTORS.json"
PRIORS = BASE / "src/STRUCTURAL_PRIORS.json"

# Every assigned exact whole gets one entry in every reader and block.
# Compound component counts and aliases are unweighted explicit costs.
DICTIONARY = {
    "sain": ("SETUP_U_GREATER", 13, "Introduce the opposed generic participants and the u>v conditional encounter."),
    "or": ("WINNER_ALIVE", 1, "Under this condition, the original stronger participant is still blowing at t1."),
    "aiin": ("AN", 1, "Assert the condition/outcome as a generic world rule through bare aN."),
    "opchdy": ("APPLY_FOCUS", 1, "Apply the written rule to the explicitly referred participant."),
    "qotor": ("OPPOSED", 1, "Relate the two source bearings as opposed in their observer horizon."),
    "sheedy": ("EQUAL_CASE", 3, "Take equal force and construct its opposed-wind obstruction consequence."),
    "shodaiin": ("SO_D_AN", 5, "So supplies opposed source relation; daN asserts the consequent and applies it to the written focus."),
    "olfar": ("APPLY_U", 1, "Apply the current rule to the original first participant u."),
    "ary": ("APPLY_V", 1, "Apply the current rule to the original second participant v."),
    "dair": ("V_GREATER", 1, "Compare the second participant's force as greater than the first's."),
    "sheo": ("BUILD_CASE", 2, "Form the written comparison's condition and physical consequence."),
    "oraiin": ("AN_APPLY_WINNER", 2, "Exact whole template asserts this case and applies it to its stronger participant."),
    "chol": ("WINNER_ALIVE", 1, "The stronger original participant is still blowing under this case."),
    "daiin": ("D_AN", 2, "d+aN: assert the world conditional and apply it to the written focus."),
    "ockhdor": ("WEAKER_CEASES", 1, "The original weaker participant ceases because of the stronger."),
    "olkor": ("WINNER_IDENTITY", 1, "The surviving stronger wind is the original participant, with unchanged identity reference."),
    "shoral": ("CONJOIN", 1, "Conjoin the two latest world claims, retaining their conditions."),
    "sosees": ("APPLY_CONDITION", 1, "Apply the generic rule to its explicit conditional encounter."),
    "pchedeey": ("SETUP_U_GREATER", 13, "Explicitly introduce a generic opposed pair and u>v encounter, independent of a reported actual storm."),
    "olkey": ("WINNER_ALIVE", 1, "The original stronger participant is still blowing in this branch."),
    "qokedy": ("EQUAL_CASE", 3, "Introduce the equal-force opposed branch with mutual obstruction."),
    "sheos": ("U_OBSTRUCTED", 1, "In the equal-force branch the original first participant is obstructed."),
    "fcheey": ("WEAKER_CEASES", 1, "The other original participant does not continue blowing in the stated branch."),
    "otchedy": ("U_GREATER_CASE", 3, "Use greater first-participant force and construct its suppression condition and consequence."),
    "chotey": ("WINNER_ALIVE", 1, "The original stronger participant continues blowing under this condition."),
    "qocthey": ("WEAKER_CEASES", 1, "The weaker participant ceases due to that stronger participant."),
    "oteey": ("ORDER_CASE", 5, "Write t0<t1 and rebuild the condition/consequence on that ordering."),
    "ol": ("REF_U", 1, "Explicitly write the original first-participant variable u as the current focus."),
    "oloeorain": ("CONJOIN", 1, "Conjoin the latest participant consequence claims."),
    "qotaiin": ("BUILD_AN", 3, "Exact whole template rebuilds the conditional case and asserts its generic consequence."),
    "tchedy": ("WEAKER_CEASES", 1, "The original weaker participant ceases because of the stronger."),
    "otedy": ("WINNER_ALIVE", 1, "The original stronger participant is still blowing at the later time."),
    "qotchdy": ("SOURCE_OPPOSITION", 1, "The opposed source relation is the antecedent of this conditional consequence."),
    "chckhey": ("CONJOIN", 1, "Conjoin the latest claims with all original references retained."),
    "qtchedy": ("WINNER_ALIVE", 1, "The original stronger participant remains blowing under this case."),
    "qodar": ("REF_V", 1, "Explicitly refer to original second participant v."),
    "qotedar": ("WEAKER_CEASES", 1, "The original weaker participant ceases, without a replacement identity."),
    "qokar": ("WINNER_FORCE", 1, "The continuing original participant is the stronger one on the written force basis."),
    "qotchd": ("CONJOIN", 1, "Conjoin the two latest consequence claims."),
    "qotom": ("APPLY_CONDITION", 1, "Apply the written generic rule to the explicit encounter condition."),
    "soiis": ("WINNER_IDENTITY", 1, "The later surviving stronger wind retains the earlier participant identity."),
    "shedaiin": ("APPLY_V", 1, "Exact whole template applies the current rule to original second participant v; no universal shed prefix."),
    "chokcod": ("CONJOIN_RULE_PROP", 1, "Join the written general rule and its participant application."),
    "shedy": ("WEAKER_CEASES", 1, "Conditional predication about the original weaker participant; distinct from IDEA000582's old region type."),
    "ockhdar": ("WEAKER_CEASES", 1, "Paid exact whole alias, not an automatic r/a reading repair."),
    "olkar": ("WINNER_IDENTITY", 1, "Paid exact whole identity-predicate alias."),
    "roseer": ("APPLY_CONDITION", 1, "Paid exact whole application alias; no literal equivalence to sosees is inferred."),
    "oloqorain": ("CONJOIN", 1, "Paid exact whole conjunction alias."),
    "ytchedy": ("WINNER_ALIVE", 1, "Paid exact whole conditional survivor-predicate alias."),
}


def materialize():
    for name in ("A_ACCOUNT.json", "A_READING.md", "A_FINAL_FREEZE_RECEIPT.json"):
        if (BASE / "artifacts" / name).exists():
            raise SystemExit("Existing author freeze preserved: " + name)
    source = json.loads(SOURCE.read_text())
    core = json.loads(CORE.read_text())
    priors = json.loads(PRIORS.read_text())
    rows, objects, shared, states = [], {}, [], {}
    all_native = source["rows"]
    positions = {n["source_group_id"]: i for i, n in enumerate(all_native)}

    def obj(row, typ, value, args=(), family=None):
        oid = row["source_group_id"] + "#" + str(len(row["returns"]) + 1)
        objects[oid] = {"type": typ, "value": value, "producer_source_id": row["source_group_id"], "arguments": list(args), "consumer_source_ids": []}
        row["returns"].append(oid)
        row["arguments"].extend(args)
        row["delta"].append({"family": family, "arguments": list(args), "returns": oid})
        return oid

    def require(st, names):
        missing = [x for x in names if st.get(x) is None]
        if missing:
            raise ValueError("MISSING_WRITTEN_" + ",".join(missing))

    def bind(row, st, key, typ, name):
        st[key] = obj(row, typ, name, family="BIND")
        return st[key]

    def opposed(row, st):
        require(st, ("u", "v", "frame"))
        st["spatial"] = obj(row, "SpatialRelation", {"relation": "OPPOSED_SOURCE_BEARINGS", "u": st["u"], "v": st["v"], "frame": st["frame"]}, (st["u"], st["v"], st["frame"]), "SPATIAL")

    def strength(row, st, mode):
        require(st, ("u", "v", "basis"))
        st["strength"] = obj(row, "StrengthComparison", {"relation": mode, "u": st["u"], "v": st["v"], "basis": st["basis"]}, (st["u"], st["v"], st["basis"]), "STRENGTH")

    def order(row, st):
        t0 = obj(row, "Time", "t0", family="LITERAL_PAYLOAD")
        t1 = obj(row, "Time", "t1", family="LITERAL_PAYLOAD")
        st["time"] = obj(row, "TimeOrder", {"earlier": t0, "later": t1, "relation": "EARLIER"}, (t0, t1), "TIME")

    def case(row, st):
        require(st, ("spatial", "strength", "time"))
        sv = objects[st["spatial"]]["value"]
        cv = objects[st["strength"]]["value"]
        if (sv["u"], sv["v"]) != (cv["u"], cv["v"]):
            raise ValueError("PARTICIPANT_PAIR_MISMATCH")
        st["condition"] = obj(row, "WorldCondition", {"spatial": st["spatial"], "strength": st["strength"], "time": st["time"], "pair": [sv["u"], sv["v"]]}, (st["spatial"], st["strength"], st["time"]), "CONDITION")
        mode = cv["relation"]
        winner = None if mode == "EQUAL" else (cv["u"] if mode == "U_GREATER" else cv["v"])
        weaker = None if mode == "EQUAL" else (cv["v"] if mode == "U_GREATER" else cv["u"])
        st["outcome"] = obj(row, "WorldOutcome", {"condition": st["condition"], "winner_original": winner, "weaker_original": weaker, "obstructed_originals": [sv["u"], sv["v"]] if mode == "EQUAL" else [], "fresh_participant": None, "event_status": "GENERIC_CONSEQUENT_NOT_ACTUAL_STORM"}, (st["condition"],), "OUTCOME")

    def setup(row, st):
        # The lexical whole explicitly binds a fresh quantified rule scope.
        # This is not actual generation of a new physical wind.
        bind(row, st, "u", "WindVariable", "u")
        bind(row, st, "v", "WindVariable", "v")
        bind(row, st, "observer", "Observer", "O")
        bind(row, st, "basis", "Basis", "S")
        horizon = obj(row, "Horizon", "H", family="LITERAL_PAYLOAD")
        st["frame"] = obj(row, "HorizonFrame", {"observer": st["observer"], "horizon": horizon}, (st["observer"], horizon), "FRAME")
        order(row, st)
        opposed(row, st)
        strength(row, st, "U_GREATER")
        case(row, st)
        st["focus"] = st["u"]
        row["scope_binding"] = "Explicit lexical quantified-pair introduction; not a line reset or physical generation."

    def an(row, st, licensed=False):
        require(st, ("condition", "outcome"))
        st["rule"] = obj(row, "UniversalWorldRule", {"condition": st["condition"], "outcome": st["outcome"], "quantification": "FOR_EVERY_ACTUAL_WIND_PAIR_SATISFYING_ANTECEDENT"}, (st["condition"], st["outcome"]), "aN")
        if licensed:
            raw = row["ivtff_group_raw"]
            shared.append({"source_group_id": row["source_group_id"], "raw_form": raw, "interface_id": "aN", "arguments": [st["condition"], st["outcome"]], "returned_value": st["rule"], "consumer_source_ids": [], "effect": "Assert a generic physics rule with actual participant identity, conditional obstruction/suppression and ordered times; no merely frozen record.", "status": "EXECUTED", "fixed_formal_units": priors["exact_forms"][raw]["isolated_group_units"], "fixed_ordered_trees": priors["exact_forms"][raw]["ordered_unit_trees"], "semantic_license": "Exploratory exact-form hypothesis, not a universal morpheme or validated meaning."})

    def apply(row, st, argument):
        require(st, ("rule",))
        if argument is None:
            raise ValueError("MISSING_WRITTEN_APPLICATION_ARGUMENT")
        rid = st["rule"]
        out = objects[rid]["value"]["outcome"]
        pid = obj(row, "WorldProposition", {"kind": "RULE_APPLICATION", "rule": rid, "outcome": out, "argument": argument, "conditional_not_observed": True}, (rid, argument), "APPLY")
        st["props"].append(pid)

    def predicate(row, st, mode):
        require(st, ("outcome", "condition"))
        out = objects[st["outcome"]]["value"]
        if mode == "SOURCE_OPPOSITION":
            who, related = st["u"], st["spatial"]
        elif mode == "U_OBSTRUCTED":
            who, related = st["u"], st["outcome"]
            if who not in out["obstructed_originals"]:
                raise ValueError("U_OBSTRUCTION_NOT_ENTAILED_BY_FIXED_OUTCOME")
        elif mode == "WEAKER_CEASES":
            who = out["weaker_original"] or st["v"]
            related = st["outcome"]
        else:
            who, related = out["winner_original"], st["outcome"]
            if who is None:
                raise ValueError("NO_SURVIVOR_IN_EQUAL_FORCE_BRANCH")
        row["fixed_property_argument"] = {"type": "PredicationPayload", "value": mode, "producer_source_id": row["source_group_id"], "cost": "Paid exact-whole predication value, not an opaque noun."}
        pid = obj(row, "WorldProposition", {"kind": mode, "participant_original": who, "condition": st["condition"], "related": related, "conditional_not_observed": True}, (who, related), "PREDICATE")
        st["focus"] = who
        st["props"].append(pid)

    for native in all_native:
        edition = native["edition"]
        st = states.setdefault(edition, {"props": []})
        raw = native["ivtff_group_raw"]
        assigned = raw in DICTIONARY
        row = dict(native, entry_id="A:" + raw if assigned else None, status="ACCOUNTED" if assigned else "UNKNOWN", interpretation=DICTIONARY[raw][2] if assigned else None, arguments=[], returns=[], consumer_source_ids=[], cost={"dictionary_entry": "A:" + raw} if assigned else {"unresolved_whole": 1}, delta=[], barriers=[], unknown_carry_source_ids=[])
        rows.append(row)
        if not assigned:
            row["barriers"].append("UNASSIGNED_EXACT_WHOLE_NOT_INERT")
            continue
        op = DICTIONARY[raw][0]
        try:
            if op == "SETUP_U_GREATER":
                setup(row, st)
            elif op == "OPPOSED":
                opposed(row, st)
            elif op == "EQUAL_CASE":
                strength(row, st, "EQUAL")
                case(row, st)
            elif op == "V_GREATER":
                strength(row, st, "V_GREATER")
            elif op == "U_GREATER_CASE":
                strength(row, st, "U_GREATER")
                case(row, st)
            elif op == "ORDER_CASE":
                order(row, st)
                case(row, st)
            elif op == "BUILD_CASE":
                case(row, st)
            elif op in ("AN", "D_AN", "SO_D_AN", "AN_APPLY_WINNER", "BUILD_AN"):
                if op == "SO_D_AN":
                    opposed(row, st)
                    case(row, st)
                elif op == "BUILD_AN":
                    case(row, st)
                an(row, st, raw in ("aiin", "daiin", "shodaiin"))
                if op in ("D_AN", "SO_D_AN"):
                    apply(row, st, st.get("focus"))
                elif op == "AN_APPLY_WINNER":
                    st["focus"] = objects[st["outcome"]]["value"]["winner_original"]
                    apply(row, st, st["focus"])
            elif op.startswith("APPLY_"):
                key = {"APPLY_U": "u", "APPLY_V": "v", "APPLY_FOCUS": "focus", "APPLY_CONDITION": "condition"}[op]
                apply(row, st, st.get(key))
            elif op in ("REF_U", "REF_V"):
                key = "u" if op == "REF_U" else "v"
                if st.get(key) is None:
                    bind(row, st, key, "WindVariable", key)
                row["arguments"].append(st[key])
                st["focus"] = st[key]
                obj(row, "WindVariableReference", {"original": st[key]}, (st[key],), "BIND")
            elif op in ("CONJOIN", "CONJOIN_RULE_PROP"):
                if op == "CONJOIN_RULE_PROP":
                    require(st, ("rule",))
                    args = [st["rule"], st["props"][-1]] if st["props"] else []
                else:
                    args = st["props"][-2:]
                if len(args) != 2:
                    raise ValueError("MISSING_TWO_WRITTEN_WORLD_CLAIMS")
                pid = obj(row, "WorldProposition", {"kind": "CONJUNCTION", "claims": args}, args, "CONJOIN")
                st["props"].append(pid)
            else:
                predicate(row, st, op)
        except ValueError as exc:
            row["status"] = "BLOCKED"
            row["barriers"].append(str(exc))

    byid = {r["source_group_id"]: r for r in rows}
    for row in rows:
        carry = set()
        for oid in set(row["arguments"]):
            ob = objects[oid]
            ob["consumer_source_ids"].append(row["source_group_id"])
            start, end = positions[ob["producer_source_id"]], positions[row["source_group_id"]]
            carry.update(n["source_group_id"] for n in all_native[start + 1:end] if n["edition"] == row["edition"] and byid[n["source_group_id"]]["status"] == "UNKNOWN")
        row["unknown_carry_source_ids"] = sorted(carry, key=positions.get)
        row["cost"]["unknown_intervening_groups"] = len(carry)
        if carry and row["status"] == "ACCOUNTED":
            row["status"] = "ACCOUNTED_WITH_UNPROVED_CARRY"
    for row in rows:
        row["consumer_source_ids"] = sorted({sid for oid in row["returns"] for sid in objects[oid]["consumer_source_ids"]}, key=positions.get)
    for use in shared:
        use["consumer_source_ids"] = objects[use["returned_value"]]["consumer_source_ids"]
        use["unknown_carry_source_ids"] = byid[use["source_group_id"]]["unknown_carry_source_ids"]

    def condition_text(cid):
        c = objects[cid]["value"]
        mode = objects[c["strength"]]["value"]["relation"]
        comparison = {"U_GREATER": "u is stronger than v", "V_GREATER": "v is stronger than u", "EQUAL": "u and v have equal force"}[mode]
        return "their source bearings are opposed in observer O's horizon H, " + comparison + " on force basis S, and t0 precedes t1"

    def outcome_text(oid):
        out = objects[oid]["value"]
        if out["winner_original"] is None:
            return "both original participants u and v obstruct one another and neither continues blowing at t1"
        winner = objects[out["winner_original"]]["value"]
        weaker = objects[out["weaker_original"]]["value"]
        return f"original {winner} still blows at t1 and original {weaker} ceases because of {winner}; no newly generated wind replaces that survivor"

    def proposition_text(oid):
        ob = objects[oid]
        v = ob["value"]
        if ob["type"] == "UniversalWorldRule":
            return "For every wind pair: if " + condition_text(v["condition"]) + ", then " + outcome_text(v["outcome"]) + "."
        kind = v["kind"]
        if kind == "CONJUNCTION":
            return "Together: " + " AND ".join(proposition_text(x) for x in v["claims"])
        if kind == "RULE_APPLICATION":
            arg = objects[v["argument"]]
            who = arg["value"] if arg["type"] == "WindVariable" else "the written encounter"
            return "For " + str(who) + ", retain the rule consequence: " + outcome_text(v["outcome"]) + ", conditional on " + condition_text(objects[v["rule"]]["value"]["condition"]) + "."
        who = objects[v["participant_original"]]["value"]
        payload = {"WINNER_ALIVE": "original " + who + " still blows at t1", "WINNER_IDENTITY": "the surviving " + who + " is the very original participant, not merely a same-kind wind", "WINNER_FORCE": "the original continuing " + who + " is the stronger participant on S", "WEAKER_CEASES": "original " + who + " no longer blows at t1 because of the stated confrontation", "U_OBSTRUCTED": "original u is obstructed", "SOURCE_OPPOSITION": "the source bearings of original u and v are opposed in H"}[kind]
        return "If " + condition_text(v["condition"]) + ", then " + payload + "."

    # Compact terminal propositions, not duplicated histories or whole-state dumps.
    for row in rows:
        row["world_claims"] = [{"returned_value": oid, "text": proposition_text(oid)} for oid in row["returns"] if objects[oid]["type"] in ("UniversalWorldRule", "WorldProposition")]
    primary = []
    for e in ("IT2a", "ZL3b", "RF1b"):
        for b in ("N", "E"):
            rr = [r for r in rows if r["edition"] == e and r["block"] == b]
            barrier = next((r for r in rr if r["status"] != "ACCOUNTED"), None)
            seam = next((r for r in rr if "UNCERTAIN" in r["left_separator"] + r["right_separator"]), None)
            complete = barrier is None and seam is None
            primary.append({"edition": e, "block": b, "native_count": len(rr), "source_group_ids": [r["source_group_id"] for r in rr], "complete": complete, "status": "COMPLETE_EXPLORATORY_C0" if complete else "PARTIAL_LITERAL_OR_SCOPE_REPLAY", "first_barrier": barrier["source_group_id"] if barrier else seam["source_group_id"] if seam else None, "first_barrier_reason": barrier["barriers"] or ["UNPROVED_UNKNOWN_CARRY"] if barrier else ["NATIVE_UNCERTAIN_SEAM"] if seam else [], "literal_unknowns": [r["source_group_id"] for r in rr if r["status"] == "UNKNOWN"]})
    aliases = collections.Counter(v[0] for v in DICTIONARY.values())
    unknown = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "UNKNOWN":
            unknown[r["ivtff_group_raw"]].append(r["source_group_id"])
    dictionary = [{"entry_id": "A:" + raw, "raw_form": raw, "rule": op, "interpretation": text, "arguments_policy": "Dictionary-fixed roles and most recent explicitly written typed inputs; no locus-specific exceptions.", "cost": {"exact_whole": 1, "constructor_components": components}, "occurrences": [r["source_group_id"] for r in rows if r["ivtff_group_raw"] == raw]} for raw, (op, components, text) in DICTIONARY.items()]
    unused = [oid for oid, ob in objects.items() if not ob["consumer_source_ids"] and ob["type"] not in ("UniversalWorldRule", "WorldProposition")]
    costs = {"initial_core_families": len(core["constructors"]), "additional_literal_operand_rule": "LITERAL_PAYLOAD materializes registered H/t0/t1 as typed operands; one paid rule, no new content constant or core signature override.", "fixed_predicate_payloads": ["WINNER_ALIVE", "WINNER_IDENTITY", "WINNER_FORCE", "WEAKER_CEASES", "U_OBSTRUCTED", "SOURCE_OPPOSITION"], "initial_opaque_constants": len(core["opaque_constants"]), "assigned_exact_wholes": len(DICTIONARY), "unassigned_exact_wholes": len(unknown), "constructor_template_components": sum(v[1] for v in DICTIONARY.values()), "exact_aliases_beyond_first_identical_rule": sum(n - 1 for n in aliases.values()), "reference_defaults": ["latest explicit typed wind pair/frame/basis/time/comparison/condition/outcome/rule", "predicate selects condition's original winner or weaker, not an arbitrary same-kind wind", "d applies aN rule to most recent written participant focus", "conjunction selects latest two world propositions", "bare aiin uses current written condition and outcome", "So explicitly constructs source opposition, then condition/outcome; d consumes the rule", "application uses explicit u/v/condition role designated by exact whole entry"], "lexical_scope_introductions": [r["source_group_id"] for r in rows if DICTIONARY.get(r["ivtff_group_raw"], (None,))[0] == "SETUP_U_GREATER"], "scope_introduction_semantics": "Paid generic quantified participant binding, not physical wind generation or metadata reset.", "unknown_carry_rows": sum(bool(r["unknown_carry_source_ids"]) for r in rows), "unknown_carry_uses": sum(len(r["unknown_carry_source_ids"]) for r in rows), "unknown_carry_truth": "Unproved assumption; carried fragments do not establish meanings for skipped words.", "unconsumed_auxiliary_outputs": unused, "unused_instructions": [], "null_parts": 0, "ambient_world_inputs": [], "unweighted_counts_only": True}
    account = {"candidate_id": "A", "model": "SUPPRESSION", "status": "COMPLETE_IT_N_E_C0_WITH_PARTIAL_ALTERNATES_AND_OUTSIDE", "freeze_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "constructor_sha256": hashlib.sha256(CORE.read_bytes()).hexdigest(), "rows": rows, "dictionary": dictionary, "unassigned_dictionary": [{"raw_form": raw, "status": "UNKNOWN", "occurrences": ids} for raw, ids in sorted(unknown.items())], "objects": objects, "primary_units": primary, "shared_part_uses": shared, "costs": costs, "mechanisms": {"strength_suppression": True, "solar_succession": False, "reason_no_succession": "No extra cause, adjacent relation or newly generated identity is supplied by this fixed reading; historical coexistence does not donate them."}, "world_status": "All N/E claims are generic conditionals, not claims that an actual storm or an observed pair existed.", "counterfactual_world_commitments": [{"world": "Opposed u/v in H on S, u>v, both assigned as encounter participants at t0.", "commitment": "Original u is still blowing at t1; original v ceases because of u. Replacing u by a fresh same-kind w violates retained identity.", "nonseed_source_ids": ["IT2a|f85r2.5|G002", "IT2a|f85r2.10|G003", "IT2a|f85r2.11|G001"], "source_is_a_semantic_hypothesis_not_confirmation": True}, {"world": "Same original pair/frame/time but equal force.", "commitment": "Neither original participant remains blowing in the confrontation; the applications at olfar and ary each retain their own original identity.", "nonseed_source_ids": ["IT2a|f85r2.3|G004", "IT2a|f85r2.3|G005"]}], "remaining_equivalence": "A static generic account using t0/t1 states, explicit original identities, opposition, force and cause can express exactly these consequences. No dynamic-interface superiority is claimed.", "known_predecessors": "IDEA000582 old or/shedy type clash and IDEA000861/789 missing discriminator/circular carry remain unchanged. This new exact or/shedy interface is separately paid, not a correction of those freezes.", "confirmation_capacity": 0, "confirmed_words": 0, "blinding": "No B/C artifacts or post-author critics read.", "new_access": False}
    account_path = BASE / "artifacts/A_ACCOUNT.json"
    account_path.write_text(json.dumps(account, ensure_ascii=False, indent=2) + "\n")
    reading = ["# Candidate A — opposed force and original survivor", "", "Complete hypothetical IT N19/E27 reading; alternate and outside replay limits remain explicit. Zero confirmed words and zero independent confirmation leaves.", "", "N: Consider two actual wind participants, called u and v only as generic variables. Their source bearings oppose one another in observer O's horizon H; use one force basis S and an encounter time t0 followed by t1. If u is stronger, the original u continues blowing and the original v ceases because of u. Retain that consequence for the original participant. If instead their forces are equal, both are obstructed: this applies separately to original u and original v. If v is stronger, the original v survives and original u ceases because of v. The written tail joins cessation with the original stronger survivor's identity and applies the general condition. This describes the alternative force cases, not three sequential weather events.", "", "E: Introduce an explicit generic pair in the same observer-relative, noncardinal terms. A greater first-participant force gives its original survivor; the equal-force alternative obstructs the originals. Return explicitly to the greater-force branch: the stronger original participant continues while the weaker original participant ceases because of it, with the encounter before the outcome. Refer to original u and join these participant claims. Generalize this conditional and retain cessation, later survival and opposed source relation. Refer to original v; retain its cessation, the stronger original's force and the causal comparison. Apply the rule to the written encounter, retain the survivor's original identity, generalize the rule, apply it to original v and join the application with the general claim. The final statement concerns both the causal cessation and identity of the stronger survivor; it is not a bare name or an OriginalOnly consumer type.", "", "All exact words in both IT primary units contribute an operation below. The exact-whole dictionary is expensive and contains paid aliases, repeated assertions and exact compound templates. It is an exploratory natural physics reading, not evidence that these assignments are likely or true. Its substantive world commitments are conditional force-dependent obstruction/cessation and retained original participant identity. No cardinal identity, storm occurrence, matter genealogy, fresh generation, cloud-clearing or solar succession is added.", "", "The common aN operation asserts a condition/outcome as a generic claim about actual wind assignments. aiin is the bare root. daiin preserves d+aN, where d applies the resulting claim to a written participant focus. shodaiin preserves So followed by daN: So builds opposed source relation in the written horizon and rebuilds its conditional inputs; aN asserts them, and d applies the rule. So may repeat already supplied geometry; that redundancy is charged. The first N aiin asserts the u>v generic rule, shodaiin asserts the equal-force rule, and N daiin asserts the v>u rule. They are different world assertions, not an inert shared tag. Their consumers appear in the account.", "", "The old IDEA000582 or/shedy clash is preserved as a historical decision. This author assigns or a conditional survivor predicate and shedy a conditional cessation predicate under a different paid dictionary. The exact S sequence or shedy tedy sodaiiin chy remains partial: tedy, sodaiiin and chy have no value here. RF's {ch'}edy remains unknown rather than inheriting shedy. Assigned words are applied in every S/W/.1/.24 occurrence, even when missing operands or unresolved unknown carry blocks interpretation.", "", "Literal primary results:", ""]
    reading += [f'- {x["edition"]} {x["block"]}: {x["native_count"]} groups; {x["status"]}; first barrier {x["first_barrier"]}.' for x in primary]
    reading += ["", "Written operation-by-operation primary reading:", ""]
    for r in rows:
        if r["edition"] == "IT2a" and r["block"] in ("N", "E"):
            claims = " ".join(x["text"] for x in r["world_claims"])
            reading.append(f'- `{r["source_group_id"]}` `{r["ivtff_group_raw"]}`: {r["interpretation"]} {claims}')
    reading += ["", "The complete account preserves all 473 native positions and twelve fields. Every dictionary assignment has the same entry at every exact recurrence. Unknown groups are not interpreted as no-ops; fragments that retain earlier inputs across them explicitly enumerate and price those intervening unknowns. Those outside fragments do not become whole S/W readings. Uncertain boundaries remain a separate alternate-reader barrier even where isolated dictionary words are assigned.", "", "Same-world counterfactual: with opposed participants of unequal force, substitute a fresh same-kind wind for the original stronger survivor at t1. This account's olkor/soiis identity predicates and qotedar cessation reference then fail their actual claimed identity relations. Their signatures accept ordinary wind references; the distinction is in the paid world proposition, not a forbidden rival type. Equal-force alternatives instead obstruct both original participants. These are consequences of the candidate reading, not manuscript-owned confirmations of that reading.", "", "A static two-time-state formulation can express the same force, original identity and causal facts. The account offers no discriminator against that fair formulation and no semantic winner. It supplies no required solar succession; adding one later would change the frozen reading. Retain it, if coherent under audit, only as an unranked whole C0 candidate.", "", "Costs: " + json.dumps(costs, ensure_ascii=False), ""]
    reading_path = BASE / "artifacts/A_READING.md"
    reading_path.write_text("\n".join(reading) + "\n")
    # Final receipt is written last and never modified by this materializer.
    receipt = {"candidate_id": "A", "freeze_utc": account["freeze_utc"], "immutable": True, "files": {str(q.relative_to(BASE)): hashlib.sha256(q.read_bytes()).hexdigest() for q in (CORE, Path(__file__), account_path, reading_path)}, "primary_complete_counts": dict(collections.Counter(x["edition"] for x in primary if x["complete"])), "native_counts": dict(collections.Counter(r["edition"] for r in rows)), "status_counts": dict(collections.Counter(r["status"] for r in rows)), "shared_part_executed_forms": sorted({u["raw_form"] for u in shared}), "source_sha256": account["source_sha256"], "no_new_access": True, "no_b_c_read": True}
    (BASE / "artifacts/A_FINAL_FREEZE_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    materialize()
