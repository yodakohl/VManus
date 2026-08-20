# GDT387 source audit

PCEEC2 is the independently parsed corpus already frozen in GDT378/GDT384.
The exact public source is <https://github.com/beatrice57/pceec2>, commit
`bf79d1c46e8ef983a7347b0664d0d80243f32831`. The 84 parsed files reproduce the
published bundle SHA-256
`c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714`.

The role vocabulary and head rules are frozen in `METHOD.md` before scoring.
Words, POS and parse nodes are used only to construct the hidden comparator
oracle. The retained oracle exports opaque element keys, a binary anonymous
role indicator, an exact opaque governor key, signed distance and distance
class; it exports no word, POS, constituent, translation or semantic label.

GDT382's observation layer was constructed before this experiment and exposes
only composite/opaque structural fields. Its PCEEC2 subset contains 27,518
visible elements across 84 source files. Two extra parser terminals outside
that frozen observation key set are ignored.

This experiment has no Voynich input. f84 is therefore absent by construction,
not merely filtered after loading.
