#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXP_DIR = Path(__file__).resolve().parents[1]
OUT = EXP_DIR / "artifacts"
G606 = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
G608 = ROOT / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts"
GUARDED = G606 / "guarded_rows.tsv"
SEQUENCES = G606 / "unit_sequences.json"
STEMS = G608 / "stable_stem_role_summary.tsv"
TREE = G608 / "merge_tree.tsv"
SEED = 608017
SECTIONS = ("B", "C", "H", "P", "S", "T")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields=None):
    rows = list(rows)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            payload = {key: row.get(key, "") for key in fields}
            if fields and payload[fields[-1]] == "":
                payload[fields[-1]] = "<NA>"
            writer.writerow(payload)


def form_text(form):
    return "+".join(form)


def fmt_counts(counter):
    return ";".join(f"{key}:{counter.get(key, 0)}" for key in SECTIONS)


def logit(p):
    p = min(1 - 1e-12, max(1e-12, p))
    return math.log(p / (1 - p))


def contrast_logodds(form_sections, form_total, all_sections, all_total, target):
    target = set(target)
    a = sum(form_sections.get(s, 0) for s in target)
    b = sum(all_sections.get(s, 0) for s in target) - a
    rest_n = all_total - form_total
    p_form = (a + 0.5) / (form_total + 1.0)
    p_rest = (b + 0.5) / (rest_n + 1.0)
    return logit(p_form) - logit(p_rest)


def js_divergence(a: Counter, b: Counter, keys=SECTIONS):
    aa = [a.get(k, 0) + 0.5 for k in keys]
    bb = [b.get(k, 0) + 0.5 for k in keys]
    sa, sb = sum(aa), sum(bb)
    pa, pb = [x / sa for x in aa], [x / sb for x in bb]
    m = [(x + y) / 2 for x, y in zip(pa, pb)]
    kl_a = sum(x * math.log(x / z, 2) for x, z in zip(pa, m))
    kl_b = sum(y * math.log(y / z, 2) for y, z in zip(pb, m))
    return 0.5 * (kl_a + kl_b)


def zmap(values):
    values = dict(values)
    mean = statistics.fmean(values.values()) if values else 0.0
    sd = statistics.pstdev(values.values()) if len(values) > 1 else 0.0
    if sd == 0:
        return {k: 0.0 for k in values}
    return {k: (v - mean) / sd for k, v in values.items()}


def paragraph_metadata(guarded):
    metadata = {}
    page_active = {}
    page_counter = Counter()
    paragraph_loci = defaultdict(list)
    for row in guarded:
        page = row["page"]
        raw = row["ivtff_raw"]
        starts = "<%>" in raw[:32]
        ends = "<$>" in raw
        if starts or page not in page_active:
            page_counter[page] += 1
            page_active[page] = f"{page}:p{page_counter[page]}"
        pid = page_active[page]
        paragraph_loci[pid].append(row["locus"])
        metadata[row["locus"]] = {**row, "paragraph_id": pid}
        if ends:
            page_active.pop(page, None)
    for pid, loci in paragraph_loci.items():
        for index, locus in enumerate(loci):
            metadata[locus]["paragraph_line_index"] = index
            metadata[locus]["paragraph_line_count"] = len(loci)
    return metadata, paragraph_loci


def build_formal_sets(tree_rows):
    entry = {"q"}
    closure = {"y", "dy", "aN"}
    knonterminal = {"k"}
    for row in tree_rows:
        if row["left"] == "q":
            entry.add(row["merged"])
        if row["right"] in {"y", "dy", "aN"}:
            closure.add(row["merged"])
        if row["right"] == "k":
            knonterminal.add(row["merged"])
    return entry, closure, knonterminal


def build_occurrences(seqdata, metadata, entry_set, closure_set, k_set):
    occurrences = {"train": [], "held": []}
    by_split_locus = {"train": defaultdict(list), "held": defaultdict(list)}
    for split in ("train", "held"):
        for rec in seqdata["sequences"][split]:
            assert not rec["page"].lower().startswith("f84")
            assert not rec["physical_folio"].lower().startswith("f84")
            by_split_locus[split][rec["locus"]].append(rec)
        for locus, chunks in by_split_locus[split].items():
            chunks.sort(key=lambda r: int(r["chunk_index"]))
            meta = metadata[locus]
            assert meta["split"] == split
            forms = [tuple(r["units"]) for r in chunks]
            for i, (rec, form) in enumerate(zip(chunks, forms)):
                frames = []
                if len(form) >= 2:
                    for pos in range(len(form)):
                        masked = list(form)
                        masked[pos] = "*"
                        frames.append(("internal", f"{pos}/{len(form)}:" + "+".join(masked)))
                if i > 0:
                    frames.append(("left", form_text(forms[i - 1])))
                if i + 1 < len(forms):
                    frames.append(("right", form_text(forms[i + 1])))
                if i > 0 and i + 1 < len(forms):
                    frames.append(("both", form_text(forms[i - 1]) + "||" + form_text(forms[i + 1])))
                occurrences[split].append({
                    "split": split,
                    "page": rec["page"],
                    "physical_folio": rec["physical_folio"],
                    "locus": locus,
                    "chunk_index": i,
                    "line_chunk_count": len(forms),
                    "section": rec["section"],
                    "paragraph_id": meta["paragraph_id"],
                    "paragraph_line_index": meta["paragraph_line_index"],
                    "paragraph_line_count": meta["paragraph_line_count"],
                    "form": form,
                    "form_text": form_text(form),
                    "frames": frames,
                    "line_initial": int(i == 0),
                    "line_final": int(i == len(forms) - 1),
                    "paragraph_initial": int(meta["paragraph_line_index"] == 0 and i == 0),
                    "paragraph_final": int(meta["paragraph_line_index"] == meta["paragraph_line_count"] - 1 and i == len(forms) - 1),
                    "entry_flag": int(form[0] in entry_set),
                    "closure_flag": int(form[-1] in closure_set),
                    "k_flag": int(any(unit in k_set for unit in form)),
                    "seq_len": len(form),
                })
    return occurrences, by_split_locus


