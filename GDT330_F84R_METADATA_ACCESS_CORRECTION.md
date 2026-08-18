# GDT330 — f84r metadata access correction

On 2026-08-18, after GDT329 was published, a scratch page-context check used
`csv.DictReader` to iterate the complete existing human page-annotation and
page-role tables before applying an in-loop whitelist for f82r, f83r, and
f107v.  A dictionary for the f84r public catalogue-metadata row was therefore
transiently materialized by the subprocess.

No f84r row or value was printed in tool output, retained by the scratch
script, selected, joined to GDT327--329, scored, or written to a scientific
artifact.  No f84r transcription, source group, family, PAGE_HOST, grammar
projection, target token, or formal holdout result was opened.  The page
catalogue metadata class had already been publicly exposed and disclosed by
GDT225, but this was nevertheless a fresh violation of the continuing
instruction not to access f84r.

GDT328 and GDT329 remain f84-free: their actual scientific inputs contain
zero f84 rows and were completed and published before this scratch check.
Future page-table access must whitelist raw lines before CSV parsing; no
further f84r access is authorized without explicit user permission.
