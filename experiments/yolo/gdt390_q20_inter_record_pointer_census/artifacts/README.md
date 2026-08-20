# GDT390 artifacts

- `gdt390_record_frame.tsv`: exact metadata-only 170-record census.
- `gdt390_pre_image_freeze.json`: page/record order, access rules, outcomes,
  eligibility, capacity, and claim ceiling frozen before image review.
- `gdt390_pre_image_freeze_validation.json`: independent freeze validation.
- `gdt390_image_manifest.tsv` / `gdt390_image_mapping.json`: allow-listed
  official-canvas mapping with the formal seal retained.
- `gdt390_review_image_hashes.tsv`: hashes and dimensions of the 13 directly
  reviewed images; image bytes and contact sheets remain outside Git.
- `gdt390_page_observations.tsv`: complete 13-page visual census.
- `gdt390_record_observations.tsv`: 170-row coverage accounting in the frozen
  record order.
- `gdt390_pointer_candidates.tsv` / `gdt390_eligible_edge_packet.tsv`: empty
  candidate and edge packets.
- `gdt390_capacity_gates.tsv`, `gdt390_access_log.json`, `gdt390_result.json`,
  and `gdt390_validation.json`: stop decision, access accounting, compact
  result, and independent artifact/accounting validation.

Commit compact, reproducible results here. Large exhaustive tables require an explicit retention justification.
