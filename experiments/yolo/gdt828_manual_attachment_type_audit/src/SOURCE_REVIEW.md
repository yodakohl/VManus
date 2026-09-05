# GDT828 independent source review (post-exposure)

Read-only audit of GDT827's fixed admitted-only packet. No new images, pages, corpus queries, lexical assignments, or external services. This was not blind. ZL3b/IT2a/RF1b are alternate readings of one manuscript.

Source: `experiments/yolo/gdt827_joint_core_paragraph_contrast/artifacts/SOURCE_LINES.tsv`; SHA256 `8df7f22589c8b79a778ac038ae901bd746947fe5781177bd7c59e7193a188fb5`. SPEC fixes four windows / 50 loci / 150 reader lines.

## Exact target groups

| Locus | Reading | Source groups |
|---|---|---|
| f81r.19 | ZL3b | `qokedy · sheedy · chedy · qoteedy · olam` |
| f81r.19 | IT2a | `qokedy · sheedy · chedy · qoteedy · olam` |
| f81r.19 | RF1b | `qokedy · shee@152;y · chedy · qoteedy · ol · am` |
| f81r.27 | ZL3b | `sol · chedy · qokedy · olkedy · dol · qokchedy` |
| f81r.27 | IT2a | `sal · chedy · qokedy · olkedy · dol · qokchedy` |
| f81r.27 | RF1b | `s@221;l · che@152;y · qoke@152;y · olkedy · dol · qokchedy` |

All internal target boundaries are DEFINITE_SPACE except RF f81r.19 ol–am, which is UNCERTAIN_SMALL_SPACE. Both target lines have native paragraph start=0/end=0 in all readers. RF .19 shee@152;y is one opaque group. RF .27 has che@152;y and qoke@152;y: the exact chedy–qokedy pair is shared by ZL/IT only. Entity preservation does not establish different authorial words or license symbol normalization.

GDT819 REPORT supplies inherited visual support for .19 middle-group continuity and the small ol/am space, but no diagnostic clause mark or POS. It did not target .27; this review adds no visual authentication there.

## Every exact chedy immediate neighbour

S=DEFINITE_SPACE; U=UNCERTAIN_SMALL_SPACE. Positions are 1-based. These are exact source groups, with unknown meanings left unknown. There are 43 positions / 15 loci: ZL3b 15, IT2a 16, RF1b 12. All right boundaries are definite; four ZL left boundaries are uncertain. No hit is a first/last line group. No cross-line adjacency is inferred.

| Locus | Reading | Position | Left group | Left boundary | Right boundary | Right group |
|---|---|---:|---|---|---|---|
| f75r.33 | ZL3b | 6 | `l` | S | S | `qokain` |
| f75r.33 | IT2a | 4 | `qol` | S | S | `qokain` |
| f75r.46 | ZL3b | 8 | `otol` | U | S | `ol[o:a]r` |
| f75r.46 | IT2a | 8 | `otol` | S | S | `olor` |
| f76r.51 | ZL3b | 9 | `dar` | U | S | `qopchedy` |
| f76r.51 | IT2a | 9 | `dar` | S | S | `qopchedy` |
| f76r.51 | RF1b | 9 | `dar` | S | S | `qopched@222;` |
| f76r.54 | ZL3b | 3 | `or` | U | S | `qolaiin` |
| f76r.54 | IT2a | 3 | `or` | S | S | `qolaiin` |
| f76r.54 | RF1b | 3 | `or` | S | S | `qolaiin` |
| f77r.25 | ZL3b | 7 | `dal` | U | S | `daror` |
| f77r.25 | IT2a | 7 | `dal` | S | S | `daror` |
| f77r.25 | RF1b | 7 | `dal` | S | S | `daror` |
| f77r.33 | ZL3b | 2 | `daiin` | S | S | `qol` |
| f77r.33 | IT2a | 2 | `daiin` | S | S | `qol` |
| f77r.33 | RF1b | 2 | `daiin` | S | S | `qol` |
| f77r.34 | ZL3b | 3 | `shedy` | S | S | `qolchedy` |
| f77r.34 | IT2a | 3 | `shedy` | S | S | `qol` |
| f77r.34 | IT2a | 5 | `qol` | S | S | `qokaiin` |
| f77r.34 | RF1b | 3 | `shedy` | S | S | `qolche@152;y` |
| f77r.35 | ZL3b | 3 | `okaiin` | S | S | `qokain` |
| f77r.35 | IT2a | 3 | `okaiin` | S | S | `qokain` |
| f77r.35 | RF1b | 3 | `okaiin` | S | S | `qokain` |
| f77r.36 | ZL3b | 4 | `qotain` | S | S | `d[o:a]lchl` |
| f77r.36 | IT2a | 4 | `qotain` | S | S | `dolchl` |
| f77r.36 | RF1b | 4 | `qotain` | S | S | `dolchl` |
| f81r.19 | ZL3b | 3 | `sheedy` | S | S | `qoteedy` |
| f81r.19 | IT2a | 3 | `sheedy` | S | S | `qoteedy` |
| f81r.19 | RF1b | 3 | `shee@152;y` | S | S | `qoteedy` |
| f81r.20 | ZL3b | 3 | `qol` | S | S | `qokeey` |
| f81r.20 | IT2a | 3 | `qol` | S | S | `qokeey` |
| f81r.20 | RF1b | 3 | `qol` | S | S | `qokeey` |
| f81r.22 | ZL3b | 2 | `qotal` | S | S | `qol` |
| f81r.22 | IT2a | 2 | `qotal` | S | S | `qol` |
| f81r.22 | RF1b | 2 | `qotal` | S | S | `qol` |
| f81r.25 | ZL3b | 7 | `okal` | S | S | `dy` |
| f81r.25 | IT2a | 7 | `okal` | S | S | `dy` |
| f81r.25 | RF1b | 7 | `okal` | S | S | `dy` |
| f81r.27 | ZL3b | 2 | `sol` | S | S | `qokedy` |
| f81r.27 | IT2a | 2 | `sal` | S | S | `qokedy` |
| f81r.28 | ZL3b | 2 | `qokesdy` | S | S | `qokar` |
| f81r.28 | IT2a | 2 | `qokesdy` | S | S | `qokar` |
| f81r.28 | RF1b | 2 | `qokesdy` | S | S | `qokar` |