def aggregate_profiles(occurrences):
    profiles = {"train": {}, "held": {}}
    all_sections = {}
    for split in ("train", "held"):
        grouped = defaultdict(list)
        for occ in occurrences[split]:
            grouped[occ["form_text"]].append(occ)
        all_sec = Counter(occ["section"] for occ in occurrences[split])
        all_sections[split] = all_sec
        all_total = len(occurrences[split])
        for form, rows in grouped.items():
            sec = Counter(r["section"] for r in rows)
            folios = {r["physical_folio"] for r in rows}
            section_folios = defaultdict(set)
            for row in rows:
                section_folios[row["section"]].add(row["physical_folio"])
            profiles[split][form] = {
                "n": len(rows),
                "folios": folios,
                "section_folios": section_folios,
                "sections": sec,
                "section_count": len(sec),
                "line_initial_rate": sum(r["line_initial"] for r in rows) / len(rows),
                "line_final_rate": sum(r["line_final"] for r in rows) / len(rows),
                "paragraph_initial_rate": sum(r["paragraph_initial"] for r in rows) / len(rows),
                "paragraph_final_rate": sum(r["paragraph_final"] for r in rows) / len(rows),
                "entry_rate": sum(r["entry_flag"] for r in rows) / len(rows),
                "closure_rate": sum(r["closure_flag"] for r in rows) / len(rows),
                "k_rate": sum(r["k_flag"] for r in rows) / len(rows),
                "seq_len": rows[0]["seq_len"],
                "logodds_H": contrast_logodds(sec, len(rows), all_sec, all_total, {"H"}),
                "logodds_PB": contrast_logodds(sec, len(rows), all_sec, all_total, {"P", "B"}),
                "logodds_B": contrast_logodds(sec, len(rows), all_sec, all_total, {"B"}),
                "logodds_P": contrast_logodds(sec, len(rows), all_sec, all_total, {"P"}),
                "logodds_T": contrast_logodds(sec, len(rows), all_sec, all_total, {"T"}),
            }
    return profiles, all_sections


def build_frame_maps(occurrences, eligible):
    frame_maps = {"train": defaultdict(Counter), "held": defaultdict(Counter)}
    carrier_frames = {"train": defaultdict(Counter), "held": defaultdict(Counter)}
    for split in ("train", "held"):
        for occ in occurrences[split]:
            form = occ["form_text"]
            if form not in eligible:
                continue
            for channel, value in occ["frames"]:
                key = (channel, value)
                frame_maps[split][key][form] += 1
                carrier_frames[split][form][key] += 1
    return frame_maps, carrier_frames


def build_graph(frame_maps, eligible):
    pair_stats = defaultdict(lambda: {"weight": 0.0, "frames": 0, "internal": 0.0, "left": 0.0, "right": 0.0, "both": 0.0})
    for (channel, _value), counts in frame_maps["train"].items():
        members = sorted(form for form in counts if form in eligible)
        for a, b in itertools.combinations(members, 2):
            contribution = math.log1p(min(counts[a], counts[b]))
            stat = pair_stats[(a, b)]
            stat["weight"] += contribution
            stat["frames"] += 1
            stat[channel] += contribution
    qualifying = {pair: stat for pair, stat in pair_stats.items() if stat["frames"] >= 2}
    neighbour_rows = defaultdict(list)
    for (a, b), stat in qualifying.items():
        neighbour_rows[a].append((stat["weight"], b))
        neighbour_rows[b].append((stat["weight"], a))
    retained_pairs = set()
    for form in sorted(eligible):
        ranked = sorted(neighbour_rows.get(form, []), key=lambda x: (-x[0], x[1]))[:5]
        for _weight, other in ranked:
            retained_pairs.add(tuple(sorted((form, other))))
    adjacency = {form: set() for form in eligible}
    for a, b in retained_pairs:
        adjacency[a].add(b)
        adjacency[b].add(a)
    raw_components = []
    seen = set()
    for node in sorted(eligible):
        if node in seen:
            continue
        stack = [node]
        seen.add(node)
        comp = []
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nxt in sorted(adjacency[cur]):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        raw_components.append(sorted(comp))
    raw_components.sort(key=lambda c: (-len(c), c[0]))
    component_of = {}
    components = {}
    for idx, comp in enumerate(raw_components, 1):
        cid = f"X{idx:03d}"
        components[cid] = comp
        for form in comp:
            component_of[form] = cid
    return qualifying, retained_pairs, adjacency, components, component_of


def held_pair_stats(pair, frame_maps):
    a, b = pair
    frames = 0
    weight = 0.0
    channels = Counter()
    examples = []
    for (channel, value), counts in frame_maps["held"].items():
        if counts.get(a, 0) and counts.get(b, 0):
            frames += 1
            weight += math.log1p(min(counts[a], counts[b]))
            channels[channel] += 1
            if len(examples) < 3:
                examples.append(f"{channel}:{value}")
    return frames, weight, channels, examples


def transferred_pair_stats(pair, frame_maps):
    """Same pair must share the same exact frame in train and held."""
    a, b = pair
    frames = 0
    weight = 0.0
    channels = Counter()
    examples = []
    for (channel, value), train_counts in frame_maps["train"].items():
        if not (train_counts.get(a, 0) and train_counts.get(b, 0)):
            continue
        held_counts = frame_maps["held"].get((channel, value), Counter())
        if held_counts.get(a, 0) and held_counts.get(b, 0):
            frames += 1
            weight += math.log1p(min(held_counts[a], held_counts[b]))
            channels[channel] += 1
            if len(examples) < 3:
                examples.append(f"{channel}:{value}")
    return frames, weight, channels, examples


