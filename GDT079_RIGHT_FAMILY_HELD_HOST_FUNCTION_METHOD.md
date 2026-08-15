# GDT079 — RIGHT_FAMILY held-host function transfer

Status: **YOLO low-capacity functional-profile test**

Restrict to the four frozen HPR4 hosts `d/ok/yk/yt` and their five explicit
RIGHT_FAMILY states.  Leave one complete PAGE_HOST out, train only on the other
three, and predict the held host's RIGHT_FAMILY.  The baseline is register-only
RIGHT_FAMILY prevalence.  Test five fixed source-native context families
(`POSITION`, `POSITION_ONLY`, `WRAPPER`, `LEFT`, `FULL`) with backoff
`{1,4,16,64,256}`.  Pay `log2(25)` for selecting among all context/backoff
configurations.  Export per-family placement summaries and all held-host
gains.  A small positive result supports a transferable record-position bias,
not a meaning or linguistic suffix.  f84r is excluded.
