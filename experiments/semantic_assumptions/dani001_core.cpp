#include "dani001_core.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <climits>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace {

constexpr std::array<uint32_t, 11> FACTORIAL = {
    1U, 1U, 2U, 6U, 24U, 120U, 720U, 5040U, 40320U, 362880U, 3628800U
};
constexpr uint8_t UNASSIGNED = 0xffU;
constexpr uint32_t MAX_CORE = 10U;
constexpr uint32_t MAX_CODE_LENGTH = 10U;
constexpr uint64_t LOW_NIBBLE_MASK = (uint64_t{1} << 40U) - 1U;

bool little_endian_host() {
    const uint32_t value = 1U;
    return *reinterpret_cast<const uint8_t *>(&value) == 1U;
}

bool valid_core_size(uint32_t n_core) {
    return n_core >= 1U && n_core <= MAX_CORE;
}

uint32_t rank_permutation(
    uint32_t n_core,
    const std::array<uint8_t, MAX_CORE> &permutation
) {
    uint32_t rank = 0U;
    for (uint32_t i = 0U; i < n_core; ++i) {
        uint32_t smaller = 0U;
        for (uint32_t j = i + 1U; j < n_core; ++j) {
            smaller += static_cast<uint32_t>(permutation[j] < permutation[i]);
        }
        rank += smaller * FACTORIAL[n_core - 1U - i];
    }
    return rank;
}

bool unrank_permutation(
    uint32_t n_core,
    uint32_t rank,
    std::array<uint8_t, MAX_CORE> &permutation
) {
    if (!valid_core_size(n_core) || rank >= FACTORIAL[n_core]) {
        return false;
    }
    std::array<uint8_t, MAX_CORE> available{};
    for (uint32_t i = 0U; i < n_core; ++i) {
        available[i] = static_cast<uint8_t>(i);
    }
    uint32_t remaining = n_core;
    for (uint32_t i = 0U; i < n_core; ++i) {
        const uint32_t block = FACTORIAL[n_core - 1U - i];
        const uint32_t index = rank / block;
        rank %= block;
        if (index >= remaining) {
            return false;
        }
        permutation[i] = available[index];
        for (uint32_t j = index + 1U; j < remaining; ++j) {
            available[j - 1U] = available[j];
        }
        --remaining;
    }
    return true;
}

struct ConstraintView {
    uint16_t input_mask = 0U;
    std::array<uint8_t, MAX_CORE> required{};
};

struct TraversalAudit {
    uint64_t branches_considered = 0U;
    uint64_t branches_pruned = 0U;
    uint64_t completed_assignments = 0U;
    uint64_t completed_rank_zero = 0U;
};

struct GlobalTraversalAudit {
    std::atomic<uint64_t> optimized_calls{0U};
    std::atomic<uint64_t> constraint_traversals{0U};
    std::atomic<uint64_t> branches_considered{0U};
    std::atomic<uint64_t> branches_pruned{0U};
    std::atomic<uint64_t> completed_assignments{0U};
    std::atomic<uint64_t> completed_rank_zero{0U};
};

GlobalTraversalAudit TRAVERSAL_AUDIT;

