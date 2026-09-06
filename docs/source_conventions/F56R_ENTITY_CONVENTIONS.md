# f56r extended-code conventions: a correction to the simplification wording

The local conversion files identify the two codes used in GDT859's detailed
readings, but do not themselves define a relation between the two occurrences.

| STA code | Detailed `STA-Eva_def.bit` | Basic `STA-Eva_Bint.bit` |
|---|---|---|
| Pd | @167; (line114) | p (line164) |
| Pe | @168; (line115) | f (line165) |

`STA-EvaT_def.bit` has no explicit Pd/Pe rows; its distinct Q2 row maps to t
(line50). This says nothing by itself about how a human transcriber decided
which code to use. The source validator's `read_rules()` reads one code/output
pair at a time; `reverse_group()` concatenates individual substitutions while
preserving its supported bracket/tag syntax. Neither operation reconstructs a
cross-group upper connection. The code definitions here are substitutions,
not drawings, palaeographic explanations or authorial symbol identities.

GDT859 preserves the observed first pair as:

- ZL3b/RF1b: `o@167;chal` / `chchs@168;y`.
- IT2a: `otchal` / `chchsty`.

The earlier user-facing phrase "IT simplifies to t" overstated the evidence
for an intentional normalization operation. The precise statement is that IT
contains literal t at corresponding positions, while ZL/RF retain the two
special entities. The supplied basic conversion of those detailed codes would
be p/f, not t/t. No reading is thereby preferred or physically corrected.

Two native viewers' upper-contact judgment and root's qualified manual group
alignment remain as published in GDT859. These conversion rows neither explain
that contact's function nor rule out a convention documented elsewhere. No
external character-description source was searched and no manuscript census,
new image, new entity identity, sound, word or meaning was inferred.

Reproduction: `python3 docs/source_conventions/check_f56r_entities.py`.
The compact JSON records exact table rows/lines and source hashes, and verifies
the existing published raw pair. Root and a separate agent independently read
the table entries and the converter definition; no target data were newly opened.
The historical table, converter and GDT859 bound bytes remain unchanged.

Primary local sources: `transcription/sources/sta/STA-Eva_def.bit`,
`STA-Eva_Bint.bit`, `STA-EvaT_def.bit` in the same directory;
`experiments/semantic_assumptions/validate_source_sta_alignment.py` lines108
and244; `experiments/yolo/gdt859_f56r_initial_bar_separator/REPORT.md`.
