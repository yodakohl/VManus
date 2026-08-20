# GDT396 claim-retention plan

Status: `FROZEN_BEFORE_QUALIFICATION`.

Every decoder must generate and validate every API-V2 endpoint in memory for
each representation it declares. To avoid hundreds of millions of redundant
serialized rows, the runner retains only the following scientifically distinct
representation/endpoint cells. Omitted cells are explicit `UNSUPPORTED` cells
in the aggregate matrix; they are not silent abstentions.

| representation | retained endpoint families |
|---|---|
| `FULL_GROUP` | lexical identity |
| `HOST_LIKE` | entity, historical-ancestry, current-shared-meaning, and register partitions |
| `COMPOSITE_STATE` | construction and before/after/transition state partitions; temporal binary |
| `INFERRED_COMPONENTS` | current-productive and fossil-component partitions; productive/fossil binaries; morphology spans |
| `CONSTRUCTION_SPAN` | scope intervals |
| `RECORD_TOPOLOGY` | entity-reuse binary; all ranked target relations; record schema |
| `MULTI_RESOLUTION` | function/operator and semantic-category partitions plus architecture variants |

Every endpoint is therefore retained at one fixed representation rather than
duplicated across all representations. The full endpoint shape, candidate
locality, rank, span, Boolean, and determinism checks occur before this
retention filter. No oracle result selects the plan. Architecture and event
function multi-constraint/scalar comparisons are retained only at
`MULTI_RESOLUTION`.
