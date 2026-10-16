# IDEA1073 — valid prefix writer; complete fitted text would not identify it

The invented writer and its two teaching examples are internally consistent.
A fixed public follower grammar supplies candidate words; full-word priority
and a mandatory shortest readable prefix permit exact recovery. This is a new
complete contract relative to971's incomplete complement module, not evidence
that Voynich uses it. No native text, image, language or word meaning was fitted.

The useful result of this review is an exact wordbook-only envelope and an
explicit overfitting countermodel **with actual obligatory shortening**. It
changes selection: do not implement a W/G fitter and count successful coverage,
roundtrips or nonzero shortening as evidence for this mechanism. An independently
specified source constraint is needed. That constraint may be hypothetical;
it need not begin with an already confirmed Voynich word.

## The fixed rule and actual checks

At a context q the candidate set is C=G(q). A received nonempty p reads as p
if p itself belongs to C; otherwise it reads the unique member of C beginning
with p, or fails. The writer chooses the shortest prefix of its intended w
that reads back as w. Full w always succeeds. The reader checks canonicality,
then updates q to the reconstructed full word, not the visible abbreviation.
Induction from START proves exact inversion for every legal source path.

The two examples in the unchanged RAW do give:

- ADD BEND ASK BEND CUT BAT DONE -> AD BE A B C BAT D
- ASK CUT BATE ASK CURE DONE -> AS CUT BATE A CUR D

These are artificial teaching strings, not native word assignments. BAT cannot
stand for BATE when both are candidates: the full BAT candidate has priority.
The old934interface collision,983dedicated-marker failure and971missing carrier
are not silently repaired or transferred to this distinct contract.

## Exact possible-prefix envelope from an independent wordbook

Fix a finite W and a word w in W. Let p be a nonempty prefix of w. We ask
whether SOME candidate set C subset W containing w could make p its mandatory
shortest code. This does not yet bind any actual G or complete source path.

For length1, p is possible: take C={w}. For length(p)>1, put t=p[:-1]. Then p
is possible if and only if there is a v in W, v!=w, such that:

1. v begins with t;
2. if p!=w, v does NOT begin with p.

Necessity: if no other candidate starts with t, then t would already uniquely
read w, contradicting shortestness. When p is only a proper prefix of w,
reading p as w also requires that no other candidate begin with p. When p=w,
full-word priority allows a longer rival starting with w.

Sufficiency: choose C={w,v}. The parent t either reads the shorter full v=t,
or remains ambiguous. No shorter prefix can read w first. At p the unique
extension rule reads w if p is proper; if p=w, full-word priority reads w.

For the RAW's existing W, BEND can thus emit B or BE, never BEN or BEND.
BAT can emit B, BA or BAT. BATE can emit B, BA or BATE, never BAT. These are
possible outputs across arbitrary candidate subsets, not jointly realized
outputs of the particular teaching grammar. They provide no native meanings.

The lemma supplies a cheap necessary filter for a genuinely fixed W before
learning G or searching a letter key. Its union of possibilities is not a
proof that one common G can generate an entire passage. The same source word
always has prefix-comparable spellings; native resemblance alone does not
identify such a shared source word. A guessed generic predictability score is
also not the defined candidate-set inclusion used by the monotonicity claim.

## A fitted wordbook can reproduce any finite text, even with real shortening

Let S be the nonempty set of nonempty group strings appearing in an arbitrary
finite desired text. Work under the RAW's stipulated literal alphabet; no
source meaning is assigned. Let P contain every nonempty prefix of every
member of S. Let L be the prefix-maximal members of S, the leaves of that trie.
Choose one fixed alphabet character a and define:

    W = (P minus L) union {u+a : u in L}
    G(q) = W for every q, including START
    F = W

Construct a putative source message by changing every occurrence of a leaf
u into u+a, and retaining every other desired word w unchanged.

For nonmaximal w, all its proper nonempty prefixes and w itself are in W.
Each shorter prefix therefore names that shorter candidate, and full-word
priority forces output w. For a leaf u, all proper nonempty prefixes of u are
in W, but u is absent. Its sole extension in W is u+a, so the shortest code
for source u+a is exactly u. No extension u+a can already lie in P, because
that would contradict maximality. Distinct leaves are prefix-incomparable,
so their extensions cannot collide or create another extension of u.

This handles one-letter words, a singleton S and prefix chains. At least one
leaf occurs in the text, so actual shortening is guaranteed. A single constant
candidate set suffices; there is no per-occurrence grammar table in this proof.

Hand example, a=A:

    Desired types S = {AB, ABC, B}
    W = {A, AB, ABCA, BA}
    Putative source: AB ABCA BA AB
    Written output:  AB ABC  B  AB

The exact output is the desired text, two source types are genuinely shortened,
and the fixed reader returns the putative source exactly. Still, every source
word was manufactured from the desired output. There is no actual translation.
The full constructed wordbook is a paid apparatus of uninterpreted strings;
a compact rule G(q)=W does not make W independent or supply its meanings.

Therefore full text coverage, exact recovery AND nonzero actual shortening,
even together, cannot select1073when its wordbook may be fitted this way.
This is an existence/identification counterexample, not a claim that a medieval
scribe used the artificial dictionary or that every independent source fits.
The RAW already requires independent W/G before a source comparison; the proof
shows concretely why relaxing that requirement would destroy the comparison.

## Old source exclusions remain; no repeated census

Every1073output is a literal source-word prefix under one22character bijection.
The retained native keeees witness therefore requires its source word to contain
four consecutive equal source characters with nonempty flanks. Even the more
generous XU^4Y test in GDT1240 found none in the five fixed source projections.
Those results are inherited, not recounted: b4/w1/bs1/gr1/deot have respectively
19315/18141/21963/21512/6288stored tokens and zero witnesses.

This depends on the old exact whole-group and working-unit premises and the
rare keeees at one physical location, not three independent reader witnesses.
The source projections retain their old editorial/normalization assumptions.
It excludes the unchanged five-source/literal-prefix conjunction, not every
wordbook, language, contextual abbreviation or physically different sign system.
Adding grammar freedom does not create a missing literal prefix in those W.
No new source corpus, word count, key search, decoder or source rerun is selected.

GDT1166's candidate pipeline and1171's order5context instrument stay failed,
with their qualified positives retained. They did not test this author-side
shortest-prefix writer. GDT1183/1184 already executed initial prefix-index/style
writers; their outcomes and paid fragment/counter mechanisms are also distinct.
Their old proposed continuations are not new unexecuted tasks.

## Review and decision

A separate source-only reviewer checked inversion, both RAW outputs, both
necessity/sufficiency of the envelope and the nontrivial leaf-extension
countermodel, including singleton/prefix-chain edge cases. The reviewer read
no native data and authored no program. This is independent logical checking,
not independent manuscript confirmation or historical validation.

Retain1073as a formally supported limited invented construction. Do not select
a source-unspecified W/G fit. An actual independently fixed wordbook/grammar
or a genuinely binding content consequence is needed before the next test;
full coverage and real shortening alone are explicitly insufficient. The
known five-source branch remains contradicted under its old premises. Neither
this formal freedom nor a missing source binding rejects the whole mechanism.

This is a bounded manual proof/selection review, not a new GDT experiment.
There is no retrospective preregistration, new native result, source score,
word meaning or translated passage. The independent producer retained no new
RAW after finding its two other directions already represented by876/952.
Preparation started14:37:27UTC; inclusive review/publication budget25minutes.
The saved review timestamp records the preparation/proof checkpoint; remaining
work is registry/context/privacy verification and publication, not another test.
