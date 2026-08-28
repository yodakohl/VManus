# GDT602 — the unknown Naibbe key is recoverable after correct segmentation

Status: **NAIBBE_KEY_RECOVERED_CONDITIONAL_ON_ORACLE_SEGMENTATION**.

## Result

The capacity-constrained solver recovers 52,626/52,641 plaintext characters
(99.9715%) and 391/396 observed state-specific code types (98.7374%). Seeds 1,
2, and 3 reach the same score and accuracy. Their exact rare-error assignments
are not byte-identical, so only score and recovery are stable.

| candidate | char accuracy | type accuracy | char-4 bits/event |
|---|---:|---:|---:|
| unconstrained maximum likelihood | 19.0631% | 9.3434% | -3.58310 |
| true key, score only | 100% | 100% | -3.69938 |
| six-table capacity model | **99.9715%** | **98.7374%** | -3.69510 |

The unconstrained score is deceptively better than the true key because it
collapses into repetitive pseudo-Latin. The independent Markov-typicality
scores reject that collapse and put the capacity solution within 0.006 bits per
event of the true key at orders 2–4.

Only five rare code types in the emitted seed-1 key are wrong, covering fifteen
characters. The complete recovered table is in
`artifacts/gdt602_recovered_key.tsv`.

## Consequence

The language-model search itself is no longer the bottleneck. The decisive
remaining problem is discovering U/P/S unit boundaries and states without the
published table or aligned plaintext. Until that succeeds on the control, the
capacity solver cannot be transferred honestly to Voynich.

No Voynich target row and no f84/f84r material was accessed. No plaintext or
meaning is claimed for the manuscript.
