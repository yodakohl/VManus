// Independent exhaustive S3-action checker: forward dense coefficient arrays.
// No producer import.  Ranks are one byte per numeric sign mask; 255 is unknown.
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <omp.h>

constexpr int MAX_D = 20;
constexpr double SECONDS = 1200.0;
using Vec = std::array<unsigned char, MAX_D>;
using Word = std::vector<int>;
struct Reduction {
    int rank = 0;
    std::array<Vec, MAX_D> rows{};
    std::array<bool, MAX_D> pivot{};
};

static void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

static int mod3(int value) {
    int remainder = value % 3;
    return remainder < 0 ? remainder + 3 : remainder;
}

static Vec coefficients(const Word& word, std::uint32_t mask, int dimension) {
    Vec value{};
    for (int symbol : word) {
        if ((mask >> symbol) & 1U) {
            // Literal forward recurrence c <- epsilon_a*c, independently of
            // the producer's reverse suffix-sign accumulation.
            for (int j = 0; j < dimension; ++j)
                value[j] = value[j] == 0 ? 0 : 3 - value[j];
        }
        value[symbol] = value[symbol] == 2 ? 0 : value[symbol] + 1;
    }
    return value;
}

static Reduction reduce(const std::vector<Word>& words, std::uint32_t mask, int dimension) {
    Reduction result;
    const Vec reference = coefficients(words.front(), mask, dimension);
    for (std::size_t i = 1; i < words.size(); ++i) {
        Vec row = coefficients(words[i], mask, dimension);
        for (int j = 0; j < dimension; ++j) row[j] = mod3(int(row[j]) - int(reference[j]));
        for (int column = 0; column < dimension; ++column) {
            if (!row[column]) continue;
            if (result.pivot[column]) {
                const int multiplier = row[column];
                for (int j = column; j < dimension; ++j)
                    row[j] = mod3(int(row[j]) - multiplier * int(result.rows[column][j]));
            } else {
                if (row[column] == 2)
                    for (int j = column; j < dimension; ++j) row[j] = (2 * row[j]) % 3;
                result.rows[column] = row;
                result.pivot[column] = true;
                ++result.rank;
                break;
            }
        }
        if (result.rank == dimension) break;
    }
    return result;
}

static std::vector<Vec> nullspace(const Reduction& reduction, int dimension) {
    std::vector<Vec> basis;
    for (int free_column = 0; free_column < dimension; ++free_column) {
        if (reduction.pivot[free_column]) continue;
        Vec vector{};
        vector[free_column] = 1;
        for (int column = dimension - 1; column >= 0; --column) {
            if (!reduction.pivot[column]) continue;
            int sum = 0;
            for (int j = column + 1; j < dimension; ++j) sum += reduction.rows[column][j] * vector[j];
            vector[column] = mod3(-sum);
        }
        basis.push_back(vector);
    }
    return basis;
}

static int endpoint(const Word& word, std::uint32_t mask, const Vec& translation, int start = 0) {
    int state = start;
    for (int symbol : word) state = mod3((((mask >> symbol) & 1U) ? -state : state) + translation[symbol]);
    return state;
}

static void check_nullspace(const std::vector<Word>& words, std::uint32_t mask,
                            const std::vector<Vec>& basis) {
    for (const Vec& translation : basis) {
        const int expected = endpoint(words.front(), mask, translation);
        for (const Word& word : words)
            require(endpoint(word, mask, translation) == expected, "nullspace endpoint replay failed");
    }
}

