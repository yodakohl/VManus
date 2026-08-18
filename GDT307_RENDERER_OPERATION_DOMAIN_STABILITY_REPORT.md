# GDT307 — selected renderer-operation domain stability

Status: **SELECTED_OPERATIONS_DOMAIN_MIXED**.

> The operation family was selected on the complete GDT303 corpus. This is frozen post-selection domain stability, not independent discovery.

| operation | section dot/accuracy/max-p | hand dot/accuracy/max-p | register dot | Currier dot | class |
|---|---:|---:|---:|---:|---|
| `wrapper:ch>s` | +0.4694/0.846/0.007933601855 | +0.4656/0.867/0.002685219089 | +0.4339 | +0.3678 | DOMAIN_STABLE |
| `wrapper:d>s` | +0.1089/0.789/0.128768460881 | +0.1318/0.947/0.003051385329 | +0.1554 | +0.0882 | DOMAIN_STABLE |
| `wrapper:NONE>q` | +0.0093/0.421/0.948492615648 | +0.0026/0.375/0.998901501282 | +0.0126 | +0.0337 | DOMAIN_MIXED_OR_UNSTABLE |

## Interpretation

The selected exact operations are evaluated only where the same exact forms occur inside and outside a held domain. `ch->s` is strongly direction-stable in all four domain views. `d->s` is also direction-stable by the frozen rule, with its strongest corrected evidence in held hand/register and a weaker held-section correction. In contrast, `NONE->q` has small positive mean dots but fails section and hand direction accuracy. Thus `s` substitution is the more domain-stable physical-position operation, while q remains better characterized by its known post-DY host/register ecology. This cannot rescue the failed global wrapper model because the effect is confined to selected, exact compatible pairs.

## Claim ceiling

Selected formal renderer-operation domain stability only; no grammar semantics sound language plaintext meaning or translation. No f84 row was opened, parsed, retained, joined, or scored.
