# GDT837: integrated mandatory wholeword control

Does the unchanged GDT836 search implementation recover a previously unused
ciphertext control when its candidate keys must obey mandatory wholeword (W)
precedence? This tests recovery and the added benefit of the constraint separately.
GDT836's Questio capacity stop remains unchanged. No Voynich fitting is involved.

The fixed source is the complete ITTB Summa contra gentiles (SCG), in canonical
reference order. Books I–II (s1–9859) supply discovery; III–IV (s9860–23687) supply
held evaluation. These are annotated source sentences, not historical paragraphs;
legacy JSON field names `paragraphs` and `paragraph_id` preserve compatibility.
All original UD partitions are merged by source identity. A metadata pass excludes
ittb-forma concordances before their payload is parsed. The source commit and
files are pinned in sources/MANIFEST.json. The ITTB train subset was previously
a GDT832 reference: freshness here means a new ciphertext/recovery control, not
an unseen raw corpus. Native Monarchia remains the independent, frozen reference.
The known ITTB u-for-v spelling difference is retained without repair.

ENCODER_SPEC.json fixes source gates, nominal 26 literal / 4 suffix / 8 wholeword
slots, values, mandatory W-before-S-before-L encoding and three opaque key seeds.
All 38 slots are renamed X00–X37; individual roles and outputs are unknown to
both fit arms. Word, atomic and source-sentence boundaries and nominal role counts
are supplied. Suffix choices (12) and wholeword choices (128) are the unchanged
GDT834 reference-derived pools. The objective is the unchanged GDT832 continuous
word-context language model, family factor OFF. This is not a full suffix inverse.

RELAXED and STRICT use the exact GDT836 C++ source. STRICT checks every decoded
discovery word type against every current W entry, including inactive entries,
after each atomic proposal and before score/best-state updates. A matching output
must have been written as that W atom alone. Rejected proposals restore state.
Both arms start from the first strict-compatible initialization, at most 1000
attempts. Rejected initializations are not scored or saved as best. Search RNG
is reset independently. Inherited initialization samples its W values from the
first eight pool entries; the experiment does not alter that limitation.

SPEC.json fixes all 48 fits: three keys, two arms, eight starts, 60000 annealing
steps and four greedy sweeps each. Paired initialization keys, attempt counts
and seeds must agree. Each cell selects its highest discovery objective, with
ties resolved by lowest start. All 48 outcomes and six selections are locked
before held recovery or world-key truth is read. Any initialization exhaustion
stops the whole panel without selections or truth evaluation. No extra restart,
source repartition, normalization change or post-truth selection is allowed.

STRICT must pass on every key: 95% held words, 99% held characters, 90% novel
composed forms, 90% unambiguous novel composed lemma occurrences, every identifiable
active role/output exact, and zero discovery/held W-priority violations. Both
arms use the same GDT834 same-emission role-identifiability domain, without using
STRICT-specific constraints to make its recovery criterion easier. Characters
use wordwise edit distance divided by summed maximum paired lengths, excluding
spaces. Novelty is measured against discovery plaintext. RELAXED recovery is
reported separately and its failure does not block a STRICT pass. Demonstrated
constraint benefit additionally requires a mean held word gain of at least one
percentage point and no loss on any key. Equal successful arms mean recovery
without demonstrated benefit. Three keys share one content split.

The source capacity audit and source generation precede fitting. Gzip artifacts
use canonical JSON, empty gzip filenames and zero timestamps; GENERATION.json
binds compressed and uncompressed bytes. Shared source gold is stored once;
world truth files contain only maps and provenance. The fitter reads discovery
ciphertext and reference resources only. Code, methods, inputs, held ciphertext
commitments and unpublished confirmation commitments are frozen in PREREG_LOCK.
An independent validator reconstructs source counts, scores, selection, key
identifiability, W compatibility and held metrics. Software validation is distinct
from historical recovery. Even a recovery pass does not establish optional
abbreviation, a Voynich language/word, or reopen GDT616 or CDA001.
