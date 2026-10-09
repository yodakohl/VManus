# Fixed values and parity

For a block with source ordinary-letter count vector n, ALT changes the writer's
bit state by n modulo2, regardless of entry state. The written alias sequence
identifies every source letter without reference to entry state; entry state
only decides whether that sequence is canonical. Repeating exactly the same
written whole unit block is legal iff every ordinary count is even. Applying
the same source block twice restores state, so first and third encodings agree.
Auxiliary characters have fixed values and no tick; odd total length alone is
not a contradiction. Example aÄa has even ordinary parity despite length3.

Let C be one fixed non-erasing uniquely decodable code for those units. If X is
a whole coded group, X lies in C*. If XX is also a valid whole group, its unique
unit parse is parse(X)parse(X), even when C is not prefix-free. Hence canonical
ALT imposes even ordinary-letter counts on decode(X). No reset may occur
between the copies; ordinary word gaps do not reset this contract. XX is one
source word containing two equal character blocks, not necessarily two words. Existing ol and olol
therefore impose this condition UNDER the writer contract, without first fixing
o/l as atomic letter codes. There is no general constraint on an arbitrary
substring X that is not separately known to belong to C*. A valid prefix alone
does not establish the rest as a unit-aligned suffix for a merely UD carrier.

If both B and dy are complete code strings, B Bdy or BBdy additionally supply
the concatenated B/B/dy unit parse; this does not establish native morphemes or
word meanings. Transcription/spacing conditions and the common fixed-carrier
assumption must stay explicit. An even-parity decoded block is possible, so the
known doubled forms do not by themselves refute this model.

Fixed uniquely decodable rendering preserves whole-word equality. Therefore
all three numerical frequency conditions can be tested on unit sequences before
selecting any drawing. No conservation of glyph lengths, edit distance or
character entropy follows. This is1197's prior mathematical contract and not
an inference that EVA characters are plaintext letters.