def selection_scores(profiles, eligible, components, used=None):
    used = set(used or ())
    candidates = [f for f in eligible if f not in used and len(components.get(f, [])) >= 0]
    return candidates


def choose_from_components(candidate_scores, component_of, components, k, special_entity=False):
    options = []
    for cid, members in components.items():
        ranked = []
        for member in members:
            if member not in candidate_scores:
                continue
            value = candidate_scores[member]
            numeric = value[0] if isinstance(value, tuple) else value
            ranked.append((numeric, member))
        ranked = sorted(ranked, key=lambda x: (-x[0], x[1]))
        if special_entity:
            if len(ranked) < k:
                continue
            top3 = ranked[:3]
            tail = ranked[3:20]
            if len(tail) < 2:
                continue
            low = min(tail, key=lambda x: (candidate_scores[x[1]][1] if isinstance(candidate_scores[x[1]], tuple) else 0, -x[0], x[1]))
            high = max(tail, key=lambda x: (candidate_scores[x[1]][1] if isinstance(candidate_scores[x[1]], tuple) else 0, x[0], x[1]))
            picked = top3 + ([low] if low not in top3 else []) + ([high] if high not in top3 and high != low else [])
            if len(picked) < 5:
                for item in ranked:
                    if item not in picked:
                        picked.append(item)
                    if len(picked) == 5:
                        break
            picked = picked[:5]
            numeric = [x[0] for x in picked]
        else:
            if len(ranked) < k:
                continue
            picked = ranked[:k]
            numeric = [x[0] for x in picked]
        options.append((statistics.fmean(numeric), cid, [x[1] for x in picked]))
    if not options:
        return None, []
    _score, cid, picked = sorted(options, key=lambda x: (-x[0], x[1], x[2]))[0]
    return cid, picked


def select_pools(profile_train, eligible, components, component_of):
    comp_members = {cid: members for cid, members in components.items() if len(members) >= 4}
    allowed = {form for members in comp_members.values() for form in members}
    used = set()
    selected = {}
    chosen_components = {}

    op_candidates = [f for f in allowed if f not in used and profile_train[f]["section_count"] >= 3]
    z_line = zmap({f: profile_train[f]["line_initial_rate"] for f in op_candidates})
    z_entry = zmap({f: profile_train[f]["entry_rate"] for f in op_candidates})
    op_scores = {f: z_line[f] + z_entry[f] + 0.25 * math.log(profile_train[f]["section_count"]) for f in op_candidates}
    cid, picks = choose_from_components(op_scores, component_of, comp_members, 4)
    selected["operation"] = picks
    chosen_components["operation"] = cid
    used.update(picks)

    plant_scores = {f: profile_train[f]["logodds_H"] for f in allowed if f not in used}
    cid, picks = choose_from_components(plant_scores, component_of, comp_members, 4)
    selected["plant_part"] = picks
    chosen_components["plant_part"] = cid
    used.update(picks)

    liquid_scores = {f: profile_train[f]["logodds_PB"] for f in allowed if f not in used}
    cid, picks = choose_from_components(liquid_scores, component_of, comp_members, 4)
    selected["liquid_material"] = picks
    chosen_components["liquid_material"] = cid
    used.update(picks)

    entity_scores = {}
    for f in allowed:
        if f in used:
            continue
        score = max(profile_train[f]["logodds_B"], profile_train[f]["logodds_P"], profile_train[f]["logodds_T"])
        entity_scores[f] = (score, profile_train[f]["line_initial_rate"])
    cid, picks = choose_from_components(entity_scores, component_of, comp_members, 5, special_entity=True)
    selected["record_entity"] = picks
    chosen_components["record_entity"] = cid
    used.update(picks)
    return selected, chosen_components, op_scores


def resampled_profiles(occurrences, eligible, multipliers):
    rows_by_form = defaultdict(list)
    all_sections = Counter()
    all_total = 0
    for occ in occurrences["train"]:
        mult = multipliers.get(occ["physical_folio"], 0)
        if mult <= 0:
            continue
        all_total += mult
        all_sections[occ["section"]] += mult
        if occ["form_text"] in eligible:
            rows_by_form[occ["form_text"]].append((occ, mult))
    out = {}
    for form in eligible:
        rows = rows_by_form.get(form, [])
        n = sum(mult for _, mult in rows)
        if n == 0:
            sec = Counter()
            line = entry = closure = kval = 0.0
        else:
            sec = Counter()
            for occ, mult in rows:
                sec[occ["section"]] += mult
            line = sum(occ["line_initial"] * mult for occ, mult in rows) / n
            entry = sum(occ["entry_flag"] * mult for occ, mult in rows) / n
            closure = sum(occ["closure_flag"] * mult for occ, mult in rows) / n
            kval = sum(occ["k_flag"] * mult for occ, mult in rows) / n
        out[form] = {
            "n": n,
            "sections": sec,
            "section_count": sum(v > 0 for v in sec.values()),
            "line_initial_rate": line,
            "entry_rate": entry,
            "closure_rate": closure,
            "k_rate": kval,
            "logodds_H": contrast_logodds(sec, n, all_sections, all_total, {"H"}),
            "logodds_PB": contrast_logodds(sec, n, all_sections, all_total, {"P", "B"}),
            "logodds_B": contrast_logodds(sec, n, all_sections, all_total, {"B"}),
            "logodds_P": contrast_logodds(sec, n, all_sections, all_total, {"P"}),
            "logodds_T": contrast_logodds(sec, n, all_sections, all_total, {"T"}),
        }
    return out