int validate_enumeration(
    uint32_t n_core,
    uint32_t n_constraints,
    const uint16_t *input_masks,
    const uint8_t *required_outputs,
    uint32_t n_vectors,
    const uint32_t *weights,
    uint32_t rank_begin,
    uint32_t rank_end,
    uint32_t *output
) {
    if (!little_endian_host()) {
        return DANI001_INVALID_ARGUMENT;
    }
    if (!valid_core_size(n_core)) {
        return DANI001_INVALID_CORE_SIZE;
    }
    if (rank_begin > rank_end || rank_end > FACTORIAL[n_core]) {
        return DANI001_INVALID_RANK_RANGE;
    }
    if (n_vectors == 0U || output == nullptr) {
        return DANI001_INVALID_ARGUMENT;
    }
    if (n_constraints > 0U &&
        (input_masks == nullptr || required_outputs == nullptr || weights == nullptr)) {
        return DANI001_INVALID_ARGUMENT;
    }
    const size_t rank_count = static_cast<size_t>(rank_end - rank_begin);
    if (rank_count > 0U &&
        static_cast<size_t>(n_vectors) > std::numeric_limits<size_t>::max() / rank_count) {
        return DANI001_INVALID_ARGUMENT;
    }

    const uint16_t valid_mask = static_cast<uint16_t>((uint32_t{1} << n_core) - 1U);
    std::vector<uint64_t> weight_upper_bound(n_vectors, 0U);
    for (uint32_t c = 0U; c < n_constraints; ++c) {
        const uint16_t mask = input_masks[c];
        if ((mask & static_cast<uint16_t>(~valid_mask)) != 0U) {
            return DANI001_INVALID_CONSTRAINT;
        }
        uint16_t seen_outputs = 0U;
        for (uint32_t i = 0U; i < n_core; ++i) {
            const uint8_t required = required_outputs[
                static_cast<size_t>(c) * n_core + i
            ];
            const bool assigned = (mask & static_cast<uint16_t>(1U << i)) != 0U;
            if (!assigned) {
                if (required != UNASSIGNED) {
                    return DANI001_INVALID_CONSTRAINT;
                }
                continue;
            }
            if (required >= n_core) {
                return DANI001_INVALID_CONSTRAINT;
            }
            const uint16_t output_bit = static_cast<uint16_t>(1U << required);
            if ((seen_outputs & output_bit) != 0U) {
                return DANI001_INVALID_CONSTRAINT;
            }
            seen_outputs |= output_bit;
        }
        for (uint32_t v = 0U; v < n_vectors; ++v) {
            weight_upper_bound[v] += weights[
                static_cast<size_t>(c) * n_vectors + v
            ];
            if (weight_upper_bound[v] > std::numeric_limits<uint32_t>::max()) {
                return DANI001_WEIGHT_OVERFLOW;
            }
        }
    }
    return DANI001_OK;
}

template <typename Leaf>
TraversalAudit enumerate_constraint_completions(
    uint32_t n_core,
    uint16_t input_mask,
    const uint8_t *required,
    uint32_t rank_begin,
    uint32_t rank_end,
    Leaf &&leaf
) {
    TraversalAudit audit{};

    /*
     * Traverse inputs in permutation order, not merely the free inputs.  At
     * depth d, every candidate output owns one exact lexicographic Lehmer
     * interval of size (n-d-1)!.  Disjoint intervals are rejected before the
     * output is assigned or a completed permutation exists.  In particular,
     * [1,n!) rejects the final identity-only [0,1) branch before its leaf.
     */
    auto recurse = [&] (
        auto &&self,
        uint32_t depth,
        uint16_t used,
        uint32_t prefix_rank
    ) -> void {
        if (depth == n_core) {
            ++audit.completed_assignments;
            audit.completed_rank_zero += static_cast<uint64_t>(prefix_rank == 0U);
            leaf(prefix_rank);
            return;
        }

        const bool fixed = (
            input_mask & static_cast<uint16_t>(1U << depth)
        ) != 0U;
        const uint32_t first_output = fixed ? required[depth] : 0U;
        const uint32_t output_stop = fixed ? first_output + 1U : n_core;
        const uint32_t block = FACTORIAL[n_core - 1U - depth];
        for (uint32_t output = first_output; output < output_stop; ++output) {
            const uint16_t bit = static_cast<uint16_t>(1U << output);
            if ((used & bit) != 0U) {
                continue;
            }
            uint32_t ordinal = 0U;
            for (uint32_t candidate = 0U; candidate < output; ++candidate) {
                ordinal += static_cast<uint32_t>(
                    (used & static_cast<uint16_t>(1U << candidate)) == 0U
                );
            }
            const uint32_t branch_begin = prefix_rank + ordinal * block;
            const uint32_t branch_end = branch_begin + block;
            ++audit.branches_considered;
            if (branch_end <= rank_begin || branch_begin >= rank_end) {
                ++audit.branches_pruned;
                continue;
            }
            self(
                self,
                depth + 1U,
                static_cast<uint16_t>(used | bit),
                branch_begin
            );
        }
    };
    recurse(recurse, 0U, 0U, 0U);
    return audit;
}

bool constraint_matches(
    uint32_t n_core,
    uint16_t input_mask,
    const uint8_t *required,
    const std::array<uint8_t, MAX_CORE> &permutation
) {
    for (uint32_t i = 0U; i < n_core; ++i) {
        if ((input_mask & static_cast<uint16_t>(1U << i)) != 0U &&
            permutation[i] != required[i]) {
            return false;
        }
    }
    return true;
}

