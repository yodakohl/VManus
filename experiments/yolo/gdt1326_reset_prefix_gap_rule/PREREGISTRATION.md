# GDT1326 — reset prefix-only gap formatter

Decision note/preregistration11October2026 before fixed-pair witness extraction.
Budget04:24–04:45UTCinclusive prior review, implementation, independent validation
and publication. Nominate only exact ol/oldyfrom existing word profiles. No broad
prefix census, alternative witness search, model fitting or later lookahead repair.

Complete hypothetical family: a shared bijection maps a22-symbol source alphabet
(one symbol may be sourceSPACE)onto22drawing units. Source is any finite string
on this alphabet; unsupported characters are outside the domain. All source
symbols, including the source-space symbol, are written as their mapped drawing.
The encoder inserts visible gaps by a deterministic rule F_p(prefix)after each
written unit, using only the current group prefix. It immediately cuts whenF=1,
then resets to the SAMEinitial state for that page. Fmay have arbitrarily large
or even unbounded prefix memory and may differ by page. No future-unit lookahead,
previous group, intended lexical ending, line position, remaining width, running
group count, random coin or hidden varying state enters the decision.
The reader discards format gaps/LFand inverts the shared bijection; thus this
family preserves its entire source alphabet stream without using source-word
gaps as visible grouping. It is an invented family, not historical attestation.

Finite-stream end may flush an unfinished final group. Physical line wrapping
occurs only BETWEENcomplete formatted groups, never as an extra midgroup cut.
Assume one continuing source stream within a retained physical prose line: no
invisible message end/restart between its groups. Source capitalization and
punctuation are preserved only if among the declared source alphabet symbols;
no literal Latin or general ASCII coverage is claimed or needed for this test.

Necessary condition: a nonfinal emitted group w has F_p(w)=1. If another whole
group on that same page starts with properprefixw, it reaches exactly the same
prefix state and must also cut atw. Contradiction. Hence the nonfinal group set
cannot contain a proper prefix of any emitted whole group. The longer group can
even be a final flush; only the short witness needs positive continuation evidence.
This is the standard prefix-freedom fact applied to OUTERformat groups, not a
new coding theorem. It does not assert that Voynich words are source words.

Data: unchanged1233strict unique22unit groups and915original source-line packets,
with631allowlist. For each reader separately, retain only the preregistered ol
andoldystrings that have an ORIGINAL-index-consecutive following group also in the
strict panel, on the same exact locus. Both compared forms already have definite
outer spaces. Join raw text, unit list, indices, page and separators to915.
Find exact page selectors containing both forms; choose lexicographically first
page, then smallest IDfor each form. Preserve all eligible nominated occurrences
and page lists for audit, but attach no pvalue or independence claim. Do not pool
readers. No available same-page pair givesNO_FIXED_PAIR_CAPACITY, not a new search.
A pair givesPREFIX_STOP_CONTRADICTIONconditional on units/gaps and no hidden end.
No source values or meanings are assigned to ol,oldy,individual signs or SPACE.

Primary indexes the strict cache and joins915. Validator scans original915adjacent
group windows, reconstructs every nominated eligible occurrence and selectedpair,
and checks prefix via raw equality plus explicit unit lists. Hash-bind both programs,
protocol and inputs before extraction. Source-free fixtures distinguish finalflush
from a true internalstop, show a genuinely prefix-free stop set works, and show a
separately stated one-unit-lookahead formatter can escape this obstruction. That
last toy is a LIMITwitness, not a selected native repair.

Predecessors:1234requires prefix-free INNERletter spellings; entire words there
are concatenations ofcodes and may be prefixes of longerwords. Its27entry bound
and1248attainment remain.1196uses known sourceword/vowel-run boundaries;1203uses
sourceword boundary indices shifted+1and anEND. Neither is a prefix-only outer
formatter.1293dedicatedprefix-only signs and1283greedy line geometry retain their
own contracts. The bounded reviewer checked the reset/prefix proof independently
without new native data. Existing ol/oldyprofiles are exposed motivation, not holdout.

Interpretation: a contradiction stops this precise automatic grouping mechanism,
including its larger-memory variants under unchanged inputs. It does not establish
semantic spaces, a language, actual glyph units, natural word boundaries, a minimum
human memory, or the impossibility of simple writing. Ordinary knowledge of intended
words, lookahead or state carried across gaps can change the contract, but are not
automatically fitted. No new images/rawmixedTSVs,f84/f84r/f116v/f1rbody,327/336body,
reserve or semantic relation-edge packet. No changes to old source/grammar failures.
