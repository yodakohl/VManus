# GDT277 — calibration of the frozen GDT276 MDL signature

Status: **GDT276_SIGNATURE_NOT_ARCHITECTURE_SPECIFIC**.

GDT276 remained byte-identical. Five known control architectures were passed through the frozen five-world scorer on one exact 4,476-event length/structure/alphabet-capacity view.

| architecture | leading world | abbreviation − compressed bits | matched saving | signature | LOFO-safe rank+direction |
|---|---|---:|---:|---|---|
| ORDINARY_NATURAL_LANGUAGE | LOCAL_CODEBOOK | -864.7 | +474.5 | NO | NO |
| ABBREVIATION_HEAVY_MEDIEVAL | LOCAL_CODEBOOK | -1059.1 | +903.5 | NO | NO |
| ARBITRARY_LOCAL_CODEBOOK | ABBREVIATION_HEAVY_LANGUAGE | -287.6 | +126.5 | YES | YES |
| COMPOSITIONAL_TECHNICAL_NOTATION | ABBREVIATION_HEAVY_LANGUAGE | -708.3 | +154.1 | YES | YES |
| HYBRID_SHORTHAND | ABBREVIATION_HEAVY_LANGUAGE | -810.2 | +85.3 | YES | YES |
| VOYNICH_MATCHED_REFERENCE | ABBREVIATION_HEAVY_LANGUAGE | -1337.2 | +1607.8 | YES | YES |

The fixed signature requires the abbreviation-heavy character world to rank first, beat the compressed character world, and save bits against its matched context permutation. The table is a diagnostic calibration, not a model posterior.

Known non-language code/notation systems with the full fixed signature: **3** (ARBITRARY_LOCAL_CODEBOOK, COMPOSITIONAL_TECHNICAL_NOTATION, HYBRID_SHORTHAND). Known language/abbreviation controls with it: **0** (none). Under the strict fold-local representation, non-language systems retaining rank+direction: **3** (ARBITRARY_LOCAL_CODEBOOK, COMPOSITIONAL_TECHNICAL_NOTATION, HYBRID_SHORTHAND).

## Limits

The capacity overlay exactly matches host length at each retained Voynich structural opportunity, but necessarily breaks native adjacency across length queues. Alphabet normalization is lossy and reported. Expanded and diplomatic Nuremberg are paired views, while A/B/B2 are constructed controls. These facts prevent a cultural or linguistic inference even if the signature is selective.

No PAGE_HOST substring was mined. No meaning, language, notation identity, plaintext, or translation is assigned. The only Voynich input was the published f84-free GDT276 event inventory; no f84 row or source was opened, parsed, retained, joined, or scored.
