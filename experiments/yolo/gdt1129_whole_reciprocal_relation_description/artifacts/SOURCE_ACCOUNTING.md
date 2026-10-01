# GDT1129 independent source accounting

Source: `experiments/yolo/gdt985_f75v_source_availability_continuation/artifacts/SOURCE_PACKET.json`; SHA256 `2ac5094a1d4394cae01141050912c5ad2cef0ca3d0053918b0294af828eccac0`. The registered packet is unchanged. No author account was read; no target query, image, mixed TSV, reserve, profile census or new segmentation was used. Only these two owned accounting artifacts were written.

The bounded packet has **176 unique native IDs**: IT59, ZL59 and RF58 across the same five physical lines. These are alternate readings of one physical paragraph. Counts describe raw spelling; they do not assign meanings.

| Reader | Groups | Distinct raw whole forms | Repeated spellings | Complete paragraph records | Inherited eligible / ineligible / unavailable groups |
|---|---:|---:|---:|---:|---|
| IT2a | 59 | 39 | 10 | 1 | 59 / 0 / 0 |
| ZL3b | 59 | 41 | 9 | 1 | 12 / 47 / 0 |
| RF1b | 58 | 44 | 5 | 0 | 0 / 0 / 58 |

| Locus | IT groups | ZL groups | RF groups |
|---|---:|---:|---:|
| f75v.38 | 13 | 12 | 12 |
| f75v.39 | 12 | 12 | 12 |
| f75v.40 | 13 | 13 | 13 |
| f75v.41 | 15 | 15 | 15 |
| f75v.42 | 6 | 7 | 6 |

Every row in JSON retains the exact `native_group` dictionary, complete source line metadata and inherited paragraph line metadata when present. The original paragraph records are also preserved. IDs are not aligned by index between different readers: IT `.38` splits `tol sheor`, whereas ZL/RF preserve `tolsheor`; ZL `.42` preserves separate `o` and `l`. IT `otain` versus ZL `okain`, and IT `.40` second `dal` versus ZL `dol`, remain distinct. No join, entity normalization or correction was performed.

Inherited capacity flags are separate from row conservation. IT has all five eligible lines. ZL `.39`–`.42` has 47 groups on ineligible lines; its six uncertain seams remain literal. RF has no complete paragraph record and all start/end flags are zero, so 58 groups remain unavailable for a complete-paragraph score. Fourteen RF groups carry literal entity or brace encodings. This inventory does not decode them or claim every brace encodes uncertain glyph identity. These flags do not refute conditional exploratory authoring.

| Uncertain seam | Exact left raw | Exact right raw |
|---|---|---|
| `ZL3b|f75v.39|G003` → `ZL3b|f75v.39|G004` | `qol` | `sheedy` |
| `ZL3b|f75v.40|G010` → `ZL3b|f75v.40|G011` | `ol` | `sheey` |
| `ZL3b|f75v.41|G006` → `ZL3b|f75v.41|G007` | `ol` | `shey` |
| `ZL3b|f75v.41|G011` → `ZL3b|f75v.41|G012` | `qol` | `cheey` |
| `ZL3b|f75v.41|G014` → `ZL3b|f75v.41|G015` | `or` | `sheolo` |
| `ZL3b|f75v.42|G001` → `ZL3b|f75v.42|G002` | `o` | `l` |

| RF special raw encoding ID | Raw form |
|---|---|
| `RF1b|f75v.38|G012` | `ke@152;y` |
| `RF1b|f75v.39|G006` | `{ch'}eedy` |
| `RF1b|f75v.40|G001` | `dlshe@152;y` |
| `RF1b|f75v.40|G007` | `shee@152;y` |
| `RF1b|f75v.40|G009` | `@152;@221;l` |
| `RF1b|f75v.41|G001` | `s@221;l` |
| `RF1b|f75v.41|G002` | `she@152;y` |
| `RF1b|f75v.41|G004` | `she@222;` |
| `RF1b|f75v.41|G007` | `she@222;` |
| `RF1b|f75v.41|G009` | `she@222;` |
| `RF1b|f75v.41|G012` | `chee@222;` |
| `RF1b|f75v.41|G014` | `@221;r` |
| `RF1b|f75v.42|G002` | `{ch'}ee@222;` |
| `RF1b|f75v.42|G003` | `qol{ch'}ey` |

Exact distinct inventory below contains **56 union spellings**. Zero means absent from this packet branch, not absent from the corpus. JSON supplies every occurrence ID, plus separate repeated-form inventories per reader. Repetition across readers does not add physical evidence.

