# GDT001 sparse-payload follow-up

Status: exploratory; not a confirmed translation.

The test reused the null winner's exact lattice paths and charged one common
structural scaffold. Five mechanically defined core/payload subsets were each
compared with an identically split source n-gram null. Three GPU mapping
restarts were CPU-rescored per subset.

Every language channel lost. The closest was `CHE_PREFIX`: 3.194015 versus
3.058726 bits/source-symbol for its matched null, a deficit of 26,290 bits.
The other deficits ranged from 134,289 to 255,620 bits. Every selector produced
three different mapping hashes.

Decision: `STOP_NO_SPARSE_LANGUAGE_GAIN_KEYS_UNSTABLE`. This rules out only
these explicit Middle High German sparse-payload mappings; it does not prove
that the manuscript is nonsemantic or lacks language.
