# GDT1180 — small contextual source alphabets

Fixed exploratory comparison after1179. All source books and inherited target summaries are exposed. The failed GDT001 preceding-source inverse key (484914 bits behind anonymous baseline, unstable) and GDT605/606 inverse failures remain unchanged. This is a forward construction test, not native key inference.

Source: unchanged1054 complete recipe projections in1177 SOURCE_TEXTS.json, original order and all normalized characters/word boundaries. b4/w1 alone train tables. bs1/gr1 are exposed transfer controls, not independent confirmation. No source omission, added filler or whole-word meaning dictionary.

Unit inventory: lowercase a–z followed by IDEA935's56 fixed rare characters in their declared order, followed by sch ch ck ei ie au eu en er em es ung lich heit keit. Greedy longest literal shortcut within each word; ties lexical. All remaining characters must belong to the fixed alphabet. Unknown words are supported; unknown characters outside it are explicitly rejected. No shortcut crosses a source space.

Six models: V2-flat,V3-flat,V4-flat,V2-edge,V3-edge,V4-edge. V2 is vowel(aeiouyäöü) versus other; V3 vowel versus sonorant(lmnr) versus other; V4 is the V/C pattern of the previous two decoded characters. At recipe start history is two spaces (nonvowels). History persists across word spaces, which do not update it. After each unit, update using every character in its full expansion. These are invented operational alphabets, not Voynich sound values.

For flat models one table per state. Edge models use a table for initial, medial or final unit; single-unit words count as final. Position is knowable from written word boundaries and prefix-code width before interpreting the unit. Train unit counts per state/position on b4/w1, rank descending count then Unicode unit order across the full fixed inventory; even zero-count entries follow that order. Top21 units each get a single sign from the fixed glyph order for that phase. All remaining units get q plus exactly two base22 digits of the unit's zero-based global inventory index. A q-prefixed code is always three glyphs. No naked q. All other signs are single-unit codes. Unused escape indices and noncanonical escaped common units are rejected. Alphabet rows are learned once; no adaptation on transfer books.

Base22 digit order: a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh.
Flat and medial sign order: e o a y i n d ch r l s k t sh p f m ckh cth cph cfh.
Initial: o ch d y a s k t p f sh e i n r l m ckh cth cph cfh.
Final: y n r l o e a i d s m k t p f ch sh ckh cth cph cfh.
These fixed role orders are informed construction using already known broad shape, not hidden training or evidence for their native values.

Physical lines wrap at48 glyphs without splitting a word; recipe boundaries remain paragraphs. All1054 recipes must decode exactly and reencode from recovered words. Count actual common and escape entries, paid glyphs and full source lengths. An encoder, its complete public table and visible paragraphs/spaces must suffice without access to the original source or unprinted labels.

All ten1174 metrics, tolerances and first8000-word samples remain unchanged. Full basic pass requires all ten for all three readers in all four books, complete reversal, and alphabet compliance. Partial scores are never success. Passing only permits comparison with stronger structural knowledge; it is not a translation or established medieval practice. No post-result row, state, shortcut, corpus, threshold or exception changes. Before first measurement, lock preregistration, method, source, tables code and metric/target dependencies. Budget: remaining declared block through05:58UTC including closure; reassess there rather than automatically expand.
