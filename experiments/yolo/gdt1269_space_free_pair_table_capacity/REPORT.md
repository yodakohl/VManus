# GDT1269 — arbitrary visible spacing does not rescue a small pair table

**ALL_SMALL_PAIR_TABLES_EXCLUDED.** On the fixed old23-snippet packet per reader,
every tested global configuration requires more than32distinct two-unit code
entries. The most generous lower bounds are70IT2a and72ZL3b, both attained by the
NO_SINGLETON configuration. Allowing one single-unit control cannot lower them.
These are necessary lower bounds, NOT exact minimum workable codebooks.

The result permits codes to cross every visible word and line boundary. It also
permits each observed snippet to start/end halfway through a pair, so no actual
word or paragraph boundary is inferred. What fails is the stated small constant
pair-code family, not every spacing-based or meaningful writing system.

## The proposed human procedure and the proof
A writer has a fixed table of at most32two-sign entries, optionally with one
single-sign control h. No pair starts with h, although h may be its second sign.
Source symbols are encoded by lookup; display spaces may then be inserted anywhere.
A reader discards display spaces and reads h singly, otherwise two signs at a time.
The actual source-symbol values are unassigned.32is a bounded table contract,
not a general limit on what a medieval person could learn.

We concatenate the unchanged working units of each retained old paragraph in
stored reading order, ignoring visible spaces and line breaks. A continuous
observed fragment can begin at a code boundary (phase0) or inside an incoming
pair (phase1, skip its first unit). Both parses are retained. A final incomplete
pair is ignored; a control at a reached code boundary is read normally.

For each fragment, every pair TYPE appearing in BOTH parses must be somewhere in
the true global dictionary, whichever phase is correct. Union these mandatory
types across fragments. This cannot overstate the necessary dictionary: it even
allows different favorable phases for different snippets without demanding that
they form one globally consistent code stream. We repeat for no control and all
22possible h choices. A global renaming merely permutes these cases and pairs.

The mandatory TYPE need not occupy the same position in both parses. For example,
ZL's first saved NO_SINGLETON witness for(a,i) occurs at offsets34and15 of the
f103r.18–20snippet, respectively in G006andG003 of f103r.18. Both conditional
locations are stored; neither individual position is declared the true code cut.
No source letter or meaning is assigned to that required pair.

The order of set operations matters. For abstract snippets aba and bab with no
control, each intersection is empty; dictionary{ab}could explain them with
opposite starting phases. Intersecting aggregate phase dictionaries instead of
unioning the per-snippet intersections would falsely force both ab andba.
Both implementations and a dedicated fixture enforce the correct order.

## Every configuration, no favorable-marker selection

| Single control | IT2a mandatory pair types | ZL3b mandatory pair types |
|---|---:|---:|
|none|70|72|
|a|133|128|
|cfh|73|76|
|ch|130|127|
|ckh|117|100|
|cph|92|90|
|cth|94|87|
|d|134|131|
|e|132|128|
|f|73|92|
|i|129|128|
|k|125|132|
|l|127|125|
|m|90|98|
|n|118|125|
|o|138|128|
|p|130|131|
|q|135|129|
|r|121|127|
|s|116|113|
|sh|135|122|
|t|121|125|
|y|137|128|

The two packets contain3293and3420working units respectively. Their23paragraphs
per reader were previously selected as1259rank-certificate witnesses, not as a
representative random sample or an untouched holdout. For this exact capacity
contradiction, a sound counterexample subset suffices. The readers are alternative
transcriptions of the same manuscript, not independent replications. RF was not
in the inherited own-paragraph packet and is not silently reconstructed here.

The lower bound does not construct a70/72entry writer. These counts are not a
native alphabet-size estimate or confirmation of605's98learned BPEunits. Other true-phase pairs may
require additional entries, and a global assignment may fail for other reasons.
Larger codebooks, homophony beyond the entry cap, multiple single-unit controls,
contextual tables, variable-length codes, a changed reading order or different
physical units remain outside this exact test. None is automatically selected as
a repair. No phonetic alphabet, syllabary, word meaning or historical use follows.

## Predecessors and assumptions retained
1234/1235/1267used whole-group membership in a code monoid. This test expressly
drops visible-group/code-boundary alignment; its different necessary bound cannot
be substituted for those older decisions.001's old fixed blocks reset inside each
visible word, retain short last blocks and fit many block types homophonically
to a language model. Its CONTINUE_BLOCK_CIPHER_UNSTABLE remains unchanged, not a
blanket historical failure. No old decoder, target map or language fit was rerun.

The source1259integer-balance proof is not a parity or code theorem and plays no
logical role here; only its already validated raw certificate packet is reused.
Every interior group is retained in order. Independent validation checks source
row continuity, complete per-row group indices, exact raw unit segmentation,
old count vectors and both-phase provenance. No unknown symbol was removed and
no disconnected source excerpts were joined within one snippet.

Exact working units are still an assumption: ch and ckh are each one working
unit here, not respectively two/three ASCII characters. The result is conditional
on that reading and input integrity; it does not measure ink or diagnose rare
transcription errors. No error allowance or rare-form deletion was introduced.

Before this selection a stricter penlift-grouping idea was stopped from existing
primaries:1263's full22-unit connectivity leaves no fixed nonempty class that
always ends a group;1243also reports ten internal white gaps in three fixed f45r
groups. This was a manual consequence/retrieval, not a new image or census, and
not a rejection of normal cursive writing with internal pen lifts.

## Verification and closure
Protocol, both executable programs, immutable inputs and the source-free proof
review were hash-locked before the native pair count. Beforehand,43045contiguous
clips of short legal streams from19small codebooks never forced an absent pair.
Named fixtures cover h as second unit, partial edges, singletonruns, empty clips
and the union/intersection trap. A separate pending-state scanner and dynamic
unique working-unit parser independently check all46reader/configuration cases,
2116snippet-phase parses and5312mandatory-type witness records. PASS.
These counts are computational checks, not independent semantic evidence.

RESULT.json records all cases; PAIR_CERTIFICATES.json.gz preserves each complete
phase list and both conditional source locations of every mandatory type.
Run src/run.py then src/validate.py in an isolated copy. No new rawTSVquery,
image, source text, native scope, f84/f84r, f116v or reserved confirmation.
No new relation or semantic edge score; this is a finite logical code-capacity
certificate. Confirmed native meanings0.

Decision: stop at-most32fixed pair-entry tables with zero or one such control,
even under arbitrary decorative spacing and unknown snippet phases. Do not
interpret this as proof that visible spaces are linguistic word boundaries.
The allocated20:28–21:13UTCwindow includes preparation through local closure.
Local4Octobercheckpoint only; no commit/push or automatic larger-table search.
