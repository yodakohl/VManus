# Erratum: audit row count

The frozen `TEN_HOUR_REPORT_AUDIT_B.md` says “ten completed rows” in its first
paragraph. It should say **nine completed rows**: 537, 558, 560, 550, 564, 565,
566, 569 and 572. The 568 row was pending at audit time and was not included
among the completed rows. The original audit remains unchanged; its SHA-256 is
`d8a157f81ec680cd0a77ab34044499fe6d6fbb22a4439014b7cbd3c3f6ec3849`.