bool decode_value(
    uint64_t encoded,
    std::array<uint8_t, MAX_CODE_LENGTH> &codes,
    uint32_t &length
) {
    if ((encoded >> 44U) != 0U) {
        return false;
    }
    length = static_cast<uint32_t>((encoded >> 40U) & 0x0fU);
    if (length > MAX_CODE_LENGTH) {
        return false;
    }
    const uint64_t payload = encoded & LOW_NIBBLE_MASK;
    for (uint32_t i = 0U; i < MAX_CODE_LENGTH; ++i) {
        const uint8_t code = static_cast<uint8_t>((payload >> (4U * i)) & 0x0fU);
        if (i < length) {
            if (code == 0U || code > 14U) {
                return false;
            }
            codes[i] = code;
        } else if (code != 0U) {
            return false;
        }
    }
    return true;
}

uint64_t encode_value(const uint8_t *codes, uint32_t length) {
    uint64_t encoded = static_cast<uint64_t>(length) << 40U;
    for (uint32_t i = 0U; i < length; ++i) {
        encoded |= static_cast<uint64_t>(codes[i]) << (4U * i);
    }
    return encoded;
}

bool contains_key(const uint64_t *keys, uint32_t n_keys, uint64_t value) {
    for (uint32_t i = 0U; i < n_keys; ++i) {
        if (keys[i] == value) {
            return true;
        }
    }
    return false;
}

int validate_encoded_values(const uint64_t *values, uint32_t count) {
    if (count > 0U && values == nullptr) {
        return DANI001_INVALID_ARGUMENT;
    }
    for (uint32_t i = 0U; i < count; ++i) {
        std::array<uint8_t, MAX_CODE_LENGTH> codes{};
        uint32_t length = 0U;
        if (!decode_value(values[i], codes, length)) {
            return DANI001_INVALID_ENCODING;
        }
    }
    return DANI001_OK;
}

uint32_t direct_match_unchecked(
    uint64_t skeleton,
    const uint64_t *keys,
    uint32_t n_keys,
    uint32_t mode
) {
    if (contains_key(keys, n_keys, skeleton)) {
        return DANI001_MATCH_DIRECT;
    }
    if (mode == DANI001_DIRECT) {
        return DANI001_UNMATCHED;
    }

    std::array<uint8_t, MAX_CODE_LENGTH> codes{};
    uint32_t length = 0U;
    (void)decode_value(skeleton, codes, length);
    constexpr std::array<uint8_t, 3> gallows = {12U, 13U, 14U};
    constexpr std::array<uint8_t, 3> standard = {2U, 5U, 7U};
    const auto in = [](uint8_t value, const std::array<uint8_t, 3> &set) {
        return std::find(set.begin(), set.end(), value) != set.end();
    };

    if (length > 1U && in(codes[0], gallows)) {
        const uint64_t stripped = encode_value(codes.data() + 1U, length - 1U);
        if (contains_key(keys, n_keys, stripped)) {
            return DANI001_MATCH_GALLOWS;
        }
        if (length > 2U && in(codes[1], standard)) {
            const uint64_t double_stripped = encode_value(codes.data() + 2U, length - 2U);
            if (contains_key(keys, n_keys, double_stripped)) {
                return DANI001_MATCH_GALLOWS_STANDARD;
            }
        }
    }
    if (length > 1U && in(codes[0], standard)) {
        const uint64_t stripped = encode_value(codes.data() + 1U, length - 1U);
        if (contains_key(keys, n_keys, stripped)) {
            return DANI001_MATCH_STANDARD;
        }
    }
    if (length > 2U && codes[length - 2U] == 8U && codes[length - 1U] == 6U) {
        const uint64_t stripped = encode_value(codes.data(), length - 2U);
        if (contains_key(keys, n_keys, stripped)) {
            return DANI001_MATCH_SUFFIX_YN;
        }
    }
    return DANI001_UNMATCHED;
}

