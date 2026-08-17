# GDT241 — f82r HPR2 formal-field expansion

## Question

Can the frozen HPR2 group-state inventory expand f82r field segmentation beyond
the eight complete-line loci used by GDT229, without fabricating semantic roles
or record positions?

## Method

Stream-reject every f84 row from `gdt016_group_state_inventory.tsv`.  Build the
frozen GDT227 PAGE_HOST/compiler parse and split each available f82r physical
line at `dy_closure`, retaining a final open field at line end.  Validate the
eight overlapping loci byte-for-byte against the ordered GDT239 field dossier.

Newly covered lines receive only local line-field ordinals and formal compiler
cells.  They do not receive GDT229 position/length role labels because they are
absent from the complete-line frame that defined those record coordinates.