static void selftest() {
    std::set<std::array<int, 3>> actions;
    for (int epsilon : {-1, 1}) for (int b = 0; b < 3; ++b) {
        std::array<int, 3> action{};
        for (int x = 0; x < 3; ++x) action[x] = mod3(epsilon * x + b);
        require(std::set<int>(action.begin(), action.end()).size() == 3, "affine action not bijective");
        actions.insert(action);
    }
    require(actions.size() == 6, "affine actions do not enumerate S3");
    // Exhaustively compare the linear expression with scalar state transitions.
    for (int length = 0; length <= 5; ++length) for (int word_mask = 0; word_mask < (1 << length); ++word_mask) {
        Word word;
        for (int i = 0; i < length; ++i) word.push_back((word_mask >> i) & 1);
        for (unsigned mask = 0; mask < 4; ++mask) for (int a = 0; a < 3; ++a) for (int b = 0; b < 3; ++b) {
            Vec translation{}; translation[0] = a; translation[1] = b;
            const Vec c = coefficients(word, mask, 2);
            int slope = 1;
            for (int symbol : word) if ((mask >> symbol) & 1U) slope = -slope;
            for (int start = 0; start < 3; ++start)
                require(endpoint(word, mask, translation, start) == mod3(slope * start + c[0] * a + c[1] * b),
                        "forward coefficient expression differs from direct action");
        }
    }
    for (unsigned mask = 0; mask < 2; ++mask)
        require(reduce({{0}, {0, 0}}, mask, 1).rank == 1, "unit-rank fixture failed");
    const std::vector<Word> odd_words{{0}, {0, 0, 0}};
    require(reduce(odd_words, 0, 1).rank == 1, "translation fixture failed");
    const Reduction deficient = reduce(odd_words, 1, 1);
    require(deficient.rank == 0, "nontrivial reflection fixture failed");
    const auto basis = nullspace(deficient, 1);
    require(basis.size() == 1 && basis[0][0] == 1, "reflection nullspace wrong");
    check_nullspace(odd_words, 1, basis);
    for (unsigned mask = 0; mask < 4; ++mask) {
        const std::vector<Word> same_endpoint{{0}, {1}};
        const auto r = reduce(same_endpoint, mask, 2);
        require(r.rank == 1, "shared one-letter endpoint fixture failed");
        check_nullspace(same_endpoint, mask, nullspace(r, 2));
        require(reduce({{0}, {1}, {0, 0}, {1, 1}}, mask, 2).rank == 2, "two-symbol exclusion fixture failed");
    }
}

