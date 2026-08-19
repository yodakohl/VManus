# GDT372 external pre-specification capacity

Status: **FROZEN BEFORE SIMULATION**.

GDT370–371 showed that a medium stable visual↔formal relation is impractical to
confirm when 81 candidate comparisons are searched. GDT372 changes only that
search freedom. It asks how much capacity is recovered when an external source
or independently normalized referent freezes 1, 3, 9, 27, or 81 eligible
formal comparisons before target exposure.

The generator, medium coefficient `.9`, nuisance heterogeneity, Jeffreys
estimation, held scoring, and stable/reversing definitions are inherited. The
selector cost is exactly `log2(library_size)`.

Frozen grid:

- candidate family: 1, 3, 9, 27, 81;
- discovery folios: 4, 8, 12;
- untouched held folios: 2, 4, 8;
- arrays per folio: 1 or 2;
- cells per array: 6 or 12;
- scenarios: null, medium stable, medium reversing;
- 256 trials; seed `37220260819`.

A trial passes with positive selector-paid aggregate held gain and positive raw
gain on at least `ceil(.75 * held_folios)`, never fewer than two. A design is
adequate at stable detection >=.80, null any-pass <=.05, and reversing any-pass
<=.10. Choose the smallest adequate panel separately for every library size.

This is synthetic planning only. It does not open or score Voynich evidence,
and it cannot establish any association, object, role, word, language,
plaintext, meaning, or translation. f84 is forbidden.
