# KB: source quotation integrity before mutation

Engineering decision, 2026-09-07 21:54 UTC. Budget: 15 minutes including implementation, tests, review and publication.

KA demonstrated eight newly asserted nonliteral source spans and two mistyped source hashes. Existing add/review commands accepted them. Historical fidelity validation is separate from semantic admissibility. The unknown is whether a small ingress check can reject these errors without making old records unreadable or preventing source-free raw hypotheses.

Smallest adequate change: validate only newly supplied design.source_evidence in add/review before append. Support the existing single Markdown evidence object, literal physical lines and exact SHA256; optional end must agree when supplied. Reject non-Markdown targets before content access. No retrospective rewriting or scientific gate. Synthetic lifecycle tests must establish unchanged storage on rejection, valid multiline acceptance, and correction of old bad records without inherited-source validation.

Pass permits continued registry intake with this guard; failure leaves intake under explicit manual source validation. Do not expand to a generic evidence framework. Manuscript findings: none.
