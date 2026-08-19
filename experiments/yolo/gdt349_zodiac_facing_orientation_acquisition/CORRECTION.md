# GDT349 pre-review freeze correction

The first freeze invocation stopped before writing any artifact because the
producer incorrectly expected the upstream strict cyclic panel to contain all
300 public zodiac records.  The published upstream artifact contains 235 rows:
21 complete strict rings after 65 incomplete, non-primary, or non-ring records
were excluded by its earlier text-blind capacity audit.

Before any new image was opened for GDT349, the method and code were corrected
to freeze all 235 upstream rows without further selection.  No orientation
call, Voynich formal value, or score was available during this correction.
