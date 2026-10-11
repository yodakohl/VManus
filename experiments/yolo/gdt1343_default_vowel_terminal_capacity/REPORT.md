# GDT1343 — very little strict terminal capacity for consonant doubling

**CONDITIONAL_TERMINAL_CODA_CAPACITY_BOUND.** The new IDEA1012 writer suppresses
an inherent vowel by doubling a consonant body. That requires every consonant-
final source word to end in two identical complete written units. Only18/31/29
strict native groups have such an ending in ZL/IT/RF respectively. This yields
a narrow necessary source-ending bound, not rejection of every possible source
language and not a native sound or word assignment.

## Fixed result and uncertainty

| Reading | Strict groups N | Final doubles D=M | Strict coda ceiling | Excluded U | Full-raw ceiling under extra assumption |
|---|---:|---:|---:|---:|---:|
| ZL3b |25,564|18|0.0704%|6,354|19.9637%|
| IT2a |29,821|31|0.1040%|1,612|5.2270%|
| RF1b |25,622|29|0.1132%|5,882|18.7627%|

A strict group is completely parseable under the unchanged22working units and
has clear outer seams. Its source word, if this writer is correct, can end in
a consonant only when the two final units agree. These percentages describe
that exact strict subset, NOT a representative estimate of all manuscript words.
They imply no general phonological fact without the hypothetical writing rule.

The last column grants EVERY excluded raw group a possible consonant ending:
(M+U)/(N+U). It additionally assumes exactly one source word for each stored raw
group, including uncertain boundaries. If actual word counts differ, that column
does not apply. It is not a deciphered corpus statistic or confidence interval.
The large reader difference mainly reflects distinct uncertainty eligibility;
readings concern one manuscript and are not independent replications.

Only7/8/7different units have positive final-double counts. Hence assigning any
17units as consonant bodies can retain every observed double; the key-independent
17-body maximum M equals D in each reading. No vowel class or key is selected.

Full exclusion accounts and per-unit counts are in RESULT. Every one of94,855
original Pgroup IDs has a saved classification. WITNESSES retains all78 alternative-
reader terminal-double rows, complete raw forms, units, locations and metadata.
These are not78 independent physical observations.

## The construction and hand-checkable implication

The deliberately invented rule has17consonant bodies and5vowel signs:

- C followed by one fixed default vowel A writes c.
- C followed by another vowel V writes cv.
- C with no following vowel writes cc.
- An unattached V writes v.

At source-word end, a final C necessarily takes the third branch. Its cc is
terminal because no following token remains. A key permutation cannot change
equality. At most17written units can be consonant bodies, giving the sum of the
17largest observed terminal-double counts as a generous bound.

The converse is false: source CACA also writes cc and ends in a vowel. A written
double is therefore possible capacity, not an identified consonant ending.
The relation is ambiguous beyond this example: CV and CAV can both write cv.
A fixed language/lexicon would need to select among exact re-encodings; none is
supplied. Every written string has some preimage, so parseability is no evidence.

Examples inspected after the census include literal doee (f105v.35), shee
(f108v.10) and qokaiii (f107v.40). The last ends in ii despite its three-i run.
No e/i phoneme value is assigned. Parsing uses full ch/sh/ckh/etc units before
comparing endings; this is not an ASCII-character doubling count. The22working
units themselves remain an analytical convention, not a recovered alphabet.

## Research decision

This exact writer remains possible only with correspondingly sparse consonant
endings in the strict matched source population. That is a substantive obligation
for any future independently specified source, not permission to choose a language
or change word grouping after seeing the limit. No language has been tested here.
Do not build a decoder or silently add a word-final exception. Original source
failures remain:1202 already excludes the unchanged four sourceword projections
under even two whole-word spellings; this one-output-per-source-word rule cannot
rescue those comparisons. Their original pooled-screen qualifications remain.

The proposal is different from892/906's freely prefix-decodable fixed CV search
and1219's126trained default cells. Those failures do not automatically reject
this ambiguous law. Conversely, escaping their premises establishes no fit.
The old787additive-profile failure does not reject every compositional word
constructor; it supplies no positive evidence for this particular new rule.

No general ban on inherent vowels, syllabic writing, meaningful content or
repeated signs follows. No selected replacement, historical-use claim, sound
key, new source corpus, native word meaning or semantic relation score. All
current whole-page readings remain exploratory; confirmed lexemes remain0.

## Reproduction and validation

Proposal, proof, scripts, source and allowlist were locked at18:28:01UTC on
11October2026 before the new census. These were already exposed data, not a
blind holdout or public preregistration before calculation. Only the immutable
GDT1342guarded cache was reused; no new raw TSV, image, reserve, f84/f84r/f116v
or f1rbody was opened.

The runner checks1364small abstract source words plus an explicit converse
counterexample before counting. The separately written validator uses a regex
parser, verifies all94,855classifications and all witnesses, and computes M as
D minus the five smallest counts. Source/accounting validation PASS. Its saved
fixture check is not an independent re-execution of the1364source examples.
A separate agent reviewed the general implication, uncertainty convention and
code without looking at native counts; that logical review is not palaeographic
or semantic confirmation. All artifacts retain these distinct scopes.

    python3 experiments/yolo/gdt1343_default_vowel_terminal_capacity/src/run.py
    python3 experiments/yolo/gdt1343_default_vowel_terminal_capacity/src/validate.py
