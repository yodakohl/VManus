# GDT343 source audit — global opaque identity capacity

GDT343 reuses the six public, hash-frozen CoReMA collections and the corrected
diplomatic-token handling from GDT342. No new external source is introduced.

The source layer contains 1,136 complete records and 13,612 non-title elements
with editor concept IDs. There are 1,134 records with at least one normalized
concept, 989 with a repeated concept, and 983 with a concept present in more
than one field. The held-parallel panel remains 688 wording-distinct records
and 657 cross-collection pairs under the unchanged title/concept/surface rule.

Unlike GDT342, a concept receives the same salted opaque identity in every
record and collection. This is the comparator ground-truth analogue of a
globally stable code identity. The exported artifacts do not reveal a Q ID,
concept name, English label, or source word. The salt is a fixed domain string,
not a secret key and not selected from retrieval outcomes.

The exact raw-word control hashes diplomatic source tokens only. It never uses
CoReMA's semantic `commodity` attribute. The validator reconstructs this
baseline and the global-concept baseline directly from source.

No Voynich target table, GDT327 row, illustration, or f84 artifact was opened
for this source audit or design.
