# GDT1378 — Necessary fixed epoch field of a complete calendar writer

## Decision note

IDEA126 now has a primary printed calendar/era example (BSB1483 images3–5).
Prior969/972–974/992 show why a correct source calculation cannot identify a
native writer. Unknown: does any fully readable admitted nine-group prose line
satisfy even the unavoidable epoch-field spelling of this independently drafted
writer? A zero result stops this exact writer in the strict panel before a
large decoder; a positive retains only candidate field capacity. No capacity
is a separate stop. Budget25minutes inclusive of preparation, implementation,
independent validation and publication. No automatic additional fields, broader
records, numeral coding, or source fitting after the result.

## Complete hypothetical writer (source facts versus invention)

Source facts are the six printed addends for1326completed years, six months and
two days, their total484504days, fixed era offset1132959days and combined
1617463days. The following generalized ledger and notation are INVENTED.
They are permitted exploratory hypotheses, not an attested Voynich record.

Inputs: completed year Y=0..9999, calendar month M=1..12 and a valid day d.
Running yearY+1 is leap iff divisible by4, without Gregorian exceptions.
D(y)=365*y+floor(y/4). Let Y=1000h+100c+10t+u. The first four fields are
successive differences of D at cumulative endpoints
0,1000h,1000h+100c,1000h+100c+10t,Y. This telescoping definition preserves leap
remainders; it is a hypothetical generalization, not a newly transcribed table.
F5 is the sum of completed month lengths beforeM in yearY+1. F6=d.
F7=sum(F1..F6), F8=1132959, F9=F7+F8. Exactly nine fields, no omissions/opcodes.

Write each nonnegative integer in canonical base60 with no leading zero cells.
Each cell is written in DECIMAL digits: the first minimally, all later cells
with exactly two digits, including00. Whole zero is `0`. A dedicated separator
joins cells. One global injective map sends ten decimal digits plus separator
to eleven distinct units from the unchanged22 working inventory. A field is
one visible group and a record is ONE COMPLETE nine-group prose line. No
cross-line wrapping, selected substring, field shift or inferred header.

The source example in this invented notation is:

    1:41:27:30 30:26:15 2:01:45 36:31 3:01 2 2:14:35:04 5:14:42:39 7:29:17:43

The historical numeral orders and zero omissions are kept separate in the
source dossier; this line is not represented as a historical quotation.
No word values or Voynich digit assignments are proposed.

## Frozen necessary test and admitted scope

F8 is always `5:14:42:39`: ten units with first-occurrence equality pattern
[0,1,2,3,1,3,4,1,5,6]. Injectivity requires BOTH equalities and inequalities.
A matching seven-symbol pattern extends to an11-symbol table within22units;
that proves only F8 compatibility, not the other fields or one global key.
The separate15/45 ambiguity of freely assigned base60 digit VALUES does not
transfer automatically to this decimal-within-sexagesimal writer.

Reuse the six existing GDT915 DISCOVERY/EVALUATION JSON caches, already exposed;
these old names do not create a new holdout. Readers ZL3b(primary),IT2a,RF1b are
kept separate. Admit631allowlist pages except f1r,f116v and everyf84prefix.
No new rawTSV, image or reserve. Select source metadata first: page admitted,
kindP, source_group_count exactly9, edition matching cache. Then preserve the
entire line's nine original groups without normalization.

Strict eligibility: exactly original indices1..9 and exact corresponding
edition|locus|GNNN IDs; every internal seam bilaterally DEFINITE_SPACE; each
rawgroup has one nonempty complete parse in
`a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh`.
Use full dynamic segmentation, not a prefix-free assumption. Outer line
separators are unconstrained. Missing/uncertain/nonliteral/ambiguous lines
remain UNSCORABLE, not counterexamples. No cross-reader consensus pooling.

For every strict line record rawF8, its unit list/length/pattern, and
MATCH or LENGTH_MISMATCH or EQUALITY_PATTERN_MISMATCH. Retain all strict
mismatches as well as matches and all unscorable reasons. No other field
fitting, calendar enumeration, meaning assignment or significance test.

Per reader: zero strict lines => NO_STRICT_LINE_CAPACITY; at least one strict
line and zero matches => NO_FIXED_EPOCH_FIELD_CANDIDATE; positive matches =>
NECESSARY_FIELD_CAPACITY_ONLY. Publish metadata9line count, strict count,
unscorable count, physical leaf counts and mismatch breakdown. These counts
are conditional spelling evidence, not the remaining size of the language
search space. Even zero strict matches leaves unscorable rows unresolved.

## Validation and retained decisions

Hashlock protocol, code, input spec, prospective reviews and primary source
before the new projection. Independent validator selects source lines again,
checks sourceIDs/units/seams, and compares pairwise equality relations rather
than relying on root's first-occurrence labels. Synthetic positive and negative
patterns verify the exact criterion without a new decoder-control project.
No relationship edge is scored. Old failures and source-only positives remain.
A match would require a separately preregistered full writer test; absence
closes this particular fixed line/field/code contract only. No grammar,
phonetics, calendar content or semantic arithmetic class is generally banned.
