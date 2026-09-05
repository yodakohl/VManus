# GDT814 source-paragraph correction during the exploratory pass

The initial extraction closed P blocks at every non-P record. It therefore
reported29 blocks/146 loci and marked two f76r fragments (.11–13 and .32–36)
as boundary-incomplete. No complete-paragraph success was claimed for them.

Inspection of all56 guarded f76r source records shows the actual metadata:
P start at .1 and P end at .38, with nine separate L records interleaved in
the table. Those L records are .4,.7,.10,.14,.18,.22,.27,.31,.37. They do not
carry P-end/start flags. Cutting there loses the source's declared prose span.

The final extraction therefore treats P and interleaved L as separate streams:
within a selector, L records do not close the P stream. Source P start/end
flags, a selector transition or a different non-P/non-L record still delimit
it. Retain every L record inside a selected P span as a separate context record,
not as a prose token or a decoded connective. The reader prints their locus
and parent span explicitly. This is a metadata reconstruction, not an inferred
authorial sentence or image-to-text ownership relation.

The design is amended openly after source inspection. Exact target selection,
39-selector scope, word hypotheses and the absence of semantic scoring stay
unchanged. GDT813 selected complete loci, not these external paragraphs, and
its published files are untouched. Do not export this correction as a new
language rule or a solved Voynich paragraph structure.
