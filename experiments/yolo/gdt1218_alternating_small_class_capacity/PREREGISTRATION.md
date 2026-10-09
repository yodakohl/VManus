# GDT1218 — prospectively fixed necessary small-class screen

Selected 2026-10-06 00:29:05 UTC; total wall budget 25 minutes including
preparation, implementation, validation and local closure. No target counts for
this hypothesis have yet been taken. Exposed targets are not a holdout.

## Contract and actual unknown

Consider a simple hypothetical instruction writer. Each instruction alternates
one whole group identifying one of 64 plants and one whole group containing the
other six GDT1174 fields (part, condition, operation, medium, amount, duration).
Each plant has exactly one globally fixed whole spelling. Procedure spellings
may overlap plant spellings. No actual native word is given any such meaning.
This is a necessary grammar contract, not a complete 22-glyph writer or an
open-vocabulary language. GDT1174's 64-plant inventory is an invented finite
source domain, not an inferred count of manuscript plants.

Is a fixed class of at most 64 whole forms compatible with strict alternation
in the already exposed fixed target sample? Allow arbitrary phase at every line
start, but no silent internal restart, skipped written groups, spelling variants
or exceptional standalone words. This relaxation makes a contradiction stronger.
There is no dependence on source field frequencies or a specific glyph carrier.

GDT1210 rejected a different paired four-field message model using source type
and top10 frequencies; its plant value appeared in both groups. GDT1211 bounded
one changed group per line. Neither is being reopened. GDT1040 concerns six
fixed prefix productions and retained historical guesses, which are not used.
Root read these primaries and followup pointers, 1174's actual field inventory,
route checks and bounded duplicate searches before selecting this question.
Strongest known concern is large observed type diversity despite a 64-form
class; diversity alone does not prove its members fail to alternate. Positive
motivation is a human-manageable subject plus compound instruction scheme.

## Minimal sufficient certificate and fixed selection

Use only GDT1211 TARGET_SAMPLE_IDS.json: exactly 8000 selected whole groups per
reader, identical to GDT1174. Obtain fields only by selector-first query of the
GDT1170 GUARDED.tsv, explicit SPEC.json allowed pages, columns edition,page,
locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,
right_separator. f84 and f84r forbidden; f116v excluded; no new image or source.
Validate the original sample eligibility, type and top10 counts without changing
selection. Preserve exact forms; readers are separate views of one manuscript.

An edge consists of two selected groups of the SAME reader/page/locus, original
index j and j+1, shared DEFINITE_SPACE, both eligible. No edges across omitted
groups, line boundaries, uncertain seams or reader versions. Exclude self-pairs.
In frozen sample order, greedily retain an edge only if neither exact whole form
has appeared in a retained edge; stop at 65 edges, or exhaust the sample. No
maximum matching, optimizer, alternate ordering, threshold search or repair.

Every edge must contain at least one small-class member. If 65 retained edges
have mutually disjoint endpoint types, any such class has at least 65 members,
contradicting the stipulated limit 64. This is a deterministic certificate, not
a significance test. The class can overlap procedure spellings without escaping
the bound. If fewer than 65 are found, report NOT_EXCLUDED_BY_THIS_CERTIFICATE;
greedy failure to find a certificate does not establish a 64-cover exists.
Report each reader separately; joint contract excluded if any certificate
exists. Concordance is transcription robustness, not independent replication.

## Decision, assumptions and alternatives

A certificate stops this exact 64-form alternating contract before building a
carrier. No certificate leaves only this necessary question unresolved and would
require a complete writer before selection. No automatic 64-to-larger inventory,
spelling alias, grouping exception, or alternative source partition follows.
Actual text may have productive noun forms, context-dependent spellings, several
instruction structures, or different semantic organization; no choice among
these alternatives is inferred. Conditional on cached transcription and definite
seam annotations, not an independent paleographic verification.

This is mathematical adjacency of transcribed groups, not referent identity or
new scored semantic relation evidence. No GDT388 edge-score claim, denotation,
reading, language or reserve admission. Local checkpoint exception applies;
no claim of prior public preregistration or publication. A separately written
validator must requery originals and verify certificate membership, shared seams,
disjointness, counts and greedy choice. Implementation independence only.
