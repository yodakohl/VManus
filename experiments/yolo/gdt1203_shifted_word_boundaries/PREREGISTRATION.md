# GDT1203 — shift each internal source-word boundary right by one character

Preparation2026-10-05 13:11:43UTC; total budget30minutes until13:41:43UTC,
including predecessor review, implementation, validation and local closure.
One fixed candidate. No shifts left/by2, vowel-dependent variants, exception
lists, alphabet fitting or new corpora after inspecting results.

## Decision note and genuinely changed premise
1202excludes at most two whole-word spellings on the four fixed source projections.
1200retains recurrent written parts and1201transparent grouping with preserved
content. None identifies a native meaning or a unique linguistic segmentation.
Here the continuous source-character sequence is unchanged, but an internal word
boundary moves one character right. A group contains the body of a source word
and the first character of its successor, so1202's whole-word-alias contract no
longer applies. This is an invented simple concealment rule, not an attested
medieval custom and not a proposed native reading of dal/dy.

Strongest predecessors:1176–1178already tested whole-short-word bindings;1179
pairs whole short words and tests three complete carriers, all failing;1181keeps
source-word boundaries. Their failures remain.839found no native exact conserved
pair with shifted cuts under its fixed scope; this was a capacity screen, not
this source-forward writer.930's fixed three-cell spacing model stays failed.
1202source-bound failure does not license another arbitrary alias sweep.

Unknown: does this one changed grouping actually satisfy BOTH inherited exact
frequency intervals (types and top10) in all four source books/readers? If no,
stop this exact source-forward rule before any glyph fitting. If yes, retain only
frequency feasibility; a complete sign rendering and known native-form conditions
remain to be justified in a separate decision. No automatic alphabet search.

## Fixed source and complete transform
Use only1177artifacts/SOURCE_TEXTS.json, b4,w1,bs1,gr1. Keep every stored nonempty
word, case, Unicode character, punctuation token and recipe in order. Source means
this expanded-edition projection, not diplomatic or newly independent text.
A character means one Python Unicode code point, without normalization.
For recipe words w[0]..w[n-1], n>=1, append one distinct END unit to the continuous
character stream. Shift each ORIGINAL internal boundary right by exactly1unit.
Keep the original recipe start and the new terminal position. Equivalently:
- one-word recipe: w[0] + END;
- first of multiple groups: w[0] + first character of w[1];
- interior group i: w[i] without its first character + first character of w[i+1];
- last group: w[last] without its first character + END.
Every group is nonempty, even consecutive one-character words and a last singleton.
END is transmitted content of the constructed code, not invisible metadata. It
occurs once, in the last group. It costs one extra abstract code unit per recipe.
No code unit may be silently erased for statistics. Source-character units are
stored as nonnegative Unicode integers; END=-1 is separate and cannot collide.

The decoder has only emitted group sequences and END. Concatenate units, remove
END and move all inner cuts left by1, then recover the original words. No source
word lengths, word types, origin labels, recipe ids or positional semantic values
are provided to the decoder. END alone also determines recipe segmentation in a
continuous group stream. Human example: nimm|salz|vnd|wasser -> nimms|alzv|ndw|asser END.
The observed word body survives except at its first character; its new final
character comes from the next source word. This is a conditional architecture,
not a fit to observed daldy variants or a general account of native word endings.

## Source sampling, invariants and limits
Transform every complete recipe. Count the first8000emitted groups of each book;
these can use the next source word beyond the sample edge, from the same already
exposed full recipe. Retain complete emitted groups for independent reversal,
all sample frequency tables, source hashes and exact sample recipe ranges.
Equality is literal equality of the COMPLETE ordered unit string, including END,
not equality of hidden source tuples or different parses. A fixed injective
prefix-free unit code in the existing22sign repertoire preserves these exact
whole-group frequencies. Such a code can exist for this finite inventory; none
is optimized, rendered or scored here. No extra native sign is assumed for END:
its eventual code must be paid within that repertoire. Length/entropy/q/y/edit
properties and historical usability are not validated by this frequency screen.

Targets:1174artifacts/RESULT.json cached targets only,8000groups in each alternate
reader. Retain original type_ratio and top10_share +/-0.05 intervals. Recover
integer native counts, compare actual types/top10counts to native_count +/-400,
both bounds inclusive. Overall SHIFT_ONE_FREQUENCY_SCREEN_PASS iff all24conditions
(4books x3readers x2metrics) pass; otherwise SHIFT_ONE_FREQUENCY_SCREEN_FAIL.
This is an actual fixed transform, not1202's optimistic upper/lower relaxation.
Include unchanged-word descriptive baseline, but no alternative model selection.

## Assumptions, verification and ceiling
Source-token boundaries including standalone punctuation are fixed assumptions;
other tokenizations or languages are not tested. Recipe segmentation is preserved
and explicitly marked. Actual historical source meaning is preserved only to the
extent already carried by the complete source projection. No native meaning is
assigned. A passing shape census would not establish this as a native cipher.

Independent same-author validator reconstructs output by continuous-stream cut
positions, compares persisted groups, inverse-decodes complete sources, and counts
samples separately. Tiny exhaustive nonempty-word fixtures test singletons and
an explicit negative demonstrates that dropping END permits [a,b]/[ab]collision.
Verify input/contract/run hashes before scoring. No new raw manuscript, image,
word profile, semantic relation, sealed f84/f84r/f116v or reserve access. A relation
packet is not involved. Local construction checkpoint per live-route exception.
