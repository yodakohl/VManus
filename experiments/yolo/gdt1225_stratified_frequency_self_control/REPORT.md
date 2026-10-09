# GDT1225 — pooled frequency bands do not cover every large stratum

**POOLED_FREQUENCY_BANDS_NOT_PORTABLE_TO_ALL_LARGE_STRATA.** The existing
hand=2 category fails the fixed two-frequency screen in all128page-order
samples in each of the two readings with sufficient capacity: IT2a and ZL3b.
Twelve other scoreable reader/category cells meet the registered122-of-128
criterion. Twenty-five cells have fewer than8000eligible groups and remain
NO_CAPACITY. Separate reconstruction of every count, ID hash and decision:
PASS. This limits a comparison procedure; it identifies no word meaning.

## The specific failure

| Reading, hand=2 | Eligible groups | Types in8000, range | Fixed acceptable types | Top10 occurrences, range | Joint passes |
|---|---:|---:|---:|---:|---:|
| IT2a |9480|1865–2046|2051–2851|1385–1564|0/128|
| ZL3b |8202|1933–1965|2100–2900|1453–1504|0/128|

The type count is below the unchanged lower bound in every sample of both
readings. The top-ten count additionally exceeds its upper bound in63IT2a
samples (bound1465) and all128ZL3b samples (bound1430). These failures overlap;
they are not independent events to add. RF1b hand=2 has7794eligible groups
and was not scored or resized. The labels are existing source metadata, not
new palaeographic assignments or evidence that an individual hand caused
the difference. Topic, section, spelling and other factors were not isolated.

## All sufficiently large categories

| Reading | Field=value | Eligible | Joint passes | Type range | Top10 range |
|---|---|---:|---:|---:|---:|
|IT2a|currier=A|8536|128/128|2414–2542|1267–1360|
|IT2a|currier=B|21285|128/128|2071–2478|1092–1391|
|IT2a|section=H|9382|128/128|2455–2555|1179–1282|
|IT2a|section=S|11300|128/128|2402–2665|981–1151|
|IT2a|hand=2|9480|0/128|1865–2046|1385–1564|
|IT2a|hand=3|11370|128/128|2395–2642|994–1139|
|RF1b|currier=B|17943|126/128|2083–2429|1091–1307|
|RF1b|section=H|8140|128/128|2468–2500|1230–1264|
|RF1b|section=S|9816|128/128|2415–2608|1042–1142|
|RF1b|hand=3|9801|128/128|2400–2593|1049–1144|
|ZL3b|currier=B|18349|128/128|2100–2452|1079–1401|
|ZL3b|section=S|9724|128/128|2394–2623|985–1115|
|ZL3b|hand=2|8202|0/128|1933–1965|1453–1504|
|ZL3b|hand=3|9762|128/128|2393–2614|987–1107|

RF1b CurrierB has two individual low-type exceptions but126joint passes,
so it meets the prespecified operational criterion. The other eleven passing
cells pass128/128. No section/hand intersection was selected after seeing
these values. All39capacities, including unknown hand=@, and every sample
are retained in RESULT.json. ZL3b sectionH has7994eligible groups: even this
six-group shortfall remains NO_CAPACITY rather than a changed sample size.

## What changes for the next writer

A single pooled8000-group frequency profile cannot serve as the sole universal
hard requirement for each individual register or source book. The fixed filter
rejects an actual large native category under every declared page-order sample
in both scoreable readings. Future source comparisons need a justified
comparison unit specified before the candidate outcome. This block does not
choose a favorable hand, reader, new band or replacement target.

The old source-conditioned failures remain exactly as registered. In particular,
1202still proves its optimistic two-alias bound for its four fixed source
projections against its fixed target. No old writer has been rescored on
hand=2, and these data do not show that any of those writers now fits. They
also do not prove that manuscript differences arise from source mixing.

1213still passes128/128under pooled sampling; all its sample counts and
ordered-ID hashes reproduce here.1223still has its separate cross-reading
full-profile failure and matched-reading diagnostic.1193/1195conditional
whole-form alphabet contradictions do not depend on the frequency screen
and remain unchanged. No general natural-language or meaningful-writing
family is promoted from this methodological result.

## Contract, reconstruction and limits

Selected05:53:26UTC after bounded primary/duplicate review; locked05:58:26
before data projections or results. The total work budget includes preparation
conservatively from05:49and local closure by06:34UTC. The fixed contract
uses all observed values of currier, section and hand separately, without
intersections. Capacity is checked per reading and category. Each scoreable
cell uses the same128seeds0..127,8000groups, exact whole forms and±400count
bands against its own original1174reference.122passes is an operational
threshold, not an independently estimated95%error or significance level.

The word projection is the unchanged1170cache. Metadata were separately
read through selector-first query-tsv using the same179explicit allows; no
word column was requested from the metadata table. All94,855cached prose
groups joined uniquely by edition/locus/group index with matching page.
Total eligible counts remain IT29,821,RF25,622,ZL25,564. The1174anchor
matches all24,000saved1211orderedIDs, and all128pooled1213samples reproduce.

The validator imports neither the runner nor the old metrics. It uses a
separate regex unit parser, page buckets and incremental frequency counting.
Every39capacity, scoreable-cell sample/count/hash and decision matches.
This is same-author software validation, not independent native confirmation.

Samples overlap heavily, particularly for the8202-group ZL3b hand=2 pool.
The three readings concern one manuscript; several metadata categories also
overlap. The result concerns this exposed filtered scope and its working
units, not every ink token or unobserved hand. No images, reserves, f84/f84r,
f116v, new historical source, relation packet or word meaning were used.

Reproduce in an isolated checkout with no existing RESULT.json, then run:

```bash
python experiments/yolo/gdt1225_stratified_frequency_self_control/src/run.py
python experiments/yolo/gdt1225_stratified_frequency_self_control/src/validate.py
```

Source hashes, specification, preregistration, locked code, all compact
results and validation are retained. This is a local construction checkpoint
under the4Octoberinstruction; no public release is claimed. No automatic
calibration expansion or decoder repair is selected. Confirmed native words:0.