## Native paragraph metadata

| Window | ZL3b | IT2a | RF1b |
|---|---|---|---|
| f75r.32–46 | START .32 / END .46 | START .32 / END .46 | no flags |
| f76r.51–56 | START .51 / END .56 | START .51 / END .56 | no flags |
| f77r.25–37 | START .25 / END .37 | START .25 / END .37 | no flags |
| f81r.16–31 | START .16 / END .31 | START .16 / END .23; START .24 / END .31 | no flags |

Thus .19 and .27 lie in different native IT paragraphs within one selection window. ZL puts them within one native paragraph; RF does not settle this. Metadata establishes no clause structure, syntactic scope or shared referent.

## Testable obligations and limits

1. A strictly declared construction in which every chedy is a rightward preposition and the immediately following group its nominal complement collides with fixed MANUAL qokedy=imperative press at ZL/IT f81r.27. This is a conditional type contradiction for that construction, not source-only proof that every reading of on is impossible. A different scoped complement needs one fixed, independently checkable construction. Bare adjacency does not test such a construction; local skipping or press-to-pressure switching has no support.
2. f81r.19 has qokedy followed by sheedy, then chedy followed by qoteedy. No adjacent qokedy–chedy pair occurs. In the fixed eight-entry MANUAL map, sheedy and qoteedy remain unknown; this cannot independently supply a noun required by on or an action-linker construction. Unknown does not mean nominal, finite, or conjunction.
3. TRANSFORMATION becomes, FLOW flows-through and NETWORK joins can be evaluated on the same slots but do not gain validation from leaving qokedy/qoteedy unresolved. The target pair has no independently identified result, path, endpoint, or subject. No global word-order rule is recovered.
4. IT f77r.34 has two exact chedy groups: shedy chedy qol chedy qokaiin. ZL has shedy chedy qolchedy; RF has shedy chedy qolche@152;y. Do not decompose the latter wholes to manufacture the IT sequence. MANUAL on-it-on remains a construction debt, not permission to erase a relation.
5. Exact chedy followed by qokain occurs at f75r.33 in ZL/IT and f77r.35 in all readings. These already exposed contacts do not independently identify water, basin, hand or channel. No packet fact resolves noun identity or the qokedy action sense.
6. ZL's uncertain left boundaries at f75r.46, f76r.51, f76r.54 and f77r.25 constrain universal standalone-word claims. Transcriber agreement is not independent semantic replication.

Reproduction: use csv.DictReader on this admitted-only SOURCE_LINES.tsv; json.loads on groups_json, left_json, right_json, start_json, end_json; select exact whole group == "chedy" and emit neighbours at i−1/i+1. No mixed sealed/unsealed source was opened. Definitions/limits checked against GDT827 src/SPEC.json, src/CANDIDATES.tsv, REPORT.md and GDT819 REPORT.md. No new relation evidence or semantic score is claimed.
