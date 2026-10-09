# GDT1295: local deterministic allography needs at least15source letters

**ALL_READERS_SMALL_LOCAL_ALLOGRAPH_ALPHABET_EXCLUDED.** Under the fixed rule,
all three alternate transcriptions independently require at least15different
underlying letter values. Even retaining only conflicts supported on at least
two distinct physical leaves gives a13-letter lower bound. Thus the proposed
at-most11-letter explanation cannot generate these groups by this local,
deterministic shape-choice rule. No native alphabet or letter value is identified.

## Precisely which writing rule
Each source letter writes exactly one visible working unit. A single global
inverse ψmaps each visible unit to one source letter, permitting several visible
variants per source letter. The forward form can depend arbitrarily on PAGE,
whole-word UNITLENGTH, exactUNITINDEX, and the left/current/right SOURCEletters.
Word boundaries are preserved; BOS/EOS are distinct fixed sentinels. The model
therefore allows positional spelling and different page styles, but no random
choice, longer history, whole-word identity, insertion/deletion, contextual
inverse or different word/unit segmentation. These are explicit hypotheses,
not established facts about the manuscript.

If two different visible centers x/y share the same visible neighbors,page,
length and index, they cannot decode to the same letter: that would make every
input of the deterministic forward rule identical while its outputs differ.
Each such pair is an inequality edge on the22visible units. Any valid ψmust
color adjacent vertices differently. A clique of15therefore needs15source
letters. Edges may originate on different pages because ψis global, even though
the forward rule can depend on page. Neither source sounds nor a language are fitted.

| Reader | Complete groups / positions | Matching contexts with different centers | FULL edges / clique | DISPERSED edges / clique |
|---|---:|---:|---:|---:|
|ZL3b|19332 / 89732|6334|171 / 15|159 / 13|
|IT2a|22528 / 102247|7317|177 / 15|167 / 13|
|RF1b|19321 / 86585|6234|178 / 15|161 / 13|

FULL uses every exact conflict. DISPERSED is the preregistered subgraph requiring
at least two physical leaves per edge, with each original conflict still matched
within its exact page/length/index/flank cell. It is a support diagnostic, not
transcription correction, an error rate or independent confirmation. The chosen
FULL15-clique has105edges, including3ZL/5IT/3RFedges supported on only one physical
leaf. These fragilities remain visible. The minimums15and13are LOWERBOUNDS on a
possible source alphabet, not fitted alphabet sizes or constructed writers.
The three readers remain alternate readings of one manuscript.

## Concrete examples from the ZLgraph
The k/t edge has815exact contexts on82physical leaves. Its first saved example
is f100r.13G003 qokeey versus f100r.14G003 qoteey: same6unitlength, index2, flankso/e,
samepage. The ch/sh edge has641contexts on90leaves; its first example is cho versus
sho at f100r.27G003/f100r.23G009, both2units with BOS/o flanks. The l/r edge has
747contexts on88leaves; its first example shol versus chor is at f100r.15G002/G004,
both3units with o/EOS flanks atindex2. The differing more-distant first unit in
that last pair is deliberately outside the tested local function. It cannot be
silently exported to an unrestricted whole-word spelling rule.

These examples illustrate formally different required values UNDERthe contract;
they do not prove k/t,ch/shor l/r are distinct phonemes or assign them meanings.
The graph also does not prove a missing edge means interchangeable forms.

## Maximum clique is not a complete decoding
The computed maxima are exact for the six frozen graphs. A valid coloring is
only a necessary condition: collapsing neighbor units may create additional
same-source-context collisions absent from the literal-neighbor graph. An odd
cycle likewise has clique2but needs3colors. Thus even a15coloring, if supplied,
would not demonstrate a writer; no coloring optimization or native key is run.

The source-free controls include a genuine same-frame conflict, a page change
that must not create one,62words from a valid two-letter/three-shape contextual
writer, a merged-neighbor converse counterexample, and the odd-cycle distinction.
No existing unsupported body/connector identity from928was reused.1204concerned
whole By/Bdy variants between external whole words;1254used146e-placement events
and had unique BOTHkeys;883imposed equalities on latent block endpoints. Their
original stops and positives remain separate from this new inequality bound.

## Reproduction and decision
Only unchanged1233GROUPS.json.gz:61181complete strict-interior Pgroups,278564unit
positions, rawDEFINITE_SPACEoutside, unique22unitparses. No native TSV query,
image,newpage,sourcecorpus,normalization,sealed/reserved material or meaning.
The code/spec/protocol were hash-locked before the one enumeration. The primary
uses keyed contexts and branch-and-bound maximum clique. The independent checker
reparses every raw string, sort-groups all contexts, reconstructs every edge/support
and witness, verifies each claimed clique, and exhausts all(M+1)-subsets to prove
no larger clique plus lexicographic tie selection.2,887,583subsetchecks and all
sixgraphs PASS; numerical/source verification is not independent palaeography.

Stop the exact small-alphabet local-allograph explanation. Preserve the broader
possibility of ordinary language, larger source alphabets, voluntary variation,
longer-context spelling and different physical glyph units without selecting a
repair. Do not increase a color cap, add context fields, fit a decoder or score a
new source automatically. Work remains local under4October instruction; the
requested ten-hour interval continues and has not yet elapsed.