static std::string quoted(const std::string& value) {
    std::string result = "\"";
    for (unsigned char c : value) {
        require(c >= 32, "control character in metadata");
        if (c == '\\' || c == '"') result += '\\';
        result += char(c);
    }
    return result + "\"";
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--selftest") {
            selftest();
            std::cout << "{\"status\":\"PASS\",\"checks\":\"S3 enumeration, exhaustive two-symbol short-word actions, ranks, nullspace replay\"}\n";
            return 0;
        }
        require(argc == 4, "usage: independent input.tsv output.json ranks.bin");
        const auto begun = std::chrono::steady_clock::now();
        std::ifstream input(argv[1]);
        require(bool(input), "cannot open input");
        std::string line;
        require(bool(std::getline(input, line)), "missing TSV header");
        if (!line.empty() && line.back() == '\r') line.pop_back();
        require(line == "locus\tliteral", "unexpected TSV header");
        std::vector<std::string> loci, literals;
        std::set<std::string> unique_loci;
        std::set<char> alphabet_set;
        while (std::getline(input, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            const auto tab = line.find('\t');
            require(tab != std::string::npos && line.find('\t', tab + 1) == std::string::npos, "bad input row");
            const std::string locus = line.substr(0, tab), literal = line.substr(tab + 1);
            require(!locus.empty() && !literal.empty(), "empty locus or literal");
            require(locus.rfind("f84", 0) != 0, "sealed locus forbidden");
            require(unique_loci.insert(locus).second, "duplicate locus");
            for (char c : literal) { require(c >= 'a' && c <= 'z', "nonliteral character"); alphabet_set.insert(c); }
            loci.push_back(locus); literals.push_back(literal);
        }
        require(!literals.empty(), "no input lines");
        const std::string alphabet(alphabet_set.begin(), alphabet_set.end());
        const int dimension = int(alphabet.size());
        require(dimension > 0 && dimension <= MAX_D, "alphabet dimension outside declared bound");
        std::array<int, 256> index{};
        for (int i = 0; i < dimension; ++i) index[static_cast<unsigned char>(alphabet[i])] = i;
        std::vector<Word> words;
        for (const std::string& literal : literals) {
            Word word;
            for (unsigned char c : literal) word.push_back(index[c]);
            words.push_back(std::move(word));
        }
        selftest();
        const std::uint32_t masks = 1U << dimension;
        std::vector<unsigned char> ranks(masks, 255);
        std::atomic<bool> expired(false);
        omp_set_dynamic(0);
        #pragma omp parallel for schedule(dynamic, 16) num_threads(16)
        for (std::int64_t signed_mask = 0; signed_mask < masks; ++signed_mask) {
            if (expired.load(std::memory_order_relaxed)) continue;
            const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - begun).count();
            if (elapsed >= SECONDS) { expired.store(true, std::memory_order_relaxed); continue; }
            ranks[signed_mask] = static_cast<unsigned char>(reduce(words, static_cast<std::uint32_t>(signed_mask), dimension).rank);
        }
        std::ofstream binary(argv[3], std::ios::binary);
        require(bool(binary), "cannot open ranks output");
        binary.write(reinterpret_cast<const char*>(ranks.data()), ranks.size());
        binary.close();
        require(bool(binary), "ranks output write failed");
        std::array<std::uint64_t, MAX_D + 1> histogram{};
        std::uint64_t processed = 0, deficient_count = 0;
        std::vector<std::uint32_t> diagnostic_masks;
        for (std::uint32_t mask = 0; mask < masks; ++mask) if (ranks[mask] != 255) {
            ++processed; ++histogram[ranks[mask]];
            if (ranks[mask] < dimension) {
                ++deficient_count;
                if (diagnostic_masks.size() < 100) diagnostic_masks.push_back(mask);
            }
        }
        const std::string status = processed != masks ? "INCOMPLETE" : deficient_count ? "NONTRIVIAL_START_ORBIT_MODELS_EXIST" : "NO_NONTRIVIAL_START_ORBIT";
        std::ofstream output(argv[2]);
        require(bool(output), "cannot open JSON output");
        output << "{\"status\":" << quoted(status) << ",\"alphabet\":" << quoted(alphabet)
               << ",\"reference_locus\":" << quoted(loci.front()) << ",\"lines\":" << words.size()
               << ",\"masks\":" << masks << ",\"processed\":" << processed
               << ",\"unprocessed\":" << masks - processed << ",\"deficient_masks\":" << deficient_count
               << ",\"threads_max\":16,\"seconds_limit\":1200,\"rank_histogram\":[";
        for (int i = 0; i <= dimension; ++i) { if (i) output << ','; output << histogram[i]; }
        output << "],\"diagnostics_truncated\":" << (deficient_count > diagnostic_masks.size() ? "true" : "false") << ",\"nullspaces\":[";
        bool first = true;
        for (std::uint32_t mask : diagnostic_masks) {
            const Reduction reduction = reduce(words, mask, dimension);
            require(reduction.rank == ranks[mask], "diagnostic rank differs");
            const auto basis = nullspace(reduction, dimension);
            require(int(basis.size()) == dimension - reduction.rank, "wrong nullity");
            check_nullspace(words, mask, basis);
            if (!first) output << ',';
            first = false;
            output << "{\"mask\":" << mask << ",\"rank\":" << reduction.rank << ",\"basis\":[";
            for (std::size_t i = 0; i < basis.size(); ++i) {
                if (i) output << ',';
                output << '[';
                for (int j = 0; j < dimension; ++j) { if (j) output << ','; output << int(basis[i][j]); }
                output << ']';
            }
            output << "]}";
        }
        output << "]}\n";
        output.close();
        require(bool(output), "JSON output write failed");
        std::cout << "{\"status\":" << quoted(status) << ",\"processed\":" << processed << ",\"deficient_masks\":" << deficient_count << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "independent checker error: " << error.what() << '\n';
        return 1;
    }
}
