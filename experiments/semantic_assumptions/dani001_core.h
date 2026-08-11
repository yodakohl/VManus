#ifndef VMANUS_DANI001_CORE_H
#define VMANUS_DANI001_CORE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Stable, string-free C ABI.  All output vectors are vector-major raw <u4. */
enum dani001_status {
    DANI001_OK = 0,
    DANI001_INVALID_ARGUMENT = 1,
    DANI001_INVALID_CORE_SIZE = 2,
    DANI001_INVALID_RANK_RANGE = 3,
    DANI001_INVALID_CONSTRAINT = 4,
    DANI001_WEIGHT_OVERFLOW = 5,
    DANI001_INVALID_ENCODING = 6,
    DANI001_OVERLENGTH_PREIMAGE = 7,
    DANI001_BUFFER_TOO_SMALL = 8,
    DANI001_OPENMP_UNAVAILABLE = 9,
    DANI001_UNSUPPORTED_SCALAR_SIZE = 10
};

enum dani001_match_mode {
    DANI001_DIRECT = 0,
    DANI001_DEPOSITED_AFFIX = 1
};

enum dani001_match_label {
    DANI001_UNMATCHED = 0,
    DANI001_MATCH_DIRECT = 1,
    DANI001_MATCH_GALLOWS = 2,
    DANI001_MATCH_GALLOWS_STANDARD = 3,
    DANI001_MATCH_STANDARD = 4,
    DANI001_MATCH_SUFFIX_YN = 5
};

uint32_t dani001_abi_version(void);
uint32_t dani001_has_openmp(void);
uint64_t dani001_factorial(uint32_t n_core);

/*
 * Process-local audit for the optimized constraint traversal.  Callers must
 * serialize reset/get with enumeration calls.  A lower-bounded traversal
 * prunes disjoint Lehmer-rank subtrees before constructing a completed
 * assignment; completed_rank_zero must therefore remain zero for [1,N).
 * These diagnostics extend ABI version 1 without changing any existing
 * function signature.
 */
void dani001_reset_traversal_audit(void);
int dani001_get_traversal_audit(
    uint64_t *optimized_calls,
    uint64_t *constraint_traversals,
    uint64_t *branches_considered,
    uint64_t *branches_pruned,
    uint64_t *completed_assignments,
    uint64_t *completed_rank_zero
);

/* Lexicographic permutation rank is the ordinary Lehmer rank. */
int dani001_rank_lex(
    uint32_t n_core,
    const uint8_t *permutation,
    uint32_t *rank_out
);
int dani001_unrank_lex(
    uint32_t n_core,
    uint32_t rank,
    uint8_t *permutation_out
);

/*
 * Each constraint is one compatible partial bijection.  input_masks[c] marks
 * assigned input positions; required_outputs[c*n_core+i] is the required
 * output index or 0xff for an unassigned input.  Distinct alternatives for a
 * weighted item must already be deduplicated; exact-token alternatives are
 * disjoint because they assign the same observed core-input set.
 *
 * weights is constraint-major [constraint][vector].  All weights are
 * nonnegative.  output is vector-major [vector][rank-rank_begin].  The
 * half-open rank mask means a call with rank_begin=1 never stores rank zero.
 */
int dani001_enumerate_constraints(
    uint32_t n_core,
    uint32_t n_constraints,
    const uint16_t *input_masks,
    const uint8_t *required_outputs,
    uint32_t n_vectors,
    const uint32_t *weights,
    uint32_t rank_begin,
    uint32_t rank_end,
    uint32_t threads,
    uint32_t *output
);

/* Independent scalar reference, deliberately limited to n_core <= 6. */
int dani001_enumerate_constraints_scalar(
    uint32_t n_core,
    uint32_t n_constraints,
    const uint16_t *input_masks,
    const uint8_t *required_outputs,
    uint32_t n_vectors,
    const uint32_t *weights,
    uint32_t rank_begin,
    uint32_t rank_end,
    uint32_t *output
);

/* Frozen nibble encoding primitives. */
int dani001_encode_codes(
    const uint8_t *codes,
    uint32_t length,
    uint64_t *encoded_out
);
int dani001_decode_codes(
    uint64_t encoded,
    uint8_t *codes_out,
    uint32_t *length_out
);

/* Deposited decision-order matcher over reachable encoded keys. */
int dani001_direct_match(
    uint64_t skeleton,
    const uint64_t *keys,
    uint32_t n_keys,
    uint32_t mode,
    uint32_t *match_label_out
);

/*
 * Exact accepted-preimage union.  Call first with output=NULL/capacity=0 to
 * obtain output_count, then again with sufficient capacity.  Output is sorted
 * and deduplicated.  Any accepted preimage longer than ten hard-stops.
 */
int dani001_build_preimages(
    const uint64_t *keys,
    uint32_t n_keys,
    uint32_t mode,
    uint64_t *output,
    uint32_t capacity,
    uint32_t *output_count
);

int dani001_preimage_match(
    uint64_t skeleton,
    const uint64_t *accepted_preimages,
    uint32_t n_preimages,
    uint32_t *matched_out
);

int dani001_check_preimage_equivalence(
    const uint64_t *skeletons,
    uint32_t n_skeletons,
    const uint64_t *keys,
    uint32_t n_keys,
    const uint64_t *accepted_preimages,
    uint32_t n_preimages,
    uint32_t mode,
    uint32_t *mismatch_count_out
);

#ifdef __cplusplus
}
#endif

#endif
