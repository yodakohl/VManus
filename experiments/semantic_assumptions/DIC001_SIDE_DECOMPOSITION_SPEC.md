# DIC001 side decomposition

Post-confirmation descriptive decomposition of the fixed DIC001 naive-Bayes
log-odds score into three additive blocks: left terminal (`L1`, `L2`), right
initial (`R1`, `R2`), and cross-boundary pair (`X`, `X22`).  For each held
folio, center each block on its training ordinary-space mean and divide all
three by the full score's training ordinary-space population SD.  Reconstruct
the original interleaved full score separately and require its frozen byte
digest exactly. Assign the machine-order remainder to the cross block so the
three blocks sum to that anchor; record the maximum correction and stop if it
exceeds `1e-12`.

Apply the frozen label-blind nuisance projection to all three columns and the
same page/folio summaries and 65,536 fixed-count assignments.  Report effects
and descriptive p-values without new confirmation gates.  This analysis may
localize the confirmed structural reset signature but cannot establish picture
ownership, words, POS, meaning, plaintext, or translation.
