# Luna research pipeline

Authorized by the user on 2026-09-14. Routine research workers use
`gpt-5.6-luna` with `reasoning_effort="high"` and `fork_turns="none"`.
Root handles research choice, difficult interpretation, validation and publication.
This is a division of model work; extra CPU workers are not the primary speed lever.
No throughput or token-saving factor has yet been measured for meaningful research.

## One bounded packet, three roles

- Producer: source-grounded raw hypotheses with a close rival and distinguishing
  consequence. Add new ideas through the existing `vmanus-work ideas add` registry.
- Worker: execute a fixed task, reuse source readers and tests, write a compact result.
- Critic: inspect evidence and assumptions, preferably without the producer's
  conclusions during the initial review. This is not independent meaning confirmation.

At most three Luna workers alongside root in the current four-slot setup. Reuse
workers for a related bounded follow-up; restart with a small packet when context
would otherwise grow. Do not copy the entire conversation or the history registry.
A running worker may get a concise correction, not repeated whole-project context.
Tasks must be independent enough to make concurrent work useful. Scientific
blinding and separate output ownership take precedence over convenient parallelism.

A packet describes a bounded batch, not a second scientific claim registry or a
persistent queue. Each task has a question, assigned input paths, result path and
required result fields. Inputs are bound by SHA256. Allowed pages and prior exposure
are explicit. File references in a brief are not an instruction to dump every file.
Read only the relevant primary sections and exact source cases. Old word glosses
remain hypotheses; prior failures and reopening conditions remain in the registry.

## Small reusable automation

```
python3 tools/luna_batch.py validate PACKET.json
python3 tools/luna_batch.py brief PACKET.json TASK_ID
python3 tools/luna_batch.py collect PACKET.json
```

`validate` checks packet structure, repository-relative paths and bound input hashes.
`brief` emits only the selected task and its assigned input pointers.
`collect` reports pending, invalid and completed result files without promoting
any scientific conclusion. Result evidence paths must be declared inputs or inside
the batch output directory and name existing regular files. This checks the
top-level `evidence_paths` field, not arbitrary paths embedded in prose. A valid
JSON report is not proof of its observations. Input hashes do not certify page
admission: root must supply already vetted artifacts, never an unfiltered mixed
transcription. The helper is not a substitute for the guarded source reader.

The helper does not launch agents, execute candidate code, fetch data, publish,
contact anyone or run between turns. Root uses the actual collaboration tools for
model work and the existing exact staged-tree preflight for publication. There is
no API key, daemon, alternative decoder or new database to maintain.

Root decides when a concrete hypothesis merits a new registered experiment. New
experiments still use the existing generator/manifests and fixed sealed-data gates.
Within a registered series, hypotheses may be data variants of one question, not
independent discoveries merely because many variants exist. Preserve each verdict,
its evidence, assumption costs and untested cases. Unknown data must not conceal
known violated constraints. No statistical significance or meaning confirmation
follows from agreement among workers or candidate counts.

## Low-overhead operating cycle

1. Root chooses one question and the smallest useful source packet after bounded
   predecessor review; raw idea supply may continue independently.
2. Spawn Luna high workers with `fork_turns="none"`, the role and packet task ID.
3. Workers return compact JSON plus source pointers. Escalate unexpected evidence,
   ambiguous instructions or shared-file conflicts promptly; ordinary steps proceed.
4. Root collects the batch and spends attention on disagreements and concrete
   discriminators, not on re-reading every execution detail.
5. Record material outcomes in the existing registry/ledger and publish a bounded
   batch promptly, keeping full underlying results accessible. Do not generate
   a long polished report for every raw idea or postpone a finding indefinitely.

The first pilot is `research_registry/work_batches/luna_pilot_20260914/PACKET.json`.
It uses six already exposed paragraphs on three pages and matching RF variants.
The initial worker implements this helper while producer and critic inspect the
same bounded source scope in parallel. No reserved page or new image is admitted.