int build_preimage_vector(
    const uint64_t *keys,
    uint32_t n_keys,
    uint32_t mode,
    std::vector<uint64_t> &accepted
) {
    if (mode != DANI001_DIRECT && mode != DANI001_DEPOSITED_AFFIX) {
        return DANI001_INVALID_ARGUMENT;
    }
    const int validation = validate_encoded_values(keys, n_keys);
    if (validation != DANI001_OK) {
        return validation;
    }
    constexpr std::array<uint8_t, 3> gallows = {12U, 13U, 14U};
    constexpr std::array<uint8_t, 3> standard = {2U, 5U, 7U};
    accepted.clear();
    accepted.reserve(static_cast<size_t>(n_keys) * (mode == DANI001_DIRECT ? 1U : 17U));

    for (uint32_t index = 0U; index < n_keys; ++index) {
        std::array<uint8_t, MAX_CODE_LENGTH> key_codes{};
        uint32_t key_length = 0U;
        (void)decode_value(keys[index], key_codes, key_length);
        accepted.push_back(keys[index]);
        if (mode == DANI001_DIRECT || key_length == 0U) {
            continue;
        }

        auto add = [&](const std::vector<uint8_t> &prefix,
                       const std::vector<uint8_t> &suffix) -> int {
            const size_t length = prefix.size() + key_length + suffix.size();
            if (length > MAX_CODE_LENGTH) {
                return DANI001_OVERLENGTH_PREIMAGE;
            }
            std::array<uint8_t, MAX_CODE_LENGTH> combined{};
            size_t at = 0U;
            for (const uint8_t code : prefix) {
                combined[at++] = code;
            }
            for (uint32_t i = 0U; i < key_length; ++i) {
                combined[at++] = key_codes[i];
            }
            for (const uint8_t code : suffix) {
                combined[at++] = code;
            }
            accepted.push_back(encode_value(combined.data(), static_cast<uint32_t>(length)));
            return DANI001_OK;
        };

        for (const uint8_t gp : gallows) {
            int status = add({gp}, {});
            if (status != DANI001_OK) {
                return status;
            }
            for (const uint8_t sp : standard) {
                status = add({gp, sp}, {});
                if (status != DANI001_OK) {
                    return status;
                }
            }
        }
        for (const uint8_t sp : standard) {
            const int status = add({sp}, {});
            if (status != DANI001_OK) {
                return status;
            }
        }
        const int suffix_status = add({}, {8U, 6U});
        if (suffix_status != DANI001_OK) {
            return suffix_status;
        }
    }
    std::sort(accepted.begin(), accepted.end());
    accepted.erase(std::unique(accepted.begin(), accepted.end()), accepted.end());
    return DANI001_OK;
}

}  // namespace

