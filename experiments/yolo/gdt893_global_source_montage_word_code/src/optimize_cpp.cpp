// Exact C++ implementation of the frozen GDT893 weighted compatibility model.
// INPUT: n; then n records: paragraphInt weight npairs code value ...
// OUTPUT: JSON.  Candidate indices are their original zero-based input order.
// No source strings, target readers, solution cap, or score repair are present.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using Clock = std::chrono::steady_clock;
using Weight = std::int64_t;

struct BudgetExpired {};

struct Candidate {
    int paragraph = -1;
    Weight weight = 0;
    std::vector<std::pair<int, int>> mapping;
};

struct Domain {
    int paragraph = -1;
    Weight maximum = 0;
    std::vector<int> candidates;
};

struct Stats {
    std::uint64_t candidates_read = 0, paragraphs = 0, negative_removed = 0;
    std::uint64_t nodes = 0, branches = 0, compatibility_checks = 0;
    std::uint64_t candidates_filtered = 0, bound_prunes = 0, leaves = 0;
    std::uint64_t improvements = 0, maximum_depth = 0;
};

class Solver {
public:
    explicit Solver(double seconds) : began(Clock::now()), allowance(seconds) {}

    void run(const std::string &input_path) {
        try {
            check(true);
            read(input_path);
            check(true);
            stage = "search";
            std::vector<int> selected;
            search(initial_domains, 0, root_upper, selected, 1);
            check(true);
            complete = true;
        } catch (const BudgetExpired &) {
            complete = false;
        }
    }

    void write(const std::string &output_path) const {
        std::ofstream out(output_path);
        if (!out) throw std::runtime_error("Cannot open result output");
        out << std::setprecision(17);
        out << "{\"status\":\"" << (complete ? "COMPLETE" : "UNKNOWN_BUDGET")
            << "\",\"best_weight\":" << best << ",\"optimal_solutions\":[";
        bool first_solution = true;
        for (const auto &solution : optimal) {
            if (!first_solution) out << ',';
            first_solution = false;
            out << '[';
            for (std::size_t i = 0; i < solution.size(); ++i) {
                if (i) out << ',';
                out << solution[i];
            }
            out << ']';
        }
        out << "],\"stats\":{"
            << "\"candidates\":" << declared_candidates
            << ",\"candidates_read\":" << stats.candidates_read
            << ",\"paragraphs\":" << stats.paragraphs
            << ",\"negative_weight_candidates_removed\":" << stats.negative_removed
            << ",\"nodes\":" << stats.nodes
            << ",\"branches\":" << stats.branches
            << ",\"candidate_compatibility_checks\":" << stats.compatibility_checks
            << ",\"candidates_filtered\":" << stats.candidates_filtered
            << ",\"upper_bound_prunes\":" << stats.bound_prunes
            << ",\"leaves\":" << stats.leaves
            << ",\"best_improvements\":" << stats.improvements
            << ",\"maximum_stack_depth\":" << stats.maximum_depth
            << ",\"cipher_word_ids\":" << forward.size()
            << ",\"plaintext_word_ids\":" << reverse.size()
            << ",\"elapsed_seconds\":" << elapsed()
            << ",\"best_weight_is_proven\":" << (complete ? "true" : "false")
            << ",\"upper_bound\":";
        if (complete) out << best;
        else if (upper_available) out << root_upper;
        else out << "null";
        out << ",\"budget_stage\":";
        if (complete) out << "null";
        else out << '"' << stage << '"';
        out << "}}\n";
        if (!out) throw std::runtime_error("Failed to write complete result output");
        std::cout << "{\"status\":\"" << (complete ? "COMPLETE" : "UNKNOWN_BUDGET")
                  << "\",\"best_weight\":" << best
                  << ",\"solution_sets\":" << optimal.size() << "}\n";
    }

private:
    Clock::time_point began;
    double allowance;
    std::uint64_t operations = 0;
    std::uint64_t declared_candidates = 0;
    bool complete = false, upper_available = false;
    std::string stage = "preparation";
    Weight best = 0, root_upper = 0;
    std::set<std::vector<int>> optimal{{}};
    std::vector<Candidate> candidates;
    std::vector<Domain> initial_domains;
    std::vector<int> forward, reverse;
    Stats stats;

    double elapsed() const {
        return std::chrono::duration<double>(Clock::now() - began).count();
    }

    void check(bool force = false) {
        ++operations;
        if ((force || (operations & 4095U) == 0) && elapsed() >= allowance)
            throw BudgetExpired{};
    }

