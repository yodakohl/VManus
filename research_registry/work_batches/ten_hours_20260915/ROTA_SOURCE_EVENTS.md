# Harley 978 f11v — complete written musical events, conditional timing

Source-only acquisition, 2026-09-15, completed inside the 13:05 UTC checkpoint.
No Voynich text, target image, reserve, proposed alphabet, target length or
note-per-word format was accessed or selected for this work.

The current visible reading contains **73 melody notes and six pause strokes,
plus eight notes and one pause in each of the two pes parts: 97 written events**.
Every event is included below and in [the structured inventory](ROTA_SOURCE_EVENTS.json).
The red entry cross belongs between melody notes MN009 and MN010. The boxed
instruction makes the next rota singer enter at MN010 of the previous singer.
The source admits the selected two-, three- and four-rota-singer alternatives,
with the two pes performers additional to those singers.

This is a complete current pitch/mark inventory with explicit qualifications,
**not a certified single numeric-duration transcription**. The nearby stemless
note attribution in the late melody, a ternary-ligature interpretation, and a
pes prose/score disagreement remain visible. Conditional executions are supplied
to make their consequences inspectable; none is silently promoted to the source.

## Source ownership and receipts

The [British Library's whole original image](https://live.staticflickr.com/2826/12458897473_6530558074_o.jpg)
and [owner metadata](https://www.flickr.com/photos/britishlibrary/12458897473)
identify Harley MS978 f11v. Its SHA-256 is
`f0dca799f0e46f419b0918b7be6e4443e8cda74ea53ea5a1cf97246f92bb7668`
(981,730 bytes). The whole image and enlarged local viewing crops were actually
inspected with native vision. Crops served inspection only; no source image,
pixel coordinates or machine cache paths are included in these deliverables.

[Jamieson Boyd Hurry, *Sumer is icumen in* (Novello, 1914)](https://archive.org/download/sumerisicumenin00hurruoft/sumerisicumenin00hurruoft.pdf),
printed pp28–35, was read, and the complete modern score pp32–35 was viewed.
PDF SHA-256:
`b6064c7ce7b72c740e8a0bfdc2ea7d6c8c3d22577fcce95dac0548d8afc1070a`
(3,197,963 bytes). Its modern score is attributed to W. S. Rockstro, but Hurry
explicitly acknowledges liberties with words and music. It cannot silently
replace the native current layer.

[W. S. Rockstro's original manuscript study in Grove](https://en.wikisource.org/w/index.php?title=A_Dictionary_of_Music_and_Musicians/Sumer_is_icumen_in&oldid=12180580)
was read as text. It supplies explicit rhythmic conventions and an erasure
report. Its complete engraved score was not independently collated here;
there is no invented downloaded-byte hash for the web page.

[Nicolas Meeùs, *Sumer is icumen in*](http://nicolas.meeus.free.fr/MusiqueAncienne/3Sumer.pdf)
was read, including the full p2 melody, pes and rules. PDF SHA-256:
`b0c78c8ff0c2b030ae0ff1c0334bc6a61d19bdac71441e0128c18999f9c0b1d5`
(591,529 bytes). Meeùs names Davison–Apel, *Historical Anthology of Music*,
no42, pp44–45, as his transcription source. It differs from the current
native pitch layer at more than the opening second note. This receipt does
not assert a completed note-by-note collation of that separate edition.

Public Wikisource pitch encodings were consulted for collation/navigation
before this final inventory. They were not an independent blinded witness;
a faulty lower-rule snippet omitted the native negative. No modern audio
performance supplied a duration.

## Native notation versus interpretation

The main melody occupies five physical staves; the pes occupies two more.
The melody staves have six red rulings, the upper pes seven, and the lower pes
six. Each owns a C-clef and a small sign read as B rotundum. The C reference
is counted per stave from its own top, rather than copying a bottom-line index.
The extra upper pes ruling was recognized after the independent reviewer
flagged it, then checked in the original; this is a disclosed correction to
my initial all-six-lines shorthand.

The table separates visible head class from the conditional duration. Pitch
names use reference C4, with the sign interpreted as B-flat. C4 and MIDI are
modern reference conventions; the page writes neither an octave number nor
an absolute frequency. The JSON also records diatonic steps from each C-clef.
Absolute transposition and uniform time rescaling remain equivalences for a
pure interval/relative-duration analysis.

Visible classes: **L** = approximately square head with descending stem;
**b** = untailed lozenge/oblique head; **t** = first descending ternary head
with tractus; **l** = member of a joined binary group; **u** = approximately
horizontal square head without a clear stem; **R** = upright pause stroke.
These are observations, not English word translations or modern duration
symbols. Irregular tilt, weak stems, erased marks and show-through are not
silently turned into extra notes. The upper pes dark cluster remains an
unclassified ink trace; the upper final pause stroke is close to the rule-box
edge, but its end-pause ownership is independently explicit in the red rule.

Joined groups are MN007–MN009 (descending E–D–C, first head with tractus),
MN060–MN061 (descending B-flat–A), P1N004–P1N005 and P2N007–P2N008 (both rising
G–A). The cross follows the whole three-note group, not its first member.
Main pause strokes occur after notes 14, 27, 30, 43, 56 and 73. Pes P1 pauses
after note8; P2 pauses after note3 and immediately repeats after its note8.

## Duration branches and retained conflicts

C0 is an explicit **conditional composite**, not a named complete historical
edition. Its unit is one breve. It reads imperfect longa as2, perfect longa
as3, ordinary breve as1, the ternary group as1+1+1, binary groups as2+1, and
all pauses as3. Extending the boxed one-longa pause rule from rota singers to
both pes rests is an explicit shared-scope interpretation. Modern time groups
used by the code are not manuscript barlines or units of text.

The source uncertainties are retained separately:

1. Hurry p31 realizes the descending ternary group as three equal minims.
   Rockstro's prose instead specifies a dotted minim followed by a crotchet,
   with the third ordinary minim: normalized3/2,1/2,1. C1 changes those first
   two durations and otherwise keeps C0. This is a local sensitivity using
   Rockstro's convention, not a claim to have collated his entire score.
2. Hurry p31 calls both notes of each pes ligature minims, whereas the owned
   score shows semibreve then minim, normalized2+1. Meeùs likewise uses2+1.
   C2 preserves the literal prose1+1 against the drawn score, giving each pes
   a23-breve period. It is a documentary countercase, not an endorsed repair.
3. Near the end of main stave4, the visually horizontal stemless square is
   currently read at MN067 (B-flat), with MN068 (C) oblique. Hurry p28 locates
   a missing longa stem at the penultimate note of that stave and above the
   word “ne”; the ordinal points to MN068 in this head count. Both statements
   are preserved. C0 takes MN066–MN068 as3,2,1. C3 gives the ordinal-location
   reading an explicit constructed sensitivity,2,1,3, using Hurry's
   perfect/imperfect rule. C3 is not an attested fully collated edition.
   This attribution must be resolved or explicitly retained before claiming
   a certified whole temporal score.

These four branches are not asserted exhaustive; their Cartesian product is
not claimed historically licensed. The code does not use matching lengths to
select a branch. It also does not optimize any branch against target data.
The 144-breve melody value is conditional on these stated local assignments,
not a directly written source numeral.

Current and erased layers remain distinct. Rockstro reports an earlier F at
the melody's second note, whereas the current reading is E; he also describes
several alterations on stave4. Meeùs's opening F–F and his early stave4 C-based
passage therefore cannot be copied into this current-layer inventory without
an explicit witness policy. The earlier layer has not been fully reconstructed.

## Complete event inventory

IDs enumerate noteheads separately from rests; physical stave and left-to-right
order provide source ownership. Duration is **C0 only**, in breves. Alternative
values appear in the branch list and structured file; all other C0 values are
held fixed for those conditional calculations. Pause R has no pitch.

| Event | Physical stave/order | Pitch under stated clef convention | Visible class | C0 duration |
|---|---|---|---|---:|
| MN001 | M1/1 | F4 | L | 2 |
| MN002 | M1/2 | E4 | b | 1 |
| MN003 | M1/3 | D4 | L | 2 |
| MN004 | M1/4 | E4 | b | 1 |
| MN005 | M1/5 | F4 | L | 2 |
| MN006 | M1/6 | F4 | b | 1 |
| MN007 | M1/7 | E4 | t | 1 |
| MN008 | M1/8 | D4 | b | 1 |
| MN009 | M1/9 | C4 | b | 1 |
| MN010 | M1/10 | A3 | L | 2 |
| MN011 | M1/11 | A3 | b | 1 |
| MN012 | M1/12 | Bb3 | L | 2 |
| MN013 | M1/13 | G3 | b | 1 |
| MN014 | M1/14 | A3 | L | 3 |
| MR01 | M1/15 | pause | R | 3 |
| MN015 | M1/16 | F3 | L | 2 |
| MN016 | M1/17 | A3 | b | 1 |
| MN017 | M1/18 | G3 | L | 2 |
| MN018 | M1/19 | Bb3 | b | 1 |
| MN019 | M1/20 | A3 | L | 2 |
| MN020 | M1/21 | A3 | b | 1 |
| MN021 | M2/1 | G3 | L | 2 |
| MN022 | M2/2 | F3 | b | 1 |
| MN023 | M2/3 | A3 | L | 2 |
| MN024 | M2/4 | C4 | b | 1 |
| MN025 | M2/5 | D4 | L | 2 |
| MN026 | M2/6 | D4 | b | 1 |
| MN027 | M2/7 | C4 | L | 3 |
| MR02 | M2/8 | pause | R | 3 |
| MN028 | M2/9 | F4 | L | 3 |
| MN029 | M2/10 | D4 | L | 3 |
| MN030 | M2/11 | F4 | L | 3 |
| MR03 | M2/12 | pause | R | 3 |
| MN031 | M2/13 | C4 | L | 2 |
| MN032 | M2/14 | A3 | b | 1 |
| MN033 | M2/15 | Bb3 | L | 2 |
| MN034 | M2/16 | G3 | b | 1 |
| MN035 | M2/17 | A3 | L | 2 |
| MN036 | M2/18 | C4 | b | 1 |
| MN037 | M3/1 | Bb3 | L | 2 |
| MN038 | M3/2 | A3 | b | 1 |
| MN039 | M3/3 | F3 | L | 2 |
| MN040 | M3/4 | A3 | b | 1 |
| MN041 | M3/5 | G3 | L | 2 |
| MN042 | M3/6 | E3 | b | 1 |
| MN043 | M3/7 | F3 | L | 3 |
| MR04 | M3/8 | pause | R | 3 |
| MN044 | M3/9 | A3 | L | 2 |
| MN045 | M3/10 | A3 | b | 1 |
| MN046 | M3/11 | G3 | L | 2 |
| MN047 | M3/12 | Bb3 | b | 1 |
| MN048 | M3/13 | C4 | L | 2 |
| MN049 | M3/14 | C4 | b | 1 |
| MN050 | M3/15 | D4 | L | 2 |
| MN051 | M3/16 | E4 | b | 1 |
| MN052 | M4/1 | F4 | L | 2 |
| MN053 | M4/2 | E4 | b | 1 |
| MN054 | M4/3 | D4 | L | 2 |
| MN055 | M4/4 | E4 | b | 1 |
| MN056 | M4/5 | F4 | L | 3 |
| MR05 | M4/6 | pause | R | 3 |
| MN057 | M4/7 | C4 | L | 3 |
| MN058 | M4/8 | D4 | L | 3 |
| MN059 | M4/9 | C4 | L | 3 |
| MN060 | M4/10 | Bb3 | l | 2 |
| MN061 | M4/11 | A3 | l | 1 |
| MN062 | M4/12 | F3 | L | 2 |
| MN063 | M4/13 | A3 | b | 1 |
| MN064 | M4/14 | Bb3 | L | 2 |
| MN065 | M4/15 | G3 | b | 1 |
| MN066 | M4/16 | A3 | L | 3 |
| MN067 | M4/17 | Bb3 | u | 2 |
| MN068 | M4/18 | C4 | b | 1 |
| MN069 | M4/19 | A3 | L | 2 |
| MN070 | M5/1 | C4 | b | 1 |
| MN071 | M5/2 | G3 | L | 2 |
| MN072 | M5/3 | E3 | b | 1 |
| MN073 | M5/4 | F3 | L | 3 |
| MR06 | M5/5 | pause | R | 3 |
| P1N001 | P1/1 | F3 | L | 3 |
| P1N002 | P1/2 | G3 | L | 3 |
| P1N003 | P1/3 | F3 | L | 3 |
| P1N004 | P1/4 | G3 | l | 2 |
| P1N005 | P1/5 | A3 | l | 1 |
| P1N006 | P1/6 | C4 | L | 3 |
| P1N007 | P1/7 | Bb3 | L | 3 |
| P1N008 | P1/8 | C4 | L | 3 |
| P1R01 | P1/9 | pause | R | 3 |
| P2N001 | P2/1 | C4 | L | 3 |
| P2N002 | P2/2 | Bb3 | L | 3 |
| P2N003 | P2/3 | C4 | L | 3 |
| P2R01 | P2/4 | pause | R | 3 |
| P2N004 | P2/5 | F3 | L | 3 |
| P2N005 | P2/6 | G3 | L | 3 |
| P2N006 | P2/7 | F3 | L | 3 |
| P2N007 | P2/8 | G3 | l | 2 |
| P2N008 | P2/9 | A3 | l | 1 |

## Complete operative instruction inventory

This covers the musical execution instructions in the black box and the two
red pes directions. Expanded Latin is a reading with abbreviation alternatives,
not a diplomatic glyph transcription. The source's English lyric and Latin
sacred contrafactum are separately written content. They are not translated
or reduced to note labels by this inventory. A later explicit music-content
language would need to declare that subset rather than claim a whole-page
lyric translation.

**R01 — black ruled instruction box, opening clause.** Hanc rotam cantare possunt quatuor socii.

Four companions may sing the rota.

The clause says four can sing; it does not prohibit human doubling or prove an absolute maximum.

**R02 — same box, second clause.** A paucioribus autem quam a tribus vel saltem duobus non debet dici, preter eos qui dicunt pedem.

It should not be sung by fewer than three, or at least two, apart from those who sing the pes.

Meeus prints aut where native expansion is read vel; operational alternative unchanged.

**R03 — same box, Canitur autem sic / Tacentibus clause.** Canitur autem sic. Tacentibus ceteris, unus inchoat cum hiis qui tenent pedem.

With the others silent, one begins together with those who sustain the pes.

Independent audit expands Cantatur; producer/Meeus Canitur. No operative distinction claimed.

**R04 — same box, Et cum venerit clause; red cross in main stave1.** Et cum venerit ad primam notam post crucem, inchoat alius, et sic de ceteris.

When that singer reaches the first note after the cross, another begins; likewise the others.

**R05 — same box, final Singuli clause.** Singuli vero repausent ad pausaciones scriptas et non alibi, spacio unius longe note.

Each pauses at the written pauses and nowhere else, for one long note.

Immediate boxed context is rota singers; extension of its numeric realization to pes pauses is an explicit shared-scope assumption.

**R06 — red instruction immediately right/below upper pes.** Hoc repetat unus quociens opus est, faciens pausacionem in fine.

One repeats this as often as needed, making a pause at the end.

Independent audit and Meeus print repetit; initial producer expansion repetat is retained as a provisional alternative; repeat behavior unchanged.

**R07 — red instruction to right/below lower pes.** Hoc dicat alius pausans in medio et non in fine, set immediate repetens principium.

The other sings this, pausing in the middle and not at the end, but immediately repeating the beginning.

Independent audit and Meeus print dicit; initial producer expansion dicat is retained as a provisional alternative; non is retained.


No source clause supplies a tempo, finite repetition count, exact total
performance duration or universal consonance prohibition. The selected2–4
rota singers plus two pes produce4–6 active parts. The ordinary rota reading
repeats the main melody; the explicit pes instructions require their repeats.
The execution below covers a complete common period after all selected
entries, not a purported source-prescribed stopping time.

## Independent comparison and full pes relationship

The independent [pes/rule report](ROTA_PES_RULES_INDEPENDENT.md) and
[observation JSON](ROTA_PES_RULES_INDEPENDENT.json) were sealed before the critic
read this producer's inventory. Their received hashes are respectively
`77a11f3833d49f6b6ad0f872f5a5856786faddaaf9ce846d04f89748d8fc0c86`
and `c943edac727035ff20e52785389f195ded3d6d4419189cf7c058dfd935d423a8`.
I read those files only after writing my event matrix. The exact canonical
[precomparison matrix bytes](ROTA_SOURCE_EVENTS_PRECOMPARISON.json) remain
recoverable: SHA-256
`2ff05f993c8ffcba901184bf811557ad604f4e497f785a5d80fedce3b37163fd`.
That hash identifies the event array, not an earlier full report wrapper. The
same event array remains in the final JSON; comparison annotations are outside it.
The upper ruling correction was already prompted by a reviewer message and
is not represented as independent agreement.

All18 pes note/pause positions and both rising ligatures agree. The independent
reader retains more caution about the upper stray ink and adjacency of its
final pause to the box edge; those cautions are preserved above. Minor expanded
verb forms differ, with no claimed difference in operative instruction. Exact
numeric durations were not independently resolved.

Let **A = F–G–F–[G,A rising ligature]** and **B = C–B-flat–C–pause**.
P1 writesAB and P2 writesBA. This equality preserves pitch position, classified
note/stem type, corresponding ligature structure and the required pause;
it is stronger than comparing pitches alone. It is conditional on the native
classifications just recorded. Under any *shared, rotation-equivariant*
interpretation of corresponding notated events in their circular contexts,
the complete timed P2 sequence is a rotation of P1. This theorem does not
require the two blocks to have equal durations.

Under C0/C1/C3, A=B=12 breves, so the rotation is exactly half the24-breve
period. Under the retained C2 prose countercase, A=11 and B=12: the whole
period is23 and the rotation11, while the main entry interval stays12.
Thus full event rotation survives the source prose/score conflict, but
half-period phase and alignment to rota entries do not follow without a
numeric reading. If corresponding notational symbols were given unrelated
per-part durations, the result would no longer be forced; that is precisely
the shared-interpretation dependency, not an independently known cipher key.

## Conditional executions and fixed rivals

The [source-only code](rota_source_events.py) fixes all branches and these
rivals before calculating their outputs: successive entry delay increased
by one breve; upper-pes end pause swapped with its preceding note; complete
main note/rest event cycle reversed with each pitch-duration pair retained.
The latter holds the baseline entry delay fixed. All preserve written note
counts. None is a calibrated null over possible languages or compositions.

Each branch is run with2,3and4rota entries, plus both pes from time zero.
A half-breve grid represents the finite fractions exactly. After sufficient
warm-up, the code compares a complete common period:144breves for C0/C1/C3,
3312breves for C2 (LCM of144and23). Outputs include full-sequence digests,
first differing cells and exact signed pairwise interval/rest differences.
There is no harmony-ranking metric, dissonance ban or subjective score.
**Initialization was not separately compared:** the reported receipts start
after all baseline and rival entries; they do not audit the tick0-to-warm-up
transient. The initialization prescription remains in the rule inventory.

The table shows differing signed-interval-or-undefined cells against each
branch's own baseline; rest-induced undefined values are explicitly counted.
These are descriptive exact differences, not p-values. Every fixed rival
changes the conditional performance. Knowing that a modified known score
differs from itself does not identify unknown manuscript content.

| Branch | Rota singers | Entry shift | Pes pause swap | Main reversal |
|---|---:|---:|---:|---:|
| C0 | 2 | 376 | 180 | 1284 |
| C0 | 3 | 1226 | 234 | 2348 |
| C0 | 4 | 2460 | 288 | 3684 |
| C1 | 2 | 375 | 180 | 1284 |
| C1 | 3 | 1225 | 234 | 2348 |
| C1 | 4 | 2459 | 288 | 3686 |
| C2 | 2 | 8646 | 4752 | 29388 |
| C2 | 3 | 28136 | 6264 | 53788 |
| C2 | 4 | 56518 | 7776 | 84444 |
| C3 | 2 | 380 | 180 | 1272 |
| C3 | 3 | 1236 | 234 | 2332 |
| C3 | 4 | 2466 | 288 | 3668 |

The useful source result is a finite, owned note/mark sequence with a concrete
cross-entry marker and an independently supported coupled pes rule. The
remaining unknown is a completely justified numeric realization of every
mark, especially the late stemless attribution and pes prose/score conflict.
A globally shared compositional reading can legitimately be proposed without
already identifying a word, but this receipt supplies neither a target owner
nor a code. It does not certify that a free melody plus delayed copies would
provide enough semantic restriction for decipherment.

Verification checks all97events, all73main pitches across the independent
physical-stave and duration-group representations, exact fractional timing,
all source pause positions, and the pes rotations. The code consumes no
external data at execution time. Run `python rota_source_events.py` from this
folder, or pass its repository-relative path from the repository root.

Final structured inventory SHA-256: `3923d12c26de3d309bef06cfbd1732985ae8d5ba133adc21f1633ff56fb8f34a`.
Source code SHA-256: `97d2bf4a4f5ce2ba6aba70d65db08536e778ff05a7b14564f46908a69abf9f71`.
