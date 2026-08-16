# GDT175 — recurrence with next-partner instability

Status: **MIXED_OR_UNRESOLVED**.

The publicly frozen GDT175 diagnostic was applied unchanged to 8448 PAGE_HOST groups on 1143 complete physical lines and 91 folios. It yields 7305 within-line next events. Every f84* source row was rejected before retention; no f84r row was retained, joined, or scored.

## Global result by frozen occurrence bin

| bin | hosts | covered events | held bits/event | overlap excess | JSD excess | control placement (held / overlap / JSD) |
|---|---:|---:|---:|---:|---:|---|
| N2_4 | 207 | 557 | -0.201530 | -0.002390 | 0.000994 | BELOW_CONTROL_RANGE / BELOW_CONTROL_RANGE / ABOVE_CONTROL_RANGE |
| N5_15 | 117 | 950 | -0.497886 | -0.000920 | -0.000011 | BELOW_CONTROL_RANGE / BELOW_CONTROL_RANGE / ABOVE_CONTROL_RANGE |
| N16_63 | 42 | 1222 | -0.746119 | -0.001247 | 0.000135 | BELOW_CONTROL_RANGE / INSIDE_CONTROL_RANGE / BELOW_CONTROL_RANGE |
| N64_PLUS | 22 | 3923 | -0.876495 | -0.005344 | 0.000787 | INSIDE_CONTROL_RANGE / BELOW_CONTROL_RANGE / ABOVE_CONTROL_RANGE |

Overall eligible-event coverage is 0.910609. The global held gain is -4935.492145 bits (-0.741956 bits/event). Coverage is reported independently of GDT174's ~91% recurrent-group mass.

## Register and section diagnosis

| register | folios | hosts | events | held bits/event | powered |
|---|---:|---:|---:|---:|---:|
| HERBAL_A | 46 | 161 | 1774 | -0.767920 | 1 |
| HERBAL_B | 15 | 63 | 499 | -0.749689 | 1 |
| OTHER_A | 7 | 36 | 256 | -0.683814 | 1 |
| OTHER_B | 12 | 134 | 1813 | -0.686403 | 1 |
| STARS_RECIPE_B | 12 | 154 | 1830 | -0.682437 | 1 |

Powered registers: 5; positive: 0; negative: 5. Powered section sensitivities: 5. The frozen decision is therefore **MIXED_OR_UNRESOLVED**.

## What explains the GDT174 negative NEXT_HOST result?

Register mixture is not the dominant explanation: every one of the five powered register-specific gains remains negative. Count/frequency alone is also not sufficient across the panel: the N2_4 and N5_15 bins are below the held-gain and overlap control envelopes and above the JSD envelope. But the preregistered folio-instability diagnosis requires at least three of four bins, and only those two qualify. N16_63 has negative held gain without the matched overlap/JSD signature, while N64_PLUS has held gain inside the synthetic envelope despite unusually low overlap and high divergence.

The useful conclusion is therefore heterogeneous partner instability: a folio-conditioned signal is concentrated in low-to-mid recurrence hosts, while the two high-count regimes do not form one coherent mechanism. This rejects a simple register-mixture story and a single pooled sampling story, but it does not justify inventing a new architecture or B3.

The exact per-host rows include partner-set overlap, Jeffreys-smoothed pairwise JSD, pooled and within-folio target entropy, and 256-world host-specific sampling nulls. `gdt175_side_by_side.tsv` retains the three unscaled control rows beside Voynich for every count bin.

## Claim ceiling

This diagnoses recurrence-with-partner-instability on the frozen panel. It creates no architecture, codebook, word, language, morphology, role, meaning, plaintext, or translation. B3 was not built.