    static Weight add_weight(Weight left, Weight right) {
        if (right < 0 || left < 0 || left > std::numeric_limits<Weight>::max() - right)
            throw std::runtime_error("Nonnegative coverage weight overflows int64");
        return left + right;
    }

    static int intern(std::unordered_map<std::int64_t, int> &ids, std::int64_t value) {
        auto found = ids.find(value);
        if (found != ids.end()) return found->second;
        if (ids.size() >= static_cast<std::size_t>(std::numeric_limits<int>::max()))
            throw std::runtime_error("Too many distinct word IDs");
        int index = static_cast<int>(ids.size());
        ids.emplace(value, index);
        return index;
    }

    void read(const std::string &input_path) {
        std::ifstream input(input_path);
        if (!input) throw std::runtime_error("Cannot open candidate input");
        std::int64_t count;
        if (!(input >> count) || count < 0 || count > std::numeric_limits<int>::max())
            throw std::runtime_error("Invalid candidate count");
        declared_candidates = static_cast<std::uint64_t>(count);
        candidates.reserve(static_cast<std::size_t>(count));
        std::unordered_map<std::int64_t, int> cipher_ids, plain_ids;
        std::map<std::int64_t, std::vector<int>> paragraphs;
        std::vector<int> values;
        for (std::int64_t i = 0; i < count; ++i) {
            check();
            std::int64_t paragraph, weight, pairs;
            if (!(input >> paragraph >> weight >> pairs) || pairs < 0 || pairs > std::numeric_limits<int>::max())
                throw std::runtime_error("Invalid candidate record header");
            Candidate candidate;
            candidate.weight = weight;
            candidate.mapping.reserve(static_cast<std::size_t>(pairs));
            values.clear();
            for (std::int64_t j = 0; j < pairs; ++j) {
                check();
                std::int64_t code, value;
                if (!(input >> code >> value)) throw std::runtime_error("Incomplete mapping record");
                int left = intern(cipher_ids, code), right = intern(plain_ids, value);
                candidate.mapping.emplace_back(left, right);
                values.push_back(right);
            }
            std::sort(candidate.mapping.begin(), candidate.mapping.end());
            for (std::size_t j = 1; j < candidate.mapping.size(); ++j)
                if (candidate.mapping[j - 1].first == candidate.mapping[j].first)
                    throw std::runtime_error("Duplicate code ID in candidate mapping");
            std::sort(values.begin(), values.end());
            if (std::adjacent_find(values.begin(), values.end()) != values.end())
                throw std::runtime_error("Noninjective candidate mapping");
            candidates.push_back(std::move(candidate));
            auto &domain = paragraphs[paragraph];
            if (weight >= 0) domain.push_back(static_cast<int>(i));
            else ++stats.negative_removed;
            ++stats.candidates_read;
        }
        std::string extra;
        if (input >> extra) throw std::runtime_error("Unexpected trailing candidate data");
        stats.paragraphs = paragraphs.size();
        int paragraph_index = 0;
        for (auto &entry : paragraphs) {
            check();
            Domain domain;
            domain.paragraph = paragraph_index++;
            domain.candidates = std::move(entry.second);
            for (int index : domain.candidates) {
                candidates[index].paragraph = domain.paragraph;
                domain.maximum = std::max(domain.maximum, candidates[index].weight);
            }
            if (!domain.candidates.empty()) {
                root_upper = add_weight(root_upper, domain.maximum);
                initial_domains.push_back(std::move(domain));
            }
        }
        forward.assign(cipher_ids.size(), -1);
        reverse.assign(plain_ids.size(), -1);
        upper_available = true;
    }

    bool compatible(int index) {
        ++stats.compatibility_checks;
        for (const auto &pair : candidates[index].mapping) {
            check();
            int assigned = forward[pair.first];
            if (assigned != -1 && assigned != pair.second) return false;
            assigned = reverse[pair.second];
            if (assigned != -1 && assigned != pair.first) return false;
        }
        return true;
    }

    std::vector<std::pair<int, int>> apply(int index) {
        std::vector<std::pair<int, int>> added;
        for (const auto &pair : candidates[index].mapping) {
            check();
            if (forward[pair.first] == -1) {
                if (reverse[pair.second] != -1)
                    throw std::logic_error("A filtered candidate violated reverse compatibility");
                forward[pair.first] = pair.second;
                reverse[pair.second] = pair.first;
                added.push_back(pair);
            } else if (forward[pair.first] != pair.second || reverse[pair.second] != pair.first) {
                throw std::logic_error("A filtered candidate violated forward compatibility");
            }
        }
        return added;
    }

    void undo(const std::vector<std::pair<int, int>> &added) {
        for (const auto &pair : added) {
            forward[pair.first] = -1;
            reverse[pair.second] = -1;
        }
    }

