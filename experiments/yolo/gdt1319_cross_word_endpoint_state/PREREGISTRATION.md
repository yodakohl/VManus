# GDT1319: can visible word endpoints carry a continuing state?

Decision note10October2026. Bounded selection preceded the10:12UTCclock checkpoint;
inclusive work window approximately10:00–10:40UTC covers preparation, implementation,
verification and publication. No larger-marker, exception or reset search at outcome.

Unknown: can a nonconstant global state be explicitly passed from one complete
word to the next using only the left word's last working unit and the right
word's first working unit? The exact contract has two arbitrary global functions:
I(g)=entry state of a word beginningg; O(g)=exit state of a word endingg.
For every retained contiguous word pairuv, require O(last(u))=I(first(v)).
State alphabet may be finite or infinite. IandOare separate even for the SAMEglyph,
including one-unit words; no equality within a word is assumed. Middle payloads
and internal actions are unconstrained. No source letters or meanings are assigned.

For each reading build an undirected bipartite graph on role-labelledI_g/O_gnodes.
Every retained seam adds one equality edge. Each active connected component must
have a single state value; assigning different values to different components
satisfies all equations. Thus component count is the EXACTmaximum number of distinct
state values among observed endpoint nodes, not the minimum size of a full writer.
If there is one active component, stop this INFORMATIVE explicit continuity channel
on this panel. Ifmorethanone, retain only equality capacity, not actual state labels
or a successful writer. If no edges, reportNO_CAPACITY. Unused nodes remain free.

Inputs: unchanged1233strict Pgroups with unique22unit parse and definite spaces
on both sides, all current179selectors, readers separate. Rejoin each original915
ID, raw form, original group index, metadata and both separators. Retain only
original-index-consecutive groups within one exact source locus, never across
lines, omitted groups, uncertain spaces or drawing gaps. No edge extension1314.
All here are historically exposed; no independent replication or reserved test.
No rawTSV, image, f84/f84r/f116v/f1rbody or old327/336body access.

Assume every retained seam passes the state unchanged. A real record/reset boundary
inside those seams would change this hypothesis; no unmarked reset is inserted
after seeing a counterexample. Functions are global within each reading, not varied
by page, hand or occurrence. Different marker sizes, code values conditioned on
whole words, probabilistic preferences, unmarked memory or alternate segmentation
remain outside. A constant observed interface does not imply a meaningless text:
its interior payload and other channels may still carry arbitrary information.

Retain all pair records, directed(role-source,role-target) edge multiplicities,
selector lists, first exact witness per edge, active/inactive nodes, complete
component partition and deterministic source-witness spanning forest. Every forest
edge must be an actual retained pair. Counts are descriptive; no pvalue or threshold.
No favorable reader, rare-edge omission or approximate equality.

Primary joins1233to915, traverses consecutive retained indices and uses union-find.
Independent verifier traverses complete915source-line windows, reconstructs all
pairs and uses BFS closure, checks the forest, every witness and all counts.
Source-free fixtures include a real two-state toy hand channel (entry mark, payload
bit, exit mark), an added seam merging its two states, and separate I_g/O_gfor one
symbol. Spec/code/inputs locked before native edge enumeration.

Predecessors inspected:883explicitly prohibits cross-group adjacency and constrains
fixed overlapping blocks WITHINwords;928joins letter entries within words and resets
toLOWperword.1287requires common wordSTART/naturalENDand reversible unit actions;
state continuation across spaces is outside it.318is probabilistic wrapper prediction,
not exact endpoint equality. This is a distinct boundary-location/marker contract,
not a repaired883block cipher or an automatic1287state enlargement. Optional bench
fusion was not selected: old G2BH/HBalready cover that construction and its direct
context route. No old lexical guesses, blanket ambiguity audit or new decoder.