extern "C" {

uint32_t dani001_abi_version(void) {
    return 1U;
}

uint32_t dani001_has_openmp(void) {
#ifdef _OPENMP
    return 1U;
#else
    return 0U;
#endif
}

uint64_t dani001_factorial(uint32_t n_core) {
    return valid_core_size(n_core) ? FACTORIAL[n_core] : 0U;
}

void dani001_reset_traversal_audit(void) {
    TRAVERSAL_AUDIT.optimized_calls.store(0U, std::memory_order_relaxed);
    TRAVERSAL_AUDIT.constraint_traversals.store(0U, std::memory_order_relaxed);
    TRAVERSAL_AUDIT.branches_considered.store(0U, std::memory_order_relaxed);
    TRAVERSAL_AUDIT.branches_pruned.store(0U, std::memory_order_relaxed);
    TRAVERSAL_AUDIT.completed_assignments.store(0U, std::memory_order_relaxed);
    TRAVERSAL_AUDIT.completed_rank_zero.store(0U, std::memory_order_relaxed);
}

int dani001_get_traversal_audit(
    uint64_t *optimized_calls,
    uint64_t *constraint_traversals,
    uint64_t *branches_considered,
    uint64_t *branches_pruned,
    uint64_t *completed_assignments,
    uint64_t *completed_rank_zero
) {
    if (
        optimized_calls == nullptr || constraint_traversals == nullptr ||
        branches_considered == nullptr || branches_pruned == nullptr ||
        completed_assignments == nullptr || completed_rank_zero == nullptr
    ) {
        return DANI001_INVALID_ARGUMENT;
    }
    *optimized_calls = TRAVERSAL_AUDIT.optimized_calls.load(
        std::memory_order_relaxed
    );
    *constraint_traversals = TRAVERSAL_AUDIT.constraint_traversals.load(
        std::memory_order_relaxed
    );
    *branches_considered = TRAVERSAL_AUDIT.branches_considered.load(
        std::memory_order_relaxed
    );
    *branches_pruned = TRAVERSAL_AUDIT.branches_pruned.load(
        std::memory_order_relaxed
    );
    *completed_assignments = TRAVERSAL_AUDIT.completed_assignments.load(
        std::memory_order_relaxed
    );
    *completed_rank_zero = TRAVERSAL_AUDIT.completed_rank_zero.load(
        std::memory_order_relaxed
    );
    return DANI001_OK;
}

int dani001_rank_lex(
    uint32_t n_core,
    const uint8_t *permutation,
    uint32_t *rank_out
) {
    if (!valid_core_size(n_core)) {
        return DANI001_INVALID_CORE_SIZE;
    }
    if (permutation == nullptr || rank_out == nullptr) {
        return DANI001_INVALID_ARGUMENT;
    }
    std::array<uint8_t, MAX_CORE> copy{};
    uint16_t seen = 0U;
    for (uint32_t i = 0U; i < n_core; ++i) {
        if (permutation[i] >= n_core) {
            return DANI001_INVALID_ARGUMENT;
        }
        const uint16_t bit = static_cast<uint16_t>(1U << permutation[i]);
        if ((seen & bit) != 0U) {
            return DANI001_INVALID_ARGUMENT;
        }
        seen |= bit;
        copy[i] = permutation[i];
    }
    *rank_out = rank_permutation(n_core, copy);
    return DANI001_OK;
}

int dani001_unrank_lex(
    uint32_t n_core,
    uint32_t rank,
    uint8_t *permutation_out
) {
    if (!valid_core_size(n_core)) {
        return DANI001_INVALID_CORE_SIZE;
    }
    if (permutation_out == nullptr || rank >= FACTORIAL[n_core]) {
        return DANI001_INVALID_ARGUMENT;
    }
    std::array<uint8_t, MAX_CORE> permutation{};
    if (!unrank_permutation(n_core, rank, permutation)) {
        return DANI001_INVALID_ARGUMENT;
    }
    std::copy_n(permutation.begin(), n_core, permutation_out);
    return DANI001_OK;
}

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
) {
    const int validation = validate_enumeration(
        n_core, n_constraints, input_masks, required_outputs, n_vectors, weights,
        rank_begin, rank_end, output
    );
    if (validation != DANI001_OK) {
        return validation;
    }
    if (threads == 0U) {
        return DANI001_INVALID_ARGUMENT;
    }
#ifndef _OPENMP
    if (threads != 1U) {
        return DANI001_OPENMP_UNAVAILABLE;
    }
#endif

    const size_t rank_count = static_cast<size_t>(rank_end - rank_begin);
    std::fill_n(output, static_cast<size_t>(n_vectors) * rank_count, uint32_t{0});

    uint64_t total_branches_considered = 0U;
    uint64_t total_branches_pruned = 0U;
    uint64_t total_completed_assignments = 0U;
    uint64_t total_completed_rank_zero = 0U;

#ifdef _OPENMP
#pragma omp parallel for schedule(static) num_threads(threads) \
    reduction(+:total_branches_considered,total_branches_pruned,total_completed_assignments,total_completed_rank_zero)
#endif
    for (int64_t signed_constraint = 0;
         signed_constraint < static_cast<int64_t>(n_constraints);
         ++signed_constraint) {
        const uint32_t c = static_cast<uint32_t>(signed_constraint);
        const uint8_t *required = required_outputs + static_cast<size_t>(c) * n_core;
        const TraversalAudit audit = enumerate_constraint_completions(
            n_core,
            input_masks[c],
            required,
            rank_begin,
            rank_end,
            [&](uint32_t rank) {
                const size_t local_rank = static_cast<size_t>(rank - rank_begin);
                for (uint32_t v = 0U; v < n_vectors; ++v) {
                    const uint32_t weight = weights[
                        static_cast<size_t>(c) * n_vectors + v
                    ];
                    if (weight == 0U) {
                        continue;
                    }
                    uint32_t &cell = output[static_cast<size_t>(v) * rank_count + local_rank];
#ifdef _OPENMP
#pragma omp atomic update
#endif
                    cell += weight;
                }
            }
        );
        total_branches_considered += audit.branches_considered;
        total_branches_pruned += audit.branches_pruned;
        total_completed_assignments += audit.completed_assignments;
        total_completed_rank_zero += audit.completed_rank_zero;
    }
    TRAVERSAL_AUDIT.optimized_calls.fetch_add(1U, std::memory_order_relaxed);
    TRAVERSAL_AUDIT.constraint_traversals.fetch_add(
        n_constraints, std::memory_order_relaxed
    );
    TRAVERSAL_AUDIT.branches_considered.fetch_add(
        total_branches_considered, std::memory_order_relaxed
    );
    TRAVERSAL_AUDIT.branches_pruned.fetch_add(
        total_branches_pruned, std::memory_order_relaxed
    );
    TRAVERSAL_AUDIT.completed_assignments.fetch_add(
        total_completed_assignments, std::memory_order_relaxed
    );
    TRAVERSAL_AUDIT.completed_rank_zero.fetch_add(
        total_completed_rank_zero, std::memory_order_relaxed
    );
    return DANI001_OK;
}

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
) {
    if (n_core > 6U) {
        return DANI001_UNSUPPORTED_SCALAR_SIZE;
    }
    const int validation = validate_enumeration(
        n_core, n_constraints, input_masks, required_outputs, n_vectors, weights,
        rank_begin, rank_end, output
    );
    if (validation != DANI001_OK) {
        return validation;
    }
    const size_t rank_count = static_cast<size_t>(rank_end - rank_begin);
    std::fill_n(output, static_cast<size_t>(n_vectors) * rank_count, uint32_t{0});

    std::array<uint8_t, MAX_CORE> permutation{};
    for (uint32_t i = 0U; i < n_core; ++i) {
        permutation[i] = static_cast<uint8_t>(i);
    }
    uint32_t rank = 0U;
    do {
        if (rank >= rank_begin && rank < rank_end) {
            const size_t local_rank = static_cast<size_t>(rank - rank_begin);
            for (uint32_t c = 0U; c < n_constraints; ++c) {
                const uint8_t *required = required_outputs + static_cast<size_t>(c) * n_core;
                if (!constraint_matches(n_core, input_masks[c], required, permutation)) {
                    continue;
                }
                for (uint32_t v = 0U; v < n_vectors; ++v) {
                    output[static_cast<size_t>(v) * rank_count + local_rank] += weights[
                        static_cast<size_t>(c) * n_vectors + v
                    ];
                }
            }
        }
        ++rank;
    } while (std::next_permutation(
        permutation.begin(), permutation.begin() + static_cast<ptrdiff_t>(n_core)
    ));
    if (rank != FACTORIAL[n_core]) {
        return DANI001_INVALID_RANK_RANGE;
    }
    return DANI001_OK;
}

