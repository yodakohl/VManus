# Method and claim ceiling

The writer uses list removal/insertion. The validator represents each lowercase
letter by its last-use timestamp, breaking never-seen ties by alphabet order.
Sorting most-recent first gives the same rank list without using the runner.
Inverse validation selects the letter at each supplied rank and updates timestamps
from that recovered letter alone; plaintext is used only for final comparison.

Whole-word equality is invariant under a fixed uniquely decodable carrier.
This permits necessary type/top10/exact-repeat tests without inventing native
glyph values. It does not permit native edit/length/entropy scoring on rank units.
Different rank words can encode the same plaintext word at different entry states;
identical rank words can encode different plaintext words. Neither direction is
assumed to preserve lexical identity in the manuscript.

After writing a word once, its used lowercase letters occupy the front in their
last-occurrence order. Repeating the same word leaves that complete list unchanged.
Thus the second and third encodings agree. Every valid rank stream is decodable:
this alone rejects no native stream without an independently bound carrier and
content restriction. Stable Voynich word parts remain obligations.

This is the unexecuted MTF source arm of GDT1197 under its same frequency limits,
not a reopening of the failed native inverse GDT001 experiment. Alternate readers
are one manuscript; sources are existing exposed edition projections.
