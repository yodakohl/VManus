# Reg.gr.181: actual shorthand, table and running medical text

Status: **SOURCE_INSPECTED_TARGET_UNTESTED**. This completes the source question
in GREEK1364_DECISION.md; no Greek Voynich reading or decoder was selected.
The source is now substantially more concrete than GDT609's abstract-only
reference. Its old 34-slot technical prior remains unchanged.

## What was actually read

T. W. Allen, *Fourteenth-Century Tachygraphy*, JHS11 (1890),286–293,
[DOI](https://doi.org/10.2307/623435), complete eight-page article and plateX
in the [public volume scan](https://archive.org/details/journalofhelleni10soci).
PDF pages698–705 contain printed286–293; PDF787 is plateX. The article says
five running-text passages exist but prints four numbered I–IV. We retain
that discrepancy rather than inventing a fifth.

Native visual inspection of the original
[Vatican Reg.gr.181](https://digi.vatlib.it/view/MSS_Reg.gr.181): exact labels
219v,265v,284r,XIIIr,XIIIv. Arabic13r was also viewed during locator checking;
it is ordinary running text, not Allen's front note. The front note is on
RomanXIIIr, canvasp0029. The manifest contains other labels beginning284r;
exact label equality, not a prefix, identifies the table at canvasp0599.
The original table and Allen's plateX show the same layout and damage.
Source URLs and byte hashes are in GREEK1364_SOURCE_RESULT.json.

## One connected, readable source sentence

Allen's expanded IV, printed287, gives this initial sentence:

> ἐπίβαλε μέλιτος τὸ σύμμετρον · καὶ βραχὺ ἑψήσεις καὶ διηθήσας δίδου πίνειν

Working translation: add a proportionate amount of honey; boil briefly,
filter, and give it to drink. This is **a historical source translation**,
not an instruction for use and not any Voynich translation. The rest of IV
continues with another preparation and a one-to-double ingredient amount;
the first sentence was selected to inspect a complete short construction,
not as a statistical sample of the source's abbreviation rates.

The original265v places this passage near the bottom. Eight of the eleven
editorial words in the initial sentence retain recognizable letter sequences;
the article's printed diplomatic approximation shows shorthand in τὸ,
σύμμετρον, and the two καὶ tokens. These classes overlap: σύμμετρον contains
both letters and shorthand, so they are not an exclusive token count.
No full glyph-by-glyph independent transcription is claimed. Allen explicitly
expanded ordinary ligatures/abbreviations, preserving shorthand surroundings;
his printed line is therefore unsuitable as an exact stroke inventory.

Three concrete source mechanisms survive this inspection:

| mechanism | source consequence | restriction on transferring it |
|---|---|---|
| tau dots attached to carriers | τ can be supplied to an otherwise written sequence, as in τοῖς and αὐτός in I; dot position may move to avoid iota's dots | preserve attachment and vertical position; a generic dot count loses information |
| two dots below the following carrier for mu | μ is supplied inside an otherwise partly written word; Allen explicitly contrasts this late practice with earlier shorthand | no evidence that any Voynich prefix has this phonetic value |
| a whole-word καὶ note | a compact note coexists with written words in IV and appears in the teaching table | a short isolated form need not be a single letter; it does not identify Voynich `and` |

The table is neither exhaustive nor a consistent letter-to-syllable cipher.
Allen identifies many table entries absent from the running text, two forms
labelled ἐκ, a two-word ὑπὲρ τὰς entry, possible mistakes and another hand's
ἀπό addition. The writer sometimes adds letters already represented in a
note. These are source-specific observations, not permission to add arbitrary
silent or redundant Voynich characters. Uncertain readings remain uncertain.

XIIIr/v combine abbreviated prose and larger drawn characters. Allen partially
reads instructions involving psalms, paper, skins and silk but explicitly leaves
the notes incompletely interpreted. The large drawings are not entries in
the284r syllable table and have not been assigned its values.

## Decision for Voynich

This witness supplies a genuine alternative to direct alphabetic plaintext:
letters, syllables, word notes and attached marks can share one medical book.
It supplies no justified global correspondence between those signs and the
Voynich inventory. Fitting such a correspondence freely would resume the
underconstrained mixed-key problem exposed by GDT610/612; their primary audit
and docs/joint_reading/PROPOSAL.md were checked. A Greek source would not by
itself cure that problem, and the exact 1364 notation is not established for
Voynich by a shared broad appearance.

Therefore no new target test or Greek decoder is started from this source alone.
Retain the original sentence, attachment rules, table and limitations as a
source packet. Reopening needs a stated whole-passage construction with a
bounded common correspondence and additional consequences; it need not begin
with a confirmed word, but cannot assign a separate value to every convenient
whole form. No Voynich data or reserved pages were newly accessed in this review.
Confirmed Voynich words remain0.