| Exact raw spelling | IT | ZL | RF |
|---|---:|---:|---:|
| `@152;@221;l` | 0 | 0 | 1 |
| `@221;r` | 0 | 0 | 1 |
| `aiin` | 1 | 1 | 1 |
| `charor` | 1 | 1 | 1 |
| `chee@222;` | 0 | 0 | 1 |
| `cheey` | 2 | 2 | 1 |
| `chey` | 1 | 1 | 1 |
| `chl` | 1 | 1 | 1 |
| `dal` | 2 | 1 | 1 |
| `dar` | 1 | 1 | 1 |
| `dedy` | 1 | 1 | 1 |
| `dlshe@152;y` | 0 | 0 | 1 |
| `dlshedy` | 1 | 1 | 0 |
| `dol` | 0 | 1 | 0 |
| `kchey` | 1 | 1 | 1 |
| `ke@152;y` | 0 | 0 | 1 |
| `kedy` | 1 | 1 | 0 |
| `l` | 0 | 1 | 0 |
| `o` | 0 | 1 | 0 |
| `okaiin` | 1 | 1 | 1 |
| `okain` | 0 | 1 | 1 |
| `okar` | 1 | 1 | 1 |
| `ol` | 6 | 5 | 6 |
| `olchey` | 1 | 1 | 1 |
| `olkain` | 1 | 1 | 1 |
| `olked` | 1 | 1 | 1 |
| `olol` | 1 | 1 | 1 |
| `or` | 2 | 2 | 1 |
| `orol` | 1 | 1 | 1 |
| `otain` | 1 | 0 | 0 |
| `qoin` | 1 | 1 | 1 |
| `qokain` | 4 | 4 | 4 |
| `qokal` | 2 | 2 | 2 |
| `qokar` | 1 | 1 | 1 |
| `qokeor` | 1 | 1 | 1 |
| `qoky` | 1 | 1 | 1 |
| `qol` | 4 | 4 | 4 |
| `qolshey` | 1 | 1 | 0 |
| `qol{ch'}ey` | 0 | 0 | 1 |
| `qoqokeey` | 1 | 1 | 1 |
| `s@221;l` | 0 | 0 | 1 |
| `sal` | 1 | 1 | 0 |
| `she@152;y` | 0 | 0 | 1 |
| `she@222;` | 0 | 0 | 3 |
| `shedy` | 1 | 1 | 0 |
| `shee@152;y` | 0 | 0 | 1 |
| `sheedy` | 3 | 3 | 1 |
| `sheey` | 2 | 2 | 1 |
| `sheky` | 1 | 1 | 1 |
| `sheolo` | 1 | 1 | 1 |
| `sheor` | 1 | 0 | 0 |
| `shey` | 3 | 3 | 0 |
| `tol` | 1 | 0 | 0 |
| `tolsheor` | 0 | 1 | 1 |
| `{ch'}ee@222;` | 0 | 0 | 1 |
| `{ch'}eedy` | 0 | 0 | 1 |

The IT repeat obligations are `ol`×6, `qol`×4, `qokain`×4, `sheedy`×3, `shey`×3, and `qokal`, `or`, `dal`, `cheey`, `sheey` each×2. ZL differs through `ol`×5 and single `dal`/`dol`; RF exact repeats are `ol`×6, `qol`×4, `qokain`×4, `she@222;`×3, `qokal`×2. Distinct whole forms are not a required count of semantic roots: finite reusable composition can cover them, but each whole needs explicit rendering and any residual must be priced.

A compact validator can objectively check the following declared fields. These checks verify accounting under an authored grammar; they cannot discover or confirm that grammar.

| Fields | Objective check | Boundary |
|---|---|---|
| `source_group_id`, `ivtff_group_raw`, `source_group_index`, `left_separator`, `right_separator`, `line_metadata` | Exact equality to pinned source for every row; one row per raw ID, ordered by reader/locus/native index. | Does not establish word meanings or sentence scope. |
| `dictionary_id`, `raw_form`, `value_id`, `overload_ids`, `overload_condition` | Every used form resolves to a declared dictionary record; repeated spelling has one stable value or an explicitly declared finite typed overload; overload declarations and usage can be enumerated. | A declared condition is not evidence that a manuscript occurrence has that condition; arbitrary semantic renaming can evade superficial matching. |
| `rule_id`, `constructor_id`, `input_types`, `output_type`, `arguments`, `output_id` | Declared IDs exist; arity/types match explicit declarations; argument references resolve to prior introduced objects or explicitly priced forward binding; output references are unique and their recorded use can be traced. | Free prose arguments are not machine-checkable meanings. Matching declared types does not establish actual manuscript participants. |
| `ordered_parts`, `whole_residual_id`, `entry_context_condition` | Exact ordered raw substrings concatenate to the unchanged whole; every whole residual and context condition has a finite declared ID and recorded use. | String concatenation is not proven morpheme segmentation or semantic composition; no automatic null-part inference. |
| `contribution`, `later_consumption`, `status`, `barrier_reason` | Nonempty row fields and explicit UNKNOWN/BLOCKED states; every introduced output has a recorded consumer or declared final retained object; unmatched/unconsumed IDs can be listed. | A prose claim of consumption cannot be accepted as proof. A blocked row is accounted for but cannot satisfy complete content construction. |
| `root_inventory`, `rule_inventory`, `default_inventory`, `alias_inventory`, `residual_inventory`, `cost_units` | Count distinct declared IDs and uses; reject undeclared references and duplicate IDs; retain cost categories separately. | Semantic atomicity, hidden defaults and opaque whole-branch records require independent manual review; one dictionary entry can hide multiple assumptions. |
| `alternate_status`, `inherited_anchor_eligible`, `literal_special_encoding`, `adjacent_uncertain_space` | Preserve capacity flags and literal forms independently of author compatibility; alternate coverage counts are checkable. | Compatible alternate readings are not independent physical confirmation or a meaning selector. |

The source checks passed: registered hash, allowed loci, native IDs/indexes, source counts, exact paragraph/raw equality where paragraph records exist, every separator pair and all 15 line starts/ends. All 176 groups and metadata are retained. No semantic pass, relation score or independent confirmation follows. Known GDT985 single-locus and conditional source-availability conclusions remain unchanged.
