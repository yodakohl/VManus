# GDT624 / GDT845 count reconciliation

Resolved: **829 = 816 exact raw groups + 10 collapsed bracket alternatives + 2 removed brace annotations + 1 removed inline metadata tag**.

The GDT624 and GDT631 page allowlists are equal sets of 179 selectors. GDT624's runner counts the ZL3b `eva` token field, not an edition union; its alternative-reader counts are separate. Neither runner filters source kind for the inventory. All 13 discrepant source records are kind P.

Independent comparison used multiplicity Counters keyed by page, locus and surface, not token index (cleaning can alter indices). GDT624 GRID_OCCURRENCES contains 829 rows. GDT845 HITS restricted to ZL3b and regex `^(?:qo|o)?[kt](?:ch|sh)e?d?y$` contains 816. There are exactly 13 old-only occurrences, each multiplicity one, and zero raw-only occurrences. Every one maps to exactly one saved raw ZL3b group whose `clean_ascii_fragments` field equals the old whole surface, with fragment count one.

| Locus | Raw source group | Historical surface |
|---|---|---|
| f103r.26 | `qot[ch:ee]y` | `qotchy` |
| f106r.42 | `ok{e'e}chedy` | `okchedy` |
| f107r.6 | `ok[che:eee]y` | `okchey` |
| f108r.7 | `ok[che:eee]y` | `okchey` |
| f115r.13 | `<@H=3>tchedy` | `tchedy` |
| f22v.14 | `qotch[y:?]` | `qotchy` |
| f32v.2 | `tch[y:o]` | `tchy` |
| f34r.8 | `{ch'}otchy` | `otchy` |
| f49v.12 | `qot[ch:ee]y` | `qotchy` |
| f4v.4 | `qok[sh:ch]y` | `qokshy` |
| f53r.7 | `qok[ch:ee]y` | `qokchy` |
| f66v.13 | `ok[ch:ee]dy` | `okchdy` |
| f66v.2 | `t[che:{chh}]dy` | `tchedy` |

The inline tag case `<@H=3>tchedy` on f115r.13 is metadata removal, not a disputed glyph reading. Therefore it would be misleading to describe all 13 as uncertain words. The current exact-source contract deliberately excludes it because literal raw equality fails; any normalized-word follow-up must declare metadata handling rather than silently changing GDT845.

Both source TSV inspections used `./vmanus-exp query-tsv` with explicit page allow-values and explicit output columns, plus both f84 and f84r prefix exclusions. The old occurrence query selected829/skipped forbidden0/skipped nonallowed0. The raw atlas query selected9376/skipped forbidden2122/skipped nonallowed103972 for the 12 explicitly named pages containing the 13 differences; edition/locus restriction occurred only after the guarded selector stage. No images, new pages, web requests, or old-file edits.

`src/SOURCE_AUDIT.json` contains all 13 witnesses, category membership, and input hashes. This is a source-count correction only; it neither validates the old semantic glosses nor changes the 48-cell occupancy result. Retrospective reproducibility package; no prospective preregistration.
