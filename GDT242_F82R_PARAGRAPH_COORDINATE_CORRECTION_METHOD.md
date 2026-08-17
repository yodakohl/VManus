# GDT242 — f82r paragraph-coordinate correction

## Question

Did the selected complete-line frame preserve the three paragraph boundaries
needed by the GDT229 record-relative role projection on f82r?

## Method

Use the human catalogue's frozen three-paragraph census and the source-native
line codes in the GDT002 projection.  Paragraph starts are the three physical
prose loci with start codes `@P0`, `@P0`, and `*P0`: f82r.1, f82r.11, and
f82r.20.  Assign all 32 prose loci by physical order, then join the GDT241 HPR2
coverage and the historical GDT239/GDT229 record key.

This is a coordinate-integrity audit.  It does not refit the external role
instrument or assign replacement roles.