def target_spec(family, form, profile_train):
    if family == "plant_part":
        return "H", {"H"}
    if family == "liquid_material":
        return "P|B", {"P", "B"}
    if family == "record_entity":
        candidates = [(profile_train[form][f"logodds_{s}"], s) for s in ("B", "P", "T")]
        _score, section = sorted(candidates, key=lambda x: (-x[0], x[1]))[0]
        return section, {section}
    return "FORMAL_ENTRY", set()


def section_permutation_null(occurrences, selected_lookup, profiles, reps=1000, single_section_only=False):
    rng = random.Random(SEED + 91)
    rows = []
    folio_structure = []
    for split in ("train", "held"):
        folio_events = Counter(o["physical_folio"] for o in occurrences[split])
        folio_sections = defaultdict(Counter)
        carrier_folio = defaultdict(Counter)
        for occ in occurrences[split]:
            folio_sections[occ["physical_folio"]][occ["section"]] += 1
            if occ["form_text"] in selected_lookup:
                carrier_folio[occ["form_text"]][occ["physical_folio"]] += 1
        all_folios = sorted(folio_events)
        dominant = {}
        for folio in all_folios:
            dominant[folio] = sorted(folio_sections[folio].items(), key=lambda x: (-x[1], x[0]))[0][0]
            folio_structure.append({
                "split": split,
                "physical_folio": folio,
                "events": folio_events[folio],
                "section_codes": ";".join(sorted(folio_sections[folio])),
                "dominant_section": dominant[folio],
            })
        excluded = {f for f in all_folios if single_section_only and len(folio_sections[f]) != 1}
        folios = [f for f in all_folios if f not in excluded]
        ordered = sorted(folios, key=lambda f: (folio_events[f], f))
        bins = {}
        for rank, folio in enumerate(ordered):
            bins[folio] = min(2, (rank * 3) // max(1, len(ordered)))
        bin_folios = {b: [f for f in folios if bins[f] == b] for b in range(3)}

        for form, info in selected_lookup.items():
            family = info["family"]
            target_name, target = target_spec(family, form, profiles["train"])
            if not target:
                rows.append({
                    "split": split, "carrier": form, "family": family,
                    "target": target_name, "observed_logodds": "NA",
                    "null_ge_count": "NA", "replicates": 0,
                    "p_one_sided": "NA",
                    "included_physical_folios": len(folios),
                    "excluded_mixed_section_folios": ";".join(sorted(excluded)),
                })
                continue
            all_sec_observed = Counter()
            form_sec_observed = Counter()
            for folio in folios:
                label = dominant[folio]
                all_sec_observed[label] += folio_events[folio]
                form_sec_observed[label] += carrier_folio[form].get(folio, 0)
            observed_form_n = sum(carrier_folio[form].get(f, 0) for f in folios)
            observed = contrast_logodds(
                form_sec_observed, observed_form_n, all_sec_observed,
                sum(folio_events[f] for f in folios), target,
            )
            extreme = 0
            for _ in range(reps):
                perm = {}
                for b in range(3):
                    fs = bin_folios[b]
                    labels = [dominant[f] for f in fs]
                    rng.shuffle(labels)
                    perm.update(dict(zip(fs, labels)))
                all_sec = Counter()
                form_sec = Counter()
                for folio in folios:
                    label = perm[folio]
                    all_sec[label] += folio_events[folio]
                    form_sec[label] += carrier_folio[form].get(folio, 0)
                value = contrast_logodds(form_sec, observed_form_n, all_sec, sum(folio_events[f] for f in folios), target)
                if value >= observed - 1e-12:
                    extreme += 1
            rows.append({
                "split": split,
                "carrier": form,
                "family": family,
                "target": target_name,
                "observed_logodds": f"{observed:.9f}",
                "null_ge_count": extreme,
                "replicates": reps,
                "p_one_sided": f"{(extreme + 1) / (reps + 1):.9f}",
                "included_physical_folios": len(folios),
                "excluded_mixed_section_folios": ";".join(sorted(excluded)),
            })
    return rows, folio_structure


def carrier_frame_coverage(form, carrier_frames):
    held = carrier_frames["held"].get(form, Counter())
    train = carrier_frames["train"].get(form, Counter())
    total = sum(held.values())
    seen = sum(count for frame, count in held.items() if train.get(frame, 0) > 0)
    return seen / total if total else 0.0, seen, total


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    guarded = read_tsv(GUARDED)
    assert all(not row["page"].lower().startswith("f84") for row in guarded)
    assert all(not row["physical_folio"].lower().startswith("f84") for row in guarded)
    seqdata = json.loads(SEQUENCES.read_text(encoding="utf-8"))
    tree_rows = read_tsv(TREE)
    stem_rows = read_tsv(STEMS)
    metadata, paragraph_loci = paragraph_metadata(guarded)
    entry_set, closure_set, k_set = build_formal_sets(tree_rows)
    occurrences, by_split_locus = build_occurrences(seqdata, metadata, entry_set, closure_set, k_set)
    profiles, all_sections = aggregate_profiles(occurrences)

    all_forms = set(profiles["train"]) & set(profiles["held"])
    eligible = {
        form for form in all_forms
        if profiles["train"][form]["n"] >= 12
        and profiles["held"][form]["n"] >= 6
        and len(profiles["train"][form]["folios"]) >= 4
        and len(profiles["held"][form]["folios"]) >= 2
        and not (profiles["train"][form]["seq_len"] == 1 and form in {"q", "y", "k"})
    }
    frame_maps, carrier_frames = build_frame_maps(occurrences, eligible)
    qualifying, retained_pairs, adjacency, components, component_of = build_graph(frame_maps, eligible)

    # All eligible carrier profiles.
    carrier_rows = []
    for form in sorted(eligible):
        tr, he = profiles["train"][form], profiles["held"][form]
        carrier_rows.append({
            "carrier": form,
            "component_id": component_of[form],
            "component_size": len(components[component_of[form]]),
            "seq_len": tr["seq_len"],
            "entry_flag": f"{tr['entry_rate']:.0f}",
            "closure_flag": f"{tr['closure_rate']:.0f}",
            "k_flag": f"{tr['k_rate']:.0f}",
            "train_n": tr["n"], "held_n": he["n"],
            "train_folios": len(tr["folios"]), "held_folios": len(he["folios"]),
            "train_sections": fmt_counts(tr["sections"]), "held_sections": fmt_counts(he["sections"]),
            "train_line_initial_rate": f"{tr['line_initial_rate']:.6f}", "held_line_initial_rate": f"{he['line_initial_rate']:.6f}",
            "train_logodds_H": f"{tr['logodds_H']:.6f}", "held_logodds_H": f"{he['logodds_H']:.6f}",
            "train_logodds_PB": f"{tr['logodds_PB']:.6f}", "held_logodds_PB": f"{he['logodds_PB']:.6f}",
            "train_logodds_B": f"{tr['logodds_B']:.6f}", "held_logodds_B": f"{he['logodds_B']:.6f}",
            "train_logodds_P": f"{tr['logodds_P']:.6f}", "held_logodds_P": f"{he['logodds_P']:.6f}",
            "train_logodds_T": f"{tr['logodds_T']:.6f}", "held_logodds_T": f"{he['logodds_T']:.6f}",
        })
    write_tsv(OUT / "carrier_profiles.tsv", carrier_rows)

    component_rows = []
    for cid, members in components.items():
        component_rows.append({"component_id": cid, "size": len(members), "members": ";".join(members)})
    write_tsv(OUT / "exchange_components.tsv", component_rows)

    edge_rows = []
    for a, b in sorted(retained_pairs):
        stat = qualifying[(a, b)]
        hf, hw, hc, examples = transferred_pair_stats((a, b), frame_maps)
        edge_rows.append({
            "carrier_a": a, "carrier_b": b,
            "component_id": component_of[a],
            "train_shared_frames": stat["frames"],
            "train_weight": f"{stat['weight']:.9f}",
            "train_internal_weight": f"{stat['internal']:.9f}",
            "train_left_weight": f"{stat['left']:.9f}",
            "train_right_weight": f"{stat['right']:.9f}",
            "train_both_weight": f"{stat['both']:.9f}",
            "held_reused_exact_frames": hf,
            "held_reused_weight": f"{hw:.9f}",
            "held_channels": ";".join(f"{k}:{v}" for k, v in sorted(hc.items())),
            "held_examples": ";".join(examples),
        })
    write_tsv(OUT / "exchange_edges.tsv", edge_rows)

    selected, chosen_components, op_scores = select_pools(profiles["train"], eligible, components, component_of)
    expected_sizes = {"operation": 4, "plant_part": 4, "liquid_material": 4, "record_entity": 5}
    assert {k: len(v) for k, v in selected.items()} == expected_sizes

    label_lists = {
        "operation": ["REIBEN", "KOCHEN_ERWAERMEN", "TROCKNEN", "EINWEICHEN"],
        "plant_part": ["WURZEL", "BLATT", "BLUETE", "SAMEN"],
        "liquid_material": ["WASSER", "WEIN", "OEL", "SALZ"],
        "record_entity": ["GEFAESS", "BAD", "KRANKHEIT", "FRAU", "HEILUNG"],
    }
    selected_lookup = {}
    for family in ("operation", "plant_part", "liquid_material", "record_entity"):
        ordered = sorted(selected[family], key=lambda f: (-profiles["train"][f]["n"], f))
        selected[family] = ordered
        for label, form in zip(label_lists[family], ordered):
            selected_lookup[form] = {"family": family, "label": label}

    # Frozen-pool train bootstrap.
    rng = random.Random(SEED + 17)
    train_folios = sorted({o["physical_folio"] for o in occurrences["train"]})
    bootstrap_counts = Counter()
    bootstrap_family_sizes = Counter()
    for _rep in range(200):
        draw = [rng.choice(train_folios) for _ in train_folios]
        multipliers = Counter(draw)
        boot_profiles = resampled_profiles(occurrences, eligible, multipliers)
        boot_selected, _boot_components, _boot_op = select_pools(boot_profiles, eligible, components, component_of)
        for family, forms in boot_selected.items():
            bootstrap_family_sizes[(family, len(forms))] += 1
            for form in forms:
                bootstrap_counts[(family, form)] += 1

    bootstrap_rows = []
    for form, info in sorted(selected_lookup.items()):
        bootstrap_rows.append({
            "family": info["family"], "label_default": info["label"], "carrier": form,
            "selected_restarts": bootstrap_counts[(info["family"], form)],
            "restarts": 200,
            "selection_rate": f"{bootstrap_counts[(info['family'], form)] / 200:.6f}",
            "pass_075": int(bootstrap_counts[(info["family"], form)] >= 150),
        })
    write_tsv(OUT / "bootstrap_stability.tsv", bootstrap_rows)

    null_rows, folio_structure = section_permutation_null(
        occurrences, selected_lookup, profiles, reps=1000, single_section_only=True
    )
    diagnostic_null_rows, _ = section_permutation_null(
        occurrences, selected_lookup, profiles, reps=1000, single_section_only=False
    )
    write_tsv(OUT / "section_nulls.tsv", null_rows)
    write_tsv(OUT / "section_nulls_dominant_diagnostic.tsv", diagnostic_null_rows)
    write_tsv(OUT / "section_folio_structure.tsv", folio_structure)
    null_lookup = {(r["split"], r["carrier"]): r for r in null_rows}
    boot_lookup = {r["carrier"]: r for r in bootstrap_rows}

    # Family held pair sharing.
    family_pair_rows = []
    transfer_witness_rows = []
    family_shared_by_form = Counter()
    family_held_edges = Counter()
    for family, forms in selected.items():
        for a, b in itertools.combinations(sorted(forms), 2):
            train_stat = qualifying.get(tuple(sorted((a, b))))
            tw = train_stat["weight"] if train_stat else 0.0
            tf = train_stat["frames"] if train_stat else 0
            if train_stat:
                hf, hw, hc, examples = transferred_pair_stats(tuple(sorted((a, b))), frame_maps)
            else:
                hf, hw, hc, examples = 0, 0.0, Counter(), []
            if hf > 0:
                family_shared_by_form[a] += hf
                family_shared_by_form[b] += hf
                family_held_edges[family] += 1
            family_pair_rows.append({
                "family": family, "carrier_a": a, "carrier_b": b,
                "train_shared_frames": tf, "train_weight": f"{tw:.9f}",
                "held_reused_exact_frames": hf, "held_reused_weight": f"{hw:.9f}",
                "held_examples": ";".join(examples),
            })
            if hf:
                for (channel, value), train_counts in sorted(frame_maps["train"].items()):
                    if not (train_counts.get(a, 0) and train_counts.get(b, 0)):
                        continue
                    held_counts = frame_maps["held"].get((channel, value), Counter())
                    if not (held_counts.get(a, 0) and held_counts.get(b, 0)):
                        continue
                    witness = {
                        "family": family, "carrier_a": a, "carrier_b": b,
                        "channel": channel, "exact_frame": value,
                        "train_count_a": train_counts[a], "train_count_b": train_counts[b],
                        "held_count_a": held_counts[a], "held_count_b": held_counts[b],
                    }
                    for split in ("train", "held"):
                        for carrier, suffix in ((a, "a"), (b, "b")):
                            candidates = [
                                occ for occ in occurrences[split]
                                if occ["form_text"] == carrier and (channel, value) in occ["frames"]
                            ]
                            first = sorted(candidates, key=lambda o: (o["locus"], o["chunk_index"]))[0]
                            witness[f"{split}_locus_{suffix}"] = first["locus"]
                            witness[f"{split}_chunk_{suffix}"] = first["chunk_index"]
                            witness[f"{split}_section_{suffix}"] = first["section"]
                    transfer_witness_rows.append(witness)
    write_tsv(OUT / "selected_family_pairs.tsv", family_pair_rows)
    write_tsv(OUT / "transferred_frame_witnesses.tsv", transfer_witness_rows)

    # Matched-frequency controls.
    matched_rows = []
    matched_control_for = {}
    for form in sorted(selected_lookup):
        tr = profiles["train"][form]
        candidates = []
        for other in eligible:
            if other == form or other in selected_lookup:
                continue
            otr = profiles["train"][other]
            if otr["seq_len"] != tr["seq_len"]:
                continue
            flags = (tr["entry_rate"], tr["closure_rate"], tr["k_rate"])
            oflags = (otr["entry_rate"], otr["closure_rate"], otr["k_rate"])
            if flags != oflags:
                continue
            distance = abs(math.log(tr["n"]) - math.log(otr["n"]))
            candidates.append((distance, other))
        if not candidates:
            continue
        distance, control = sorted(candidates)[0]
        matched_control_for[form] = control
        cov, seen, total = carrier_frame_coverage(form, carrier_frames)
        ccov, cseen, ctotal = carrier_frame_coverage(control, carrier_frames)
        drift = js_divergence(profiles["train"][form]["sections"], profiles["held"][form]["sections"])
        cdrift = js_divergence(profiles["train"][control]["sections"], profiles["held"][control]["sections"])
        matched_rows.append({
            "family": selected_lookup[form]["family"], "label_default": selected_lookup[form]["label"],
            "carrier": form, "control": control, "train_logfreq_distance": f"{distance:.9f}",
            "carrier_held_frame_coverage": f"{cov:.6f}", "control_held_frame_coverage": f"{ccov:.6f}",
            "carrier_seen_frame_tokens": seen, "carrier_total_frame_tokens": total,
            "control_seen_frame_tokens": cseen, "control_total_frame_tokens": ctotal,
            "carrier_section_js_bits": f"{drift:.6f}", "control_section_js_bits": f"{cdrift:.6f}",
        })
    write_tsv(OUT / "matched_frequency_controls.tsv", matched_rows)

    # Held operation scores use held z-scales over the eligible inventory.
    held_z_line = zmap({f: profiles["held"][f]["line_initial_rate"] for f in eligible})
    held_z_entry = zmap({f: profiles["held"][f]["entry_rate"] for f in eligible})
    held_op_score = {f: held_z_line[f] + held_z_entry[f] + 0.25 * math.log(max(1, profiles["held"][f]["section_count"])) for f in eligible}

    dictionary_rows = []
    member_passes = Counter()
    for family in ("operation", "plant_part", "liquid_material", "record_entity"):
        alternatives = "|".join(label_lists[family])
        for form in selected[family]:
            info = selected_lookup[form]
            tr, he = profiles["train"][form], profiles["held"][form]
            target_name, target = target_spec(family, form, profiles["train"])
            if family == "operation":
                train_score = op_scores[form]
                held_score = held_op_score[form]
                target_folios = len(he["folios"])
                p_train = p_held = None
                sign_gate = held_score > 0 and he["section_count"] >= 2
                null_gate = True
            else:
                key = "logodds_PB" if target_name == "P|B" else f"logodds_{target_name}"
                train_score, held_score = tr[key], he[key]
                target_folios = len({folio for s in target for folio in he["section_folios"].get(s, set())})
                p_train = float(null_lookup[("train", form)]["p_one_sided"])
                p_held = float(null_lookup[("held", form)]["p_one_sided"])
                null_observed_train = float(null_lookup[("train", form)]["observed_logodds"])
                null_observed_held = float(null_lookup[("held", form)]["observed_logodds"])
                sign_gate = train_score > 0 and held_score > 0 and null_observed_train > 0 and null_observed_held > 0
                null_gate = p_held <= 0.05
            frame_gate = family_shared_by_form[form] > 0
            bootstrap_rate = float(boot_lookup[form]["selection_rate"])
            folio_gate = target_folios >= 2
            member_pass = sign_gate and frame_gate and folio_gate and null_gate and bootstrap_rate >= 0.75
            member_passes[family] += int(member_pass)
            coverage, seen_frames, total_frames = carrier_frame_coverage(form, carrier_frames)
            dictionary_rows.append({
                "family": family,
                "label_default": info["label"],
                "carrier": form,
                "component_id": component_of[form],
                "unit_length": tr["seq_len"],
                "formal_shape": f"entry={int(tr['entry_rate']>0.5)};closure={int(tr['closure_rate']>0.5)};k={int(tr['k_rate']>0.5)}",
                "train_n": tr["n"], "held_n": he["n"],
                "train_folios": len(tr["folios"]), "held_folios": len(he["folios"]),
                "train_sections": fmt_counts(tr["sections"]), "held_sections": fmt_counts(he["sections"]),
                "target_contrast": target_name,
                "train_target_score": f"{train_score:.6f}", "held_target_score": f"{held_score:.6f}",
                "held_target_folios": target_folios,
                "section_null_p_train": "NA" if p_train is None else f"{p_train:.6f}",
                "section_null_p_held": "NA" if p_held is None else f"{p_held:.6f}",
                "single_section_null_observed_train": "NA" if p_train is None else f"{null_observed_train:.6f}",
                "single_section_null_observed_held": "NA" if p_held is None else f"{null_observed_held:.6f}",
                "held_family_shared_frames": family_shared_by_form[form],
                "held_frame_coverage": f"{coverage:.6f}",
                "bootstrap_selection_rate": f"{bootstrap_rate:.6f}",
                "matched_control": matched_control_for.get(form, "NONE"),
                "member_family_gate": int(member_pass),
                "exact_lexeme_gate": 0,
                "status": "DEFAULT_ONLY__LABEL_PERMUTATION_IDENTICAL",
                "named_alternatives": alternatives,
                "independent_observable": "ABSENT__SECTION_CODE_DOES_NOT_OWN_WORD",
            })
    write_tsv(OUT / "mini_dictionary_candidates.tsv", dictionary_rows)

    family_rows = []
    family_pass = {}
    for family in ("operation", "plant_part", "liquid_material", "record_entity"):
        passes = member_passes[family]
        edge_count = family_held_edges[family]
        passed = passes >= 3 and edge_count >= 2
        family_pass[family] = passed
        family_rows.append({
            "family": family,
            "selected_members": len(selected[family]),
            "member_gates_passed": passes,
            "held_shared_pair_edges": edge_count,
            "family_gate": int(passed),
            "status": "FAMILY_COMPATIBLE__LEXEME_PERMUTATION_UNIDENTIFIABLE" if passed else "DEFAULT_ONLY__NO_HELD_FAMILY_SUPPORT",
            "component_id": chosen_components[family],
        })
    write_tsv(OUT / "family_summary.tsv", family_rows)

    # Exact permutation witness: mapping changes, every distributional score remains unchanged.
    permutation_rows = []
    for family, forms in selected.items():
        labels = label_lists[family]
        base_metric = []
        for form in sorted(forms):
            row = next(r for r in dictionary_rows if r["carrier"] == form)
            base_metric.append((form, row["train_target_score"], row["held_target_score"], row["held_family_shared_frames"], row["held_frame_coverage"]))
        signature = hashlib.sha256(json.dumps(base_metric, sort_keys=True).encode()).hexdigest()
        mappings = {
            "original": labels,
            "cyclic": labels[1:] + labels[:1],
            "reversed": list(reversed(labels)),
        }
        ordered_forms = sorted(forms, key=lambda f: (-profiles["train"][f]["n"], f))
        section_objective = sum(float(next(r for r in dictionary_rows if r["carrier"] == f)["held_target_score"]) for f in forms)
        frame_objective = sum(int(next(r for r in dictionary_rows if r["carrier"] == f)["held_family_shared_frames"]) for f in forms)
        for name, mapped_labels in mappings.items():
            permutation_rows.append({
                "family": family, "permutation": name,
                "mapping": ";".join(f"{form}={label}" for form, label in zip(ordered_forms, mapped_labels)),
                "held_section_or_formal_objective": f"{section_objective:.9f}",
                "held_frame_objective": frame_objective,
                "likelihood_signature": signature,
                "delta_from_original": "0.000000000",
            })
    write_tsv(OUT / "label_permutation_witness.tsv", permutation_rows)

    # Deterministic held paragraph.
    by_paragraph = defaultdict(list)
    for occ in occurrences["held"]:
        by_paragraph[occ["paragraph_id"]].append(occ)
    paragraph_rank = []
    for pid, rows in by_paragraph.items():
        hits = [r for r in rows if r["form_text"] in selected_lookup]
        loci = {r["locus"] for r in rows}
        paragraph_rank.append((-len(hits), -len({r["form_text"] for r in hits}), -len(loci), pid))
    best_pid = sorted(paragraph_rank)[0][3]
    witness_rows = []
    for locus in paragraph_loci[best_pid]:
        if metadata[locus]["split"] != "held":
            continue
        chunks = sorted(by_split_locus["held"][locus], key=lambda r: int(r["chunk_index"]))
        forms = [form_text(tuple(r["units"])) for r in chunks]
        annotated = [f"[{selected_lookup[f]['label']}?]" if f in selected_lookup else f for f in forms]
        witness_rows.append({
            "paragraph_id": best_pid,
            "page": metadata[locus]["page"],
            "physical_folio": metadata[locus]["physical_folio"],
            "locus": locus,
            "section": metadata[locus]["section"],
            "eva_clean": metadata[locus]["eva_clean"],
            "unit_carriers": " | ".join(forms),
            "candidate_annotation": " | ".join(annotated),
        })
    write_tsv(OUT / "held_paragraph_witness.tsv", witness_rows)
    paragraph_md = [
        f"# Deterministic held paragraph witness: `{best_pid}`",
        "",
        "Question marks are mandatory: these are the frozen default labels, not readings.",
        "",
        "| Locus | guarded EVA | exact GDT605 carriers | candidate annotation |",
        "|---|---|---|---|",
    ]
    for witness in witness_rows:
        clean = lambda value: str(value).replace("|", "\\|")
        paragraph_md.append(
            f"| `{clean(witness['locus'])}` | `{clean(witness['eva_clean'])}` | "
            f"`{clean(witness['unit_carriers'])}` | `{clean(witness['candidate_annotation'])}` |"
        )
    (OUT / "HELD_PARAGRAPH.md").write_text("\n".join(paragraph_md) + "\n", encoding="utf-8")

    # Concrete counterexamples and closest alternatives.
    occ_by_form_held = defaultdict(list)
    for occ in occurrences["held"]:
        occ_by_form_held[occ["form_text"]].append(occ)
    counter_rows = []
    for row in dictionary_rows:
        form = row["carrier"]
        family = row["family"]
        target_name, target = target_spec(family, form, profiles["train"])
        held_rows = occ_by_form_held[form]
        if target:
            outside = [o for o in held_rows if o["section"] not in target]
        else:
            outside = [o for o in held_rows if not o["line_initial"]]
        if not outside:
            outside = held_rows
        severity_sections = Counter(o["section"] for o in outside)
        chosen_section = sorted(severity_sections.items(), key=lambda x: (-x[1], x[0]))[0][0]
        locus_occ = sorted((o for o in outside if o["section"] == chosen_section), key=lambda o: (o["locus"], o["chunk_index"]))[0]
        neighbours = []
        for other in adjacency.get(form, set()):
            pair = tuple(sorted((form, other)))
            stat = qualifying.get(pair)
            if stat:
                hf, hw, _hc, examples = transferred_pair_stats(pair, frame_maps)
                neighbours.append((stat["weight"], hf, other, examples))
        closest = sorted(neighbours, key=lambda x: (-x[0], -x[1], x[2]))[0] if neighbours else (0, 0, "NONE", [])
        reason = []
        if float(row["held_target_score"]) <= 0:
            reason.append("HELD_TARGET_SIGN_REVERSAL")
        if int(row["held_family_shared_frames"]) == 0:
            reason.append("NO_HELD_WITHIN_FAMILY_FRAME")
        if float(row["bootstrap_selection_rate"]) < 0.75:
            reason.append("BOOTSTRAP_UNSTABLE")
        reason.append("CLOSE_ALTERNATIVE_SAME_FORMAL_GRAPH")
        counter_rows.append({
            "family": family, "label_default": row["label_default"], "carrier": form,
            "counterexample_reasons": ";".join(reason),
            "held_locus": locus_occ["locus"], "held_section": locus_occ["section"],
            "held_chunk_index": locus_occ["chunk_index"],
            "held_line_eva": metadata[locus_occ["locus"]]["eva_clean"],
            "closest_exchange_carrier": closest[2],
            "closest_train_edge_weight": f"{closest[0]:.9f}",
            "closest_held_reused_exact_frames": closest[1],
            "closest_held_examples": ";".join(closest[3]),
        })
    write_tsv(OUT / "counterexamples.tsv", counter_rows)

    decision = "FORMAL_SLOT_ATLAS__LEXEME_PERMUTATION_UNIDENTIFIABLE" if any(family_pass.values()) else "NO_STABLE_LEXICAL_OR_FAMILY_SLOT"
    result = {
        "decision": decision,
        "exact_lexeme_assignments_passed": 0,
        "eligible_carriers": len(eligible),
        "exchange_components": len(components),
        "retained_exchange_edges": len(retained_pairs),
        "train_chunk_events": len(occurrences["train"]),
        "held_chunk_events": len(occurrences["held"]),
        "train_physical_folios": len({o["physical_folio"] for o in occurrences["train"]}),
        "held_physical_folios": len({o["physical_folio"] for o in occurrences["held"]}),
        "family_status": {r["family"]: r["status"] for r in family_rows},
        "family_gate": family_pass,
        "selected_components": chosen_components,
        "held_paragraph": best_pid,
        "input_hashes": {
            "guarded_rows.tsv": sha256(GUARDED),
            "unit_sequences.json": sha256(SEQUENCES),
            "stable_stem_role_summary.tsv": sha256(STEMS),
            "merge_tree.tsv": sha256(TREE),
            "preregistration": sha256(EXP_DIR / "PREREGISTRATION.md"),
        },
        "formal_sets": {
            "entry_q_family": sorted(entry_set),
            "closure_y_dy_aN_families": sorted(closure_set),
            "nonterminal_k_family": sorted(k_set),
        },
        "section_codes": list(SECTIONS),
        "section_code_ceiling": "opaque catalogue strata; no word ownership",
        "f84_or_f84r_rows": 0,
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest_rows = []
    for path in (GUARDED, SEQUENCES, STEMS, TREE, EXP_DIR / "PREREGISTRATION.md"):
        manifest_rows.append({"kind": "input", "path": path.resolve().relative_to(ROOT.resolve()).as_posix(), "sha256": sha256(path)})
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name not in {"ARTIFACT_MANIFEST.tsv", "VALIDATION.json", "REPORT.md", "run_stdout.json"}:
            manifest_rows.append({"kind": "output", "path": path.resolve().relative_to(ROOT.resolve()).as_posix(), "sha256": sha256(path)})
    write_tsv(OUT / "ARTIFACT_MANIFEST.tsv", manifest_rows)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
