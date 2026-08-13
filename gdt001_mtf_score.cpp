#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace {

constexpr int SOURCE_SIGNS = 25;
constexpr int TARGET_LETTERS = 26;
constexpr int TARGET_SYMBOLS = 27;
constexpr int SPACE = 25;
constexpr int TARGET_SPACE = 26;
constexpr int BOS = 27;
constexpr int ANON_SYMBOLS = 26;
constexpr int ANON_SPACE = 25;
constexpr int ANON_BOS = 26;

inline double lm_cost(const double* costs, int a, int b, int c) {
    return costs[(a * 28 + b) * TARGET_SYMBOLS + c];
}

double mtf_lm_impl(const int32_t* tokens, const int64_t* offsets, int64_t lines,
                   const int32_t* ranks, const int32_t* initial,
                   const double* costs) {
    double total = 0.0;
    for (int64_t line = 0; line < lines; ++line) {
        int32_t state[TARGET_LETTERS];
        std::copy(initial, initial + TARGET_LETTERS, state);
        int h0 = BOS, h1 = BOS;
        for (int64_t i = offsets[line]; i < offsets[line + 1]; ++i) {
            const int source = tokens[i];
            int target;
            if (source == SPACE) {
                target = TARGET_SPACE;
            } else {
                const int rank = ranks[source];
                target = state[rank];
                for (int j = rank; j > 0; --j) state[j] = state[j - 1];
                state[0] = target;
            }
            total += lm_cost(costs, h0, h1, target);
            h0 = h1; h1 = target;
        }
    }
    return total;
}

double static_lm_impl(const int32_t* tokens, const int64_t* offsets, int64_t lines,
                      const int32_t* mapping, const double* costs) {
    double total = 0.0;
    for (int64_t line = 0; line < lines; ++line) {
        int h0 = BOS, h1 = BOS;
        for (int64_t i = offsets[line]; i < offsets[line + 1]; ++i) {
            const int source = tokens[i];
            const int target = source == SPACE ? TARGET_SPACE : mapping[source];
            total += lm_cost(costs, h0, h1, target);
            h0 = h1; h1 = target;
        }
    }
    return total;
}

double categorical_bits(const int64_t* counts, int size) {
    int64_t total = 0;
    for (int i = 0; i < size; ++i) total += counts[i];
    if (!total) return 0.0;
    double logp = std::lgamma(0.5 * size) - std::lgamma(total + 0.5 * size);
    const double base = std::lgamma(0.5);
    for (int i = 0; i < size; ++i) logp += std::lgamma(counts[i] + 0.5) - base;
    return -logp / std::log(2.0);
}

double mtf_kt_impl(const int32_t* tokens, const int64_t* offsets, int64_t lines,
                   const int32_t* ranks) {
    std::vector<int64_t> counts(27 * 27 * ANON_SYMBOLS, 0);
    int32_t initial[TARGET_LETTERS];
    for (int i = 0; i < TARGET_LETTERS; ++i) initial[i] = i;
    for (int64_t line = 0; line < lines; ++line) {
        int32_t state[TARGET_LETTERS];
        std::copy(initial, initial + TARGET_LETTERS, state);
        int h0 = ANON_BOS, h1 = ANON_BOS;
        for (int64_t i = offsets[line]; i < offsets[line + 1]; ++i) {
            const int source = tokens[i];
            int target;
            if (source == SPACE) {
                target = ANON_SPACE;
            } else {
                const int rank = ranks[source];
                target = state[rank];
                for (int j = rank; j > 0; --j) state[j] = state[j - 1];
                state[0] = target;
            }
            ++counts[(h0 * 27 + h1) * ANON_SYMBOLS + target];
            h0 = h1; h1 = target;
        }
    }
    double total = 0.0;
    for (int context = 0; context < 27 * 27; ++context)
        total += categorical_bits(counts.data() + context * ANON_SYMBOLS, ANON_SYMBOLS);
    return total;
}

}  // namespace

extern "C" double gdt001_mtf_lm_score(
    const int32_t* tokens, const int64_t* offsets, int64_t lines,
    const int32_t* ranks, const int32_t* initial, const double* costs) {
    return mtf_lm_impl(tokens, offsets, lines, ranks, initial, costs);
}

extern "C" double gdt001_static_lm_score(
    const int32_t* tokens, const int64_t* offsets, int64_t lines,
    const int32_t* mapping, const double* costs) {
    return static_lm_impl(tokens, offsets, lines, mapping, costs);
}

extern "C" double gdt001_mtf_kt_score(
    const int32_t* tokens, const int64_t* offsets, int64_t lines,
    const int32_t* ranks) {
    return mtf_kt_impl(tokens, offsets, lines, ranks);
}

extern "C" void gdt001_mtf_lm_swap_scores(
    const int32_t* tokens, const int64_t* offsets, int64_t lines,
    const int32_t* ranks, const int32_t* initial, const double* costs,
    int mode, double* output) {
    const int size = mode == 0 ? SOURCE_SIGNS : TARGET_LETTERS;
    const int pairs = size * (size - 1) / 2;
    #pragma omp parallel for schedule(dynamic, 1)
    for (int index = 0; index < pairs; ++index) {
        int left = 0, remaining = index;
        while (remaining >= size - left - 1) { remaining -= size - left - 1; ++left; }
        const int right = left + 1 + remaining;
        int32_t trial_ranks[SOURCE_SIGNS], trial_initial[TARGET_LETTERS];
        std::copy(ranks, ranks + SOURCE_SIGNS, trial_ranks);
        std::copy(initial, initial + TARGET_LETTERS, trial_initial);
        if (mode == 0) std::swap(trial_ranks[left], trial_ranks[right]);
        else std::swap(trial_initial[left], trial_initial[right]);
        output[index] = mtf_lm_impl(tokens, offsets, lines, trial_ranks, trial_initial, costs);
    }
}

extern "C" void gdt001_static_lm_swap_scores(
    const int32_t* tokens, const int64_t* offsets, int64_t lines,
    const int32_t* mapping, const double* costs, double* output) {
    constexpr int size = TARGET_LETTERS;
    constexpr int pairs = size * (size - 1) / 2;
    #pragma omp parallel for schedule(dynamic, 1)
    for (int index = 0; index < pairs; ++index) {
        int left = 0, remaining = index;
        while (remaining >= size - left - 1) { remaining -= size - left - 1; ++left; }
        const int right = left + 1 + remaining;
        int32_t trial[TARGET_LETTERS];
        std::copy(mapping, mapping + TARGET_LETTERS, trial);
        std::swap(trial[left], trial[right]);
        output[index] = static_lm_impl(tokens, offsets, lines, trial, costs);
    }
}

extern "C" void gdt001_mtf_kt_swap_scores(
    const int32_t* tokens, const int64_t* offsets, int64_t lines,
    const int32_t* ranks, double* output) {
    constexpr int size = SOURCE_SIGNS;
    constexpr int pairs = size * (size - 1) / 2;
    #pragma omp parallel for schedule(dynamic, 1)
    for (int index = 0; index < pairs; ++index) {
        int left = 0, remaining = index;
        while (remaining >= size - left - 1) { remaining -= size - left - 1; ++left; }
        const int right = left + 1 + remaining;
        int32_t trial[SOURCE_SIGNS];
        std::copy(ranks, ranks + SOURCE_SIGNS, trial);
        std::swap(trial[left], trial[right]);
        output[index] = mtf_kt_impl(tokens, offsets, lines, trial);
    }
}
