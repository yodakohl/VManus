# GDT1062 method

The [preregistration](PREREGISTRATION.md) fixed the 23 admissible rows of the
public [plant-name table](https://github.com/scott-schechter/voynich-decoded/blob/71f2f3c91e9113d285ab21e024f1dd70c1f43c44/publication/04-plant-identifications.md)
before querying manuscript text. The table has 26 rows; f1v, f54r and f57r
were removed solely by the existing GDT631 text allowlist. Source commit and
SHA-256 are pinned in the preregistration and validator.

`src/run.py` uses selector-first guarded queries on the 23 explicitly allowed
pages, with explicit output columns. The cross-reader source supplies ZL3b,
IT2a and RF1b clean transcriptions; the ZL3b metadata source marks P/L kinds.
The script sorts loci numerically, chooses the first P locus and compares its
first exact group with each fixed EVA label. It also records all exact
same-page occurrences by P/L kind. No raw separator/letter is changed by this
test, and the three readings are alternate views of one manuscript. The
guarded command rejects f84* before materializing row content.

`src/validate.py` refetches and hashes the pinned public source, checks that
all 23 local claims are exactly the admitted subset of its 26 rows, and checks
every one of the 69 reader results against summary counts. Reproduce with the
commands in `experiment.json`. No image or new page was opened. This tests
source-position accuracy only; the asserted plant meanings require separate
independent evidence.