int dani001_encode_codes(
    const uint8_t *codes,
    uint32_t length,
    uint64_t *encoded_out
) {
    if (length > MAX_CODE_LENGTH || encoded_out == nullptr ||
        (length > 0U && codes == nullptr)) {
        return DANI001_INVALID_ARGUMENT;
    }
    for (uint32_t i = 0U; i < length; ++i) {
        if (codes[i] == 0U || codes[i] > 14U) {
            return DANI001_INVALID_ENCODING;
        }
    }
    *encoded_out = encode_value(codes, length);
    return DANI001_OK;
}

int dani001_decode_codes(
    uint64_t encoded,
    uint8_t *codes_out,
    uint32_t *length_out
) {
    if (codes_out == nullptr || length_out == nullptr) {
        return DANI001_INVALID_ARGUMENT;
    }
    std::array<uint8_t, MAX_CODE_LENGTH> codes{};
    uint32_t length = 0U;
    if (!decode_value(encoded, codes, length)) {
        return DANI001_INVALID_ENCODING;
    }
    std::copy_n(codes.begin(), length, codes_out);
    *length_out = length;
    return DANI001_OK;
}

int dani001_direct_match(
    uint64_t skeleton,
    const uint64_t *keys,
    uint32_t n_keys,
    uint32_t mode,
    uint32_t *match_label_out
) {
    if (match_label_out == nullptr ||
        (mode != DANI001_DIRECT && mode != DANI001_DEPOSITED_AFFIX)) {
        return DANI001_INVALID_ARGUMENT;
    }
    int status = validate_encoded_values(&skeleton, 1U);
    if (status != DANI001_OK) {
        return status;
    }
    status = validate_encoded_values(keys, n_keys);
    if (status != DANI001_OK) {
        return status;
    }
    *match_label_out = direct_match_unchecked(skeleton, keys, n_keys, mode);
    return DANI001_OK;
}

