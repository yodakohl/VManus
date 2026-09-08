# LJ submitted-scope retrieval

Unknown resolved by bounded audit: all79 authored proposals were submitted semantic, but effective review scope hides36 method-reviewed proposals and one workflow duplicate from a semantic filter. Existing unrestricted retrieval preserves them; there is no authored-topic filter.

Add opt-in submitted_scope metadata/filter derived only in the disposable index from NEW_PROPOSAL base scope. Preserve effective scope, canonical records, review/fingerprint semantics and original FTS content. Success lets the user retrieve originally semantic proposals together with their unchanged method failures; failure leaves current retrieval unchanged and stops this patch.

Smallest adequate change: existing facet mechanism, compact card field, intersecting SQL filter before pagination, focused temporary-database lifecycle tests. Total budget20minutes including implementation, validation and root publication. This is engineering navigation, not a manuscript finding or new scientific gate.