    void record(Weight weight, const std::vector<int> &selected) {
        ++stats.leaves;
        if (weight > best) {
            best = weight;
            optimal.clear();
            ++stats.improvements;
        }
        if (weight == best) {
            auto sorted = selected;
            std::sort(sorted.begin(), sorted.end());
            optimal.insert(std::move(sorted));
        }
    }

    void search(const std::vector<Domain> &domains, Weight weight, Weight upper,
                std::vector<int> &selected, std::uint64_t depth) {
        check(true);
        ++stats.nodes;
        stats.maximum_depth = std::max(stats.maximum_depth, depth);
        // Strict inequality is essential: every equally optimal set survives.
        if (upper < best) { ++stats.bound_prunes; return; }
        if (domains.empty()) { record(weight, selected); return; }
        std::size_t chosen = 0;
        for (std::size_t i = 1; i < domains.size(); ++i) {
            check();
            const auto &left = domains[i];
            const auto &right = domains[chosen];
            if (left.candidates.size() < right.candidates.size() ||
                (left.candidates.size() == right.candidates.size() &&
                 (left.maximum > right.maximum ||
                  (left.maximum == right.maximum && left.paragraph < right.paragraph)))) chosen = i;
        }
        const auto &choice_domain = domains[chosen];
        auto choices = choice_domain.candidates;
        std::sort(choices.begin(), choices.end(), [&](int left, int right) {
            const auto &a = candidates[left];
            const auto &b = candidates[right];
            if (a.weight != b.weight) return a.weight > b.weight;
            if (a.mapping.size() != b.mapping.size()) return a.mapping.size() > b.mapping.size();
            return left < right;
        });
        const Weight remaining_maximum = upper - weight - choice_domain.maximum;
        for (int choice : choices) {
            check(true);
            ++stats.branches;
            const Weight child_weight = add_weight(weight, candidates[choice].weight);
            if (add_weight(child_weight, remaining_maximum) < best) {
                ++stats.bound_prunes;
                continue;
            }
            auto added = apply(choice);
            std::vector<Domain> child;
            child.reserve(domains.size() - 1);
            Weight kept_maximum = 0, unchecked_maximum = remaining_maximum;
            bool pruned = false;
            for (std::size_t i = 0; i < domains.size(); ++i) {
                if (i == chosen) continue;
                check();
                const auto &old = domains[i];
                unchecked_maximum -= old.maximum;
                Domain next;
                next.paragraph = old.paragraph;
                next.candidates.reserve(old.candidates.size());
                for (int index : old.candidates) {
                    if (compatible(index)) {
                        next.candidates.push_back(index);
                        next.maximum = std::max(next.maximum, candidates[index].weight);
                    } else ++stats.candidates_filtered;
                }
                kept_maximum = add_weight(kept_maximum, next.maximum);
                if (!next.candidates.empty()) child.push_back(std::move(next));
                if (add_weight(add_weight(child_weight, kept_maximum), unchecked_maximum) < best) {
                    ++stats.bound_prunes;
                    pruned = true;
                    break;
                }
            }
            if (!pruned) {
                selected.push_back(choice);
                search(child, child_weight, add_weight(child_weight, kept_maximum), selected, depth + 1);
                selected.pop_back();
            }
            undo(added);
        }
        // Omission is an explicit branch.  It remains available even at an
        // equality bound, which preserves all zero-weight optional choices.
        ++stats.branches;
        if (add_weight(weight, remaining_maximum) < best) {
            ++stats.bound_prunes;
        } else {
            std::vector<Domain> rest;
            rest.reserve(domains.size() - 1);
            for (std::size_t i = 0; i < domains.size(); ++i)
                if (i != chosen) rest.push_back(domains[i]);
            search(rest, weight, add_weight(weight, remaining_maximum), selected, depth + 1);
        }
    }
};

int main(int argc, char **argv) {
    if (argc != 4) {
        std::cerr << "usage: optimize_cpp INPUT OUTPUT TIME_SECONDS\n";
        return 2;
    }
    try {
        std::size_t consumed = 0;
        std::string value(argv[3]);
        double seconds = std::stod(value, &consumed);
        if (consumed != value.size() || !std::isfinite(seconds) || seconds < 0)
            throw std::runtime_error("TIME_SECONDS must be finite and nonnegative");
        Solver solver(seconds);
        solver.run(argv[1]);
        solver.write(argv[2]);
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "INVALID_INPUT_OR_RUNTIME_ERROR: " << error.what() << '\n';
        return 2;
    }
}