int dani001_build_preimages(
    const uint64_t *keys,
    uint32_t n_keys,
    uint32_t mode,
    uint64_t *output,
    uint32_t capacity,
    uint32_t *output_count
) {
    if (output_count == nullptr || (output == nullptr && capacity != 0U)) {
        return DANI001_INVALID_ARGUMENT;
    }
    std::vector<uint64_t> accepted;
    const int status = build_preimage_vector(keys, n_keys, mode, accepted);
    if (status != DANI001_OK) {
        return status;
    }
    if (accepted.size() > std::numeric_limits<uint32_t>::max()) {
        return DANI001_INVALID_ARGUMENT;
    }
    *output_count = static_cast<uint32_t>(accepted.size());
    if (output == nullptr) {
        return DANI001_OK;
    }
    if (capacity < accepted.size()) {
        return DANI001_BUFFER_TOO_SMALL;
    }
    std::copy(accepted.begin(), accepted.end(), output);
    return DANI001_OK;
}

int dani001_preimage_match(
    uint64_t skeleton,
    const uint64_t *accepted_preimages,
    uint32_t n_preimages,
    uint32_t *matched_out
) {
    if (matched_out == nullptr) {
        return DANI001_INVALID_ARGUMENT;
    }
    int status = validate_encoded_values(&skeleton, 1U);
    if (status != DANI001_OK) {
        return status;
    }
    status = validate_encoded_values(accepted_preimages, n_preimages);
    if (status != DANI001_OK) {
        return status;
    }
    if (n_preimages > 0U) {
        if (!std::is_sorted(accepted_preimages, accepted_preimages + n_preimages) ||
            std::adjacent_find(accepted_preimages, accepted_preimages + n_preimages) !=
                accepted_preimages + n_preimages) {
            return DANI001_INVALID_ARGUMENT;
        }
    }
    *matched_out = static_cast<uint32_t>(
        n_preimages > 0U && std::binary_search(
            accepted_preimages,
            accepted_preimages + n_preimages,
            skeleton
        )
    );
    return DANI001_OK;
}

int dani001_check_preimage_equivalence(
    const uint64_t *skeletons,
    uint32_t n_skeletons,
    const uint64_t *keys,
    uint32_t n_keys,
    const uint64_t *accepted_preimages,
    uint32_t n_preimages,
    uint32_t mode,
    uint32_t *mismatch_count_out
) {
    if (mismatch_count_out == nullptr ||
        (mode != DANI001_DIRECT && mode != DANI001_DEPOSITED_AFFIX)) {
        return DANI001_INVALID_ARGUMENT;
    }
    int status = validate_encoded_values(skeletons, n_skeletons);
    if (status != DANI001_OK) {
        return status;
    }
    status = validate_encoded_values(keys, n_keys);
    if (status != DANI001_OK) {
        return status;
    }
    status = validate_encoded_values(accepted_preimages, n_preimages);
    if (status != DANI001_OK) {
        return status;
    }
    if (n_preimages > 0U) {
        if (!std::is_sorted(accepted_preimages, accepted_preimages + n_preimages) ||
            std::adjacent_find(accepted_preimages, accepted_preimages + n_preimages) !=
                accepted_preimages + n_preimages) {
            return DANI001_INVALID_ARGUMENT;
        }
    }
    uint32_t mismatches = 0U;
    for (uint32_t i = 0U; i < n_skeletons; ++i) {
        const bool direct = direct_match_unchecked(skeletons[i], keys, n_keys, mode) !=
            DANI001_UNMATCHED;
        const bool preimage = n_preimages > 0U &&
            std::binary_search(
                accepted_preimages,
                accepted_preimages + n_preimages,
                skeletons[i]
            );
        mismatches += static_cast<uint32_t>(direct != preimage);
    }
    *mismatch_count_out = mismatches;
    return DANI001_OK;
}

}  // extern "C"
