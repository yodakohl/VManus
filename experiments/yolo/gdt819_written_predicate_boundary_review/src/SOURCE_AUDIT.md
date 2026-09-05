# GDT819 source and registration audit

Scope: guarded projections of f76r, f77r and f81r only; f84/f84r explicitly forbidden.
No new page, glyph equivalence, word meaning or semantic validation.

## Material correction: RF ASCII fragments are not automatically source groups

The separator-aware atlas is
`experiments/semantic_assumptions/results/source_separator_transcription.tsv`.
Its `ivtff_group_raw`, edition/locus/group index and left/right separator fields
retain the upstream source notation. The defining producer is
`experiments/semantic_assumptions/build_source_separator_transcription.py`:
line 41 includes semicolon in `SPLIT_RE`; lines 72–81 apply the legacy cleaner;
lines 83–158 preserve source groups; line 199 maps groups to ASCII fragments.
The accompanying `SOURCE_SEPARATOR_TRANSCRIPTION_SPEC.md` explicitly identifies
multiple ASCII fragments within one group as cleaner-created, nonmanual boundaries.
Neither producer nor historical output was rerun or changed here.
This pass integrates an already documented source correction into the current
five-locus semantic trial; it is not discovery of a new normalizer defect.

| RF locus / source group | Exact source group | Legacy ASCII output | Boundary conclusion |
|---|---|---|---|
| f76r.23 / 4 | `che@152;y` | `che y` | One source group, not two source words. |
| f77r.12 / 1, 2 | `soltee@152;y`, `qotee@152;y` | `soltee y`, `qotee y` | Each source group has an artificial internal ASCII boundary. |
| f77r.12 / 4, 5 | `che@152;aiin`, `che@152;y` | `che aiin`, `che y` | Two source groups, not four source words. |
| f77r.12 / 8 | `che@152;` | `che` | Extended entity disappears without producing an extra ASCII fragment. |
| f77r.34 / 4, 8 | `qolche@152;y`, `@206;aiin` | `qolche y`, `aiin` | Artificial boundary in the former; erased initial entity in the latter. |
| f77r.35 / 7 | `che@152;aiin` | `che aiin` | One source group, not two source words. |
| f81r.19 / 2 | `shee@152;y` | `shee y` | One source group, not two source words. |

The mechanism is the semicolon terminating `@number;`, not removal of a question
mark. `@152;` remains an uninterpreted extended entity: it is not automatically
replaced by EVA d. Source grouping does not itself establish linguistic wordhood.

Fresh current cross TSV confirms f81r.19 RF exactly
`qokedy shee y chedy qoteedy ol am`. The last two groups are different from the
artificial shee/y split: RF writes `ol,am`, an uncertain small source space.
An earlier working-message summary saying RF ended in fused `olam` was corrected
immediately; it is not the current source reading.

For f77r.35, RF has eight source groups, just as ZL/IT, but genuinely reads
`qotaiin` in group 6. The source-native tail is
`sheedy.qotaiin.che@152;aiin.chealy`, not five independently separated groups.
This removes one objection to a four-group completion without proving any of its
four meanings. RF f77r.12 also does not supply four independently separated
`che / aiin / che / y` words; the ZL `chedaiin.chedy` interpretation still differs
from IT `shedaiin.chedy`. Neither reader may silently overwrite the other.

The f76r.23 doublet remains ZL/IT `chedy.chedy` and RF
`chedy.che@152;y`; f77r.34 adjacent `qokaiin.qokaiin` remains in all three.
The actual IT split `qol.chedy` at f77r.34 is also retained; it is not the same
phenomenon as RF `qolche@152;y` becoming two ASCII fragments.

## Complete paragraph and line registration

Fresh ZL page projection has 137 loci: f76r 56, f77r 50, f81r 31.
The complete target P streams contain 74 P loci:

| Target(s) | Whole source P span | P loci | Previous/next P at target |
|---|---|---:|---|
| f76r.23 | f76r.1–38 | 29 | .21 / .24 |
| f77r.12 | f77r.9–24 | 16 | .11 / .13 |
| f77r.34, .35 | f77r.25–37 | 13 | .33 / .35; .34 / .36 |
| f81r.19 | f81r.16–31 | 16 | .18 / .20 |

f76r.1–38 includes nine separately retained L records:
.4, .7, .10, .14, .18, .22, .27, .31, .37. In particular f76r.22 is the
immediate preceding record, not the preceding prose line of f76r.23.
f77r.1–8 are labels; f77r.49–50 are additional labels after the final P stream.
Line numbers must therefore not be registered by counting prose alone as loci.

All five target loci have source paragraph-start/end flags 0/0. Their whole P
streams have explicit first/last flags. ZL f77r.35 contains ordinary dot-separated
groups throughout and no special recorded clause marker before `sheedy`.
This is a transcription fact, not proof against an unpunctuated clause boundary.
Image observations must register the complete line and neighboring prose lines;
neither an image gap nor a transcription dot decodes a clause or word.

## Reproducible bounded inspection

Run `./vmanus-exp query-tsv` on the atlas with `--selector page`, explicit
`--allow f76r --allow f77r --allow f81r`, both forbidden prefixes, and columns
`source_group_id,edition,locus,page,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw,clean_ascii_fragments,clean_ascii_fragment_count,legacy_surface_positions_1based,legacy_mapping_status`.
Only after that guarded projection select the five target loci. The guard selects
3296 permitted group rows; no other source payload enters this audit.
The current ZL and cross line TSVs are independently queried with the same guard.
The atlas specifically maps the frozen pre-grounding cleaner; current cross rows
are retained independently rather than assumed identical by definition.
