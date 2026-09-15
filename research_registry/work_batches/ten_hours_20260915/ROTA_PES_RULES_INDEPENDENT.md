# Independent pes and performance-rule observations

Native inspection began 2026-09-15 at 12:30:40 UTC. The JSON observations were
sealed at 12:38:16 UTC before any producer ROTA_SOURCE_EVENTS file was read.
This receipt records the complete two written pes staves and the boxed/red
performance rules. It does not independently transcribe the rota melody.

Source: [British Library original image](https://live.staticflickr.com/2826/12458897473_6530558074_o.jpg),
Harley 978 f.11v, 1069 × 1575 pixels, SHA-256
`f0dca799f0e46f419b0918b7be6e4443e8cda74ea53ea5a1cf97246f92bb7668`.
Observation JSON SHA-256:
`c943edac727035ff20e52785389f195ded3d6d4419189cf7c058dfd935d423a8`.

**Retained observation:** eight definite noteheads in each pes, including one
ascending two-note ligature in each. The upper part has an ending pause; the
lower has a pause after its first three notes and explicitly continues into
its repeat without an ending pause. Exact numeric durations remain unresolved.
One irregular upper-stave ink cluster and the adjacency of its final boundary
to the rule-box edge are retained as classification qualifications.

## Native order and clef ownership

Both parts own a C-clef and a small adjacent sign read as round b. The upper
stave has seven red rulings; the lower has six. In each, the reference C line
is the third ruling from the top. Do not force both into a five-line staff or
copy a clef's bottom-line index across them. A read-only red-pixel tally
supports the ruling coordinates recorded in JSON; it neither detects notes
nor supplies pitches or durations. Native views used the original image,
without cropping, enhancement, OCR or audio.

The table gives diatonic staff steps relative to each stave's C reference.
Letter names are the conventional interpretation of those positions. Absolute
frequency and octave numbers are not assigned. B is flattened conditional on
the reading of the adjacent b-rotundum sign, whose small shape is less clear
than the note positions.

| Order | Upper pes | Staff steps | Lower pes | Staff steps |
|---:|---|---:|---|---:|
| 1 | F below C | −4 | C reference | 0 |
| 2 | G below C | −3 | B below C | −1 |
| 3 | F below C | −4 | C reference | 0 |
| 4 | G below C, ligature begins | −3 | **Pause** | — |
| 5 | A below C, ligature ends | −2 | F below C | −4 |
| 6 | C reference | 0 | G below C | −3 |
| 7 | B below C | −1 | F below C | −4 |
| 8 | C reference | 0 | G below C, ligature begins | −3 |
| 9 | **Pause** | — | A below C, ligature ends | −2 |

Standalone heads are square or irregularly square with downward stem traces.
The first lower C is less regular in outline. The ascending ligatures contain
two connected heads; their lower-to-upper note order uses the standard reading
of that notation, not horizontal spacing as a duration measure.

The retained order has a concrete relationship. Let A be F–G–F–G–A, and B be
C–B–C–pause. The upper part is AB and the lower BA. This is a pitch/rest-order
observation conditional on the stated notation readings. A common numeric
period and an exact phase offset still require the corresponding duration
interpretations. Exchanging both complete parts between performers is a naming
symmetry; relocating only a pause while fixing the note order is a different
operation.

An irregular dark cluster above the upper lower-note run, approximately
x329–362/y1018–1057, is not confidently a current separate note. It remains an
unclassified ink trace, possibly stray or altered ink. I neither insert a
ninth sung note nor certify an erasure. At the upper right, the vertical music
boundary is close to the black rule-box edge. The red prose independently
requires an end pause even though separating those adjacent strokes is less
secure than the lower internal pause stroke.

## Performance rules

The expanded Latin readings, with compact abbreviation uncertainties recorded
in JSON, support these complete instructions:

- Four companions can sing the rota. It should not be sung by fewer than
  three, or at least two, apart from those singing the pes. Three/four and a
  two-singer fallback are retained; the sentence is not a proof that any
  larger doubling of performers is musically impossible.
- One rota singer starts with the pes performers while the other rota singers
  remain silent. Another starts when that singer reaches the first note after
  the cross, and subsequent singers follow the same rule. This subtask does
  not assign the cross a melody-event index.
- Each is to pause at written pauses, nowhere else, for the space of one long
  note. This names a longa, not a modern beat count. The immediate boxed-rule
  context concerns rota singers; using precisely that duration for each pes
  pause also treats the prescription as shared with the red pes instructions.
- The upper red rule directs one performer to repeat as often as needed,
  pausing at the end.
- The lower red rule directs the other to pause in the middle and **not** at
  the end, then immediately repeat the beginning. The final conjunction may
  be expanded Set/Sed; this does not change the negative or repeat instruction.

No finite performance duration or fixed repetition count is supplied. A
two-pes interpretation follows the two written parts and the contrasting
unus/alius instructions. With the selected two-to-four rota-singer alternatives,
these are four-to-six active parts/performers under the ordinary one-per-part
reading, not two voices in total.

## Rhythm, external collation and limits

The notation preserves more than pitch order, but this audit has not justified
a complete numeric-duration table. Long-note perfection/imperfection, individual
ligature-member values and any shared treatment of the pes pauses must be
resolved or explicitly modelled before a timed event lattice is claimed.
No fixed metre, modern time signature, equal note duration, tempo, or convenient
finite menu of rhythmic alternatives is inserted here.

After the first native view, a public search returned Wikisource pitch
encodings and Latin snippets. That exposure is disclosed; this is independent
of the producer, not blind to public editions. A returned lower-rule snippet
omitted the visible negative, so it cannot override the original. Its numeric
durations were not adopted. [DIAMM's source record](https://www.diamm.ac.uk/sources/434/)
supports the English-mensural classification and variable ruling, but supplies
no individual event durations. A [scholarly transcription of the boxed rule](https://shc.stanford.edu/sites/default/files/2023-05/Reeve%20-%20Stanford%20Poetics%20paper%20May%20%2723%5B16%5D.pdf)
supports the expanded performance reading. No modern performance was accessed.

This receipt establishes a bounded source observation with explicit unknowns.
It does not certify a fully timed score, independently audit the melody, or
supply a Voynich musical reading. The producer's forthcoming complete inventory
can now be compared against these sealed bytes; any disagreement must remain
visible rather than rewriting this observation to agree.
