# GDT1343 — terminal capacity of the default-vowel doubling writer

Decision before code/count: IDEA1012 provides a concrete new ambiguous writing
relation. Does its mandatory final consonant doubling have appreciable capacity
in existing exact native groups? This is a necessary bound, not a model-fit test.
Small capacity restricts admissible source-word endings before building a decoder;
large capacity would leave this obstruction weak. No capacity value identifies a
source, key or meaning, and no threshold is invented afterward. No decoder or
new control corpus follows automatically. Budget includes preparation, proof,
implementation, validation and publication, ending by18:45UTC2026-10-11.

The complete raw proposal is DEFAULT_VOWEL_DOUBLING_WRITER_RAW_20261011.json.
There are17consonants and5vowels under one unknown bijection onto the existing
22working units. CA (A is one fixed inherent vowel) writes c, CV (other vowel)
writes cv, bare C writes cc, unattached V writes v. Greedy source lookahead is
fixed. One source word is one complete output group, with no word-end deletion,
fusion, punctuation, extra marker, hidden token or changed group boundary.
Ambiguous inversion is deliberate; cc also comes from CACA. All written strings
have some preimage, so parseability cannot support this writer.

Necessary theorem: if a source word ends in C, its last forward step writes cc.
Therefore consonant-final source words are no more numerous than written groups
whose last TWO COMPLETE working units agree. The converse is false. In addition,
the doubled unit must be one of17consonant bodies: maximize the count over any
17of22units by summing the17largest final-double counts. This generous upper
bound is invariant under the unknown key. No choice of vowels/phonemes is fitted.
Report both the loose all-double bound and the17-body bound, even if identical.

Read only GDT1342's already guarded SOURCE.json.gz (all94855admitted P groups).
Verify its frozen byte hash and179-selector provenance, never reopen mixed raw
TSV. f84/f84r remain sealed; f1r andf116v excluded. No new image or reserve.
Use longest-match parsing of the fixed complete22units from the raw proposal;
no cleaning/entities or ASCII-letter substitution. A strict group needs a full
parse and both seams in DEFINITE_SPACE/LINE_START/LINE_END. Source uncertainty
and boundary uncertainty stay in the denominator accounting as exclusions.

For each reading separately report total Pgroups, strict groups N, excluded U,
all final doubles D, counts by final unit, and M=sum17largestcounts. Strict-set
consonant-final fraction is at most M/N, conditional on the model and retained
units/groups. This is not a population estimate. Also report (M+U)/(N+U) as a
maximally permissive bound ONLY under the additional convention that every
excluded stored raw group still corresponds to exactly one source word and each
could end in a consonant. This convention does not adjudicate uncertain spaces;
if actual word counts differ the full-raw bound does not apply. No inverse mean
or language identification follows. Do not pool alternate readings.

Save a classification for every input ID, all strict terminal-double witnesses,
summary and uncertainty counts. Retain metadata for the witnesses. A separately
written validator must reconstruct classification with a different tokenizer,
source hashes, complete ID coverage, all witnesses and both arithmetic bounds.
Small source-free checks of the theorem and its false converse precede census;
they are not native evidence. No semantic relation packet or significance test.

Prior review: forms/composition baseline;787specificadditive-profile failure is
not all composition;892/906prefix-code grammar;1219contextualCV writer;1202fixed
four-source frequency bound. The old1202source comparisons remain excluded for
an unchanged one-output-per-token instantiation; no alternate corpus or target
band is selected. This experiment quantifies a new code-specific native necessary
capacity, not a rerun or rescoring of those sources. Whole-word labels and native
sound values remain unassigned. Historically exposed cache, not blinded holdout.
