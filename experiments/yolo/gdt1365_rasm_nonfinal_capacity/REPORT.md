# GDT1365 — A pinned dotless-script projection fails direct fixed-sign rendering

**FIXED_RASM_RENDERING_EXCLUDED_FULL.** Every FULL reading contains all18raw
characters strictly inside words. The independently specified rasm projection
allows at most15restricted or17extended nonfinal classes. Therefore no fixed
one-character rendering of those classes can cover FULL, even allowing class
mergers, reversal, arbitrary per-word reversal and additional word splitting.
This is not a general rejection of Arabic, abjads or historical dotless scripts.

On recurrent forms, the restricted Arabic projection still fails both uniform
directions. The more permissive mixed-direction diversity test and the full
software-domain tests remain CAPACITY_ONLY onGE2; those outcomes are not fits
and do not rescue the FULL failures.

## New source input, separate from manuscript evidence

The public MIT rasm_arch software by Alicia González Martínez and Thomas Milo
is pinned to commit32646fe6e76f581128bb4ac465b4c606ac88cd13. The source-only
review inspected code, documentation and licence. It supplies a complete modern
technical projection, unlike the previously inspected partial Fedeli XML
metadata; it does not supply a historical glyph collation or medical source.

For28ordinary Arabic base letters the bare TextIOpath yields18classes. Its
nonfinal alphabet has15classes; Q,N,Ycan only be emitted at cleaned-token end.
The wider software repertoire addsJ/Oand has20classes/17nonfinal classes.
These extra software-supported categories are not evidence for a historical
Arabic/Voynich alphabet. General input can lose unsupported characters; the
restricted28letterdomain retains length. Returning the original input alongside
the rasm is not a reversible decoding demonstration.

An independently transcribed positional table matched the pinned converter on
all22764synthetic restricted strings of lengths1–3. Another1071synthetic probes
checked the full software character inventory. Corpus-resource access was
explicitly disabled. No bundled Quran edition, private Decotype data, new
medical text or Voynich content entered these source-only tests.

Reproduction uses fetch_source.py for ONLYthree public codefiles andLICENSE;
source_check.py verifies hashes and synthetic behavior. No package installation
or bundled data download. The source licence and provenance are retained, while
the external software itself stays in the local cache.

## The source-independent invariant

Let each archigrapheme class emit one fixed target character. Different classes
may merge; injectivity is NOTneeded for the count bound. The image of15classes
has at most15members (similarly17). BecauseQ/N/Yare never nonfinal:

- forward output has at most15/17distinct nonfinal characters;
- reversing each word permits at most15/17distinct noninitial characters;
- even arbitrary per-word direction permits at most15/17strict-middle characters.

Source token boundaries must remain. Additional cuts cannot move a source-end
symbol into a group's interior, so they cannot evade the bound. Merging tokens,
variable-width codes, extra output controls and multiple spellings perclass are
outside this rendering contract. No assumption that all three terminal classes
actually occur is needed. The overall output capacities are18/20respectively.

## Complete native results

Same old1233strict raw words as1364; no new segmentation selected after counting.

| Reader / panel | Groups / types | All characters | Nonfinal | Noninitial | Strict middle |
|---|---:|---:|---:|---:|---:|
| IT2a FULL |22528 /4272|18|18|18|18|
| RF1b FULL |19321 /3818|18|18|18|18|
| ZL3b FULL |19332 /3773|18|18|18|18|
| IT2a GE2 |19687 /1466|18|16|17|15|
| RF1b GE2 |16786 /1315|18|16|17|15|
| ZL3b GE2 |16865 /1337|18|16|17|15|

| Panel | Restricted18 forward / reverse / mixed | Full20 forward / reverse / mixed |
|---|---|---|
| FULL, each reader |EXCLUDED / EXCLUDED / EXCLUDED|EXCLUDED / EXCLUDED / EXCLUDED|
| GE2, each reader |EXCLUDED / EXCLUDED / CAPACITY_ONLY|CAPACITY_ONLY / CAPACITY_ONLY / CAPACITY_ONLY|

These are36necessary-condition decisions, not independent evidence counts or
probabilities. The readers concern one manuscript. GE2retains wholeforms on≥2
physical leaves and is sensitivity, not error correction or a holdout.

For example, m,n,qoccur strictly inside FULL words, but none does so inGE2.
First saved examples are qokamdy for medialm in IT/ZL(f104v.2G006), aman for RF
(f111v.33G008); iiincheom for medialn in IT(f4v.9G002), otaiinodain in RF
(f2v.1G003), qokaiinos in ZL(f58v.9G006). Raw offsets and all character witnesses
are retained. These post-result examples are not newly image-confirmed, repaired
transcriptions or sound assignments. The strong FULL rejection of full20/mixed
therefore retains material rare-form sensitivity. Restricted18uniform-direction
failures remain onGE2and do not depend solely on those rare internal examples.

## Decision and limitations

Do not optimize a key or source text for this unchanged one-sign rasm rendering
onFULL. The invariant already fails before any vocabulary guess. The18-class
numerical resemblance to the18raw Voynich characters is not support: positional
capacity contradicts the direct rendering.

Do not infer an Arabic language ban or identify any native sign as Q,N,Y.
A different physical atom inventory, variable-length rendering, additional
allographs or removed source boundaries is a different model, not a successful
repair here. No such extension is selected. The GE2capacity survivors have not
passed joint word-pattern, source-frequency, historical or semantic tests.
Old193/194,1228and Fedeli-source limitations remain in their original scopes.
The new finite technical channel does not resolve the earlier historical
transcription/editorial uncertainties.

## Validation and registration

Native protocol, both programs, sourcechecks and inputs were locked at03:43:23UTC
before native enumeration. Known corpus exposure remains; this is a new formal
application, not independent confirmation. The validator froze before reading
primary results, independently reparses cached raw strings, counts positions
and reconstructs all36decisions plus full first-source/offset witnesses:PASS.
Four source-free position fixtures cover singleton, boundary and repeated-event
cases. No source glyph, actual pronunciation or historical conversion is proved.

No new rawTSV, native image, source-language corpus, reserve, f84/f84r/f116v/f1rbody
or semantic edge score. Source files were acquired only from the public pinned
software repository; no public Voynich-solution approach was searched.
