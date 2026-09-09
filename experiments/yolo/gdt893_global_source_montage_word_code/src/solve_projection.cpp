// GDT893 exact symbolic optimum family and universal projection.
// INPUT: n; n records: paragraphInt weight npairs code value ...
// The frozen input plus the PROVED maximum defines every optimum, including
// zero-weight omission ties. No optimum count or materialized all-tie list.
// CLI: solve_projection INPUT OUTPUT TIME_SECONDS
// Membership replay: solve_projection --member INPUT OPTIMUM_WEIGHT [INDEX ...]
// Membership replay checks a supplied weight, not the proof of maximality.
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
    std::int64_t original_paragraph = 0;
    Weight weight = 0;
    std::vector<std::pair<int, int>> mapping;
};
struct Domain {
    int paragraph = -1;
    Weight maximum = 0;
    std::vector<int> candidates;
};
struct Certificate {
    bool pair_query = false;
    int candidate = -1, code = -1, value = -1;
    std::string outcome;
    std::vector<int> witness;
    std::uint64_t nodes = 0;
    double seconds = 0;
};
struct Stats {
    std::uint64_t candidates_read = 0, paragraphs = 0, negative_removed = 0;
    std::uint64_t nodes = 0, branches = 0, compatibility_checks = 0;
    std::uint64_t candidates_filtered = 0, bound_prunes = 0;
    std::uint64_t improvements = 0, maximum_depth = 0;
    std::uint64_t candidate_queries = 0, pair_queries = 0;
};

class Solver {
public:
    explicit Solver(double seconds) : began(Clock::now()), allowance(seconds) {}

    void run(const std::string &path) {
        try {
            check(true);
            read(path);
            check(true);
            stage = "maximum_weight";
            std::vector<int> selected;
            search(initial_domains, 0, root_upper, selected, 1, false);
            maximum_proven = true;
            one_optimum = current_witness;
            std::sort(one_optimum.begin(), one_optimum.end());
            stage = "universal_projection";
            projection();
            check(true);
            complete = true;
        } catch (const BudgetExpired &) {
            complete = false;
            if (!maximum_proven) {
                one_optimum = current_witness;
                std::sort(one_optimum.begin(), one_optimum.end());
            }
        }
    }

    bool member(const std::string &path, Weight required, const std::vector<int> &indices) {
        read(path);
        std::set<int> unique;
        std::set<std::int64_t> paragraphs;
        __int128 total = 0;
        for (int index : indices) {
            if (index < 0 || static_cast<std::size_t>(index) >= candidates.size() ||
                !unique.insert(index).second) return false;
            const auto &candidate = candidates[index];
            if (!paragraphs.insert(candidate.original_paragraph).second || !compatible(index))
                return false;
            apply(index);
            total += static_cast<__int128>(candidate.weight);
        }
        return total == static_cast<__int128>(required);
    }

    void write(const std::string &path) const {
        std::ofstream out(path);
        if (!out) throw std::runtime_error("Cannot open result output");
        out << std::setprecision(17);
        out << "{\"status\":\"" << (complete ? "COMPLETE" : "UNKNOWN_BUDGET")
            << "\",\"best_weight\":" << best << ",\"oneoptimum\":";
        vector_json(out, one_optimum);
        // UNKNOWN never presents an unfinished intersection as universal.
        out << ",\"forced_candidate_indices\":";
        if (complete) vector_json(out, std::vector<int>(common_candidates.begin(), common_candidates.end()));
        else out << "null";
        out << ",\"forced_word_values\":";
        if (complete) {
            out << '[';
            std::vector<std::pair<std::int64_t, std::int64_t>> originals;
            for (const auto &pair : common_pairs)
                originals.emplace_back(original_codes[pair.first], original_values[pair.second]);
            std::sort(originals.begin(), originals.end());
            for (std::size_t i = 0; i < originals.size(); ++i) {
                if (i) out << ',';
                out << '[' << originals[i].first << ',' << originals[i].second << ']';
            }
            out << ']';
        } else out << "null";
        out << ",\"symbolic_optima\":{\"schema\":\"GDT893_CANDIDATE_SELECTION_V1\","
            << "\"constraint_source\":\"frozen_input_candidate_records_in_original_order\","
            << "\"candidate_count\":" << declared_candidates
            << ",\"maximum_weight_is_proven\":" << (maximum_proven ? "true" : "false")
            << ",\"maximum_weight\":";
        if (maximum_proven) out << best; else out << "null";
        out << ",\"variables\":\"x_i in {0,1} for every input candidate i\","
            << "\"constraints\":[\"For each paragraph p: sum(x_i: paragraph_i=p)<=1\","
            << "\"For every selected mapping pair (a,u),(b,v): (a=b) iff (u=v)\","
            << "\"sum(weight_i*x_i)=maximum_weight\"],"
            << "\"omitted_paragraphs\":\"untranslated\","
            << "\"membership_cli\":\"solve_projection --member INPUT MAXIMUM_WEIGHT [INDEX ...]\","
            << "\"binding\":\"The caller must retain and hash-bind the exact input records and executable source.\"}"
            << ",\"query_certificates\":[";
        for (std::size_t i = 0; i < certificates.size(); ++i) {
            if (i) out << ',';
            const auto &certificate = certificates[i];
            out << "{\"kind\":\"" << (certificate.pair_query ? "FORBID_WORD_PAIR" : "FORBID_CANDIDATE")
                << "\",\"target_weight\":" << best;
            if (certificate.pair_query)
                out << ",\"word_pair\":[" << original_codes[certificate.code] << ','
                    << original_values[certificate.value] << ']';
            else out << ",\"candidate_index\":" << certificate.candidate;
            out << ",\"outcome\":\"" << certificate.outcome << "\",\"witness\":";
            if (certificate.outcome == "FOUND_WITNESS") vector_json(out, certificate.witness);
            else out << "null";
            out << ",\"nodes\":" << certificate.nodes << ",\"elapsed_seconds\":" << certificate.seconds << '}';
        }
        out << "],\"stats\":{\"candidates\":" << declared_candidates
            << ",\"candidates_read\":" << stats.candidates_read
            << ",\"paragraphs\":" << stats.paragraphs
            << ",\"negative_weight_candidates_removed\":" << stats.negative_removed
            << ",\"nodes\":" << stats.nodes << ",\"branches\":" << stats.branches
            << ",\"candidate_compatibility_checks\":" << stats.compatibility_checks
            << ",\"candidates_filtered\":" << stats.candidates_filtered
            << ",\"upper_bound_prunes\":" << stats.bound_prunes
            << ",\"best_improvements\":" << stats.improvements
            << ",\"maximum_stack_depth\":" << stats.maximum_depth
            << ",\"candidate_projection_queries\":" << stats.candidate_queries
            << ",\"word_projection_queries\":" << stats.pair_queries
            << ",\"cipher_word_ids\":" << forward.size()
            << ",\"plaintext_word_ids\":" << reverse.size()
            << ",\"elapsed_seconds\":" << elapsed()
            << ",\"best_weight_is_proven\":" << (maximum_proven ? "true" : "false")
            << ",\"universal_projection_is_complete\":" << (complete ? "true" : "false")
            << ",\"upper_bound\":";
        if (maximum_proven) out << best;
        else if (upper_available) out << root_upper;
        else out << "null";
        out << ",\"budget_stage\":";
        if (complete) out << "null"; else out << '"' << stage << '"';
        out << "}}\n";
        if (!out) throw std::runtime_error("Failed to write complete result output");
        std::cout << "{\"status\":\"" << (complete ? "COMPLETE" : "UNKNOWN_BUDGET")
                  << "\",\"best_weight\":" << best
                  << ",\"best_weight_is_proven\":" << (maximum_proven ? "true" : "false") << "}\n";
    }

private:
    Clock::time_point began;
    double allowance;
    std::uint64_t operations = 0, declared_candidates = 0;
    bool complete = false, maximum_proven = false, upper_available = false;
    std::string stage = "preparation";
    Weight best = 0, root_upper = 0;
    std::vector<int> one_optimum, current_witness;
    std::vector<Candidate> candidates;
    std::vector<Domain> initial_domains;
    std::vector<int> forward, reverse;
    std::vector<std::int64_t> original_codes, original_values;
    std::set<int> common_candidates, proven_candidates;
    std::map<int, int> common_pairs;
    std::set<std::pair<int, int>> proven_pairs;
    std::vector<Certificate> certificates;
    Stats stats;

    static void vector_json(std::ostream &out, const std::vector<int> &indices) {
        out << '[';
        for (std::size_t i = 0; i < indices.size(); ++i) {
            if (i) out << ',';
            out << indices[i];
        }
        out << ']';
    }
    double elapsed() const {
        return std::chrono::duration<double>(Clock::now() - began).count();
    }
    void check(bool force = false) {
        ++operations;
        if ((force || (operations & 4095U) == 0) && elapsed() >= allowance) throw BudgetExpired{};
    }
    static Weight add_weight(Weight left, Weight right) {
        if (right < 0 || left < 0 || left > std::numeric_limits<Weight>::max() - right)
            throw std::runtime_error("Nonnegative coverage weight overflows int64");
        return left + right;
    }
    static int intern(std::unordered_map<std::int64_t, int> &ids,
                      std::vector<std::int64_t> &originals, std::int64_t value) {
        auto found = ids.find(value);
        if (found != ids.end()) return found->second;
        if (ids.size() >= static_cast<std::size_t>(std::numeric_limits<int>::max()))
            throw std::runtime_error("Too many distinct word IDs");
        int index = static_cast<int>(ids.size());
        ids.emplace(value, index);
        originals.push_back(value);
        return index;
    }
    void read(const std::string &path) {
        std::ifstream input(path);
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
            candidate.original_paragraph = paragraph;
            candidate.weight = weight;
            candidate.mapping.reserve(static_cast<std::size_t>(pairs));
            values.clear();
            for (std::int64_t j = 0; j < pairs; ++j) {
                check();
                std::int64_t code, value;
                if (!(input >> code >> value)) throw std::runtime_error("Incomplete mapping record");
                int left = intern(cipher_ids, original_codes, code);
                int right = intern(plain_ids, original_values, value);
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
            for (int index : domain.candidates)
                domain.maximum = std::max(domain.maximum, candidates[index].weight);
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
                if (reverse[pair.second] != -1) throw std::logic_error("Reverse incompatibility");
                forward[pair.first] = pair.second;
                reverse[pair.second] = pair.first;
                added.push_back(pair);
            } else if (forward[pair.first] != pair.second || reverse[pair.second] != pair.first)
                throw std::logic_error("Forward incompatibility");
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
        if (weight > best) {
            best = weight;
            current_witness = selected;
            ++stats.improvements;
        }
    }
    bool cannot_improve(Weight upper, bool query) const {
        return query ? upper < best : upper <= best;
    }
    bool search(const std::vector<Domain> &domains, Weight weight, Weight upper,
                std::vector<int> &selected, std::uint64_t depth, bool query) {
        check(true);
        ++stats.nodes;
        stats.maximum_depth = std::max(stats.maximum_depth, depth);
        if (query && weight == best) { current_witness = selected; return true; }
        if (!query) record(weight, selected);
        if (cannot_improve(upper, query)) { ++stats.bound_prunes; return false; }
        if (domains.empty()) return false;
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
            if (cannot_improve(add_weight(child_weight, remaining_maximum), query)) {
                ++stats.bound_prunes;
                continue;
            }
            auto added = apply(choice);
            selected.push_back(choice);
            if (query && child_weight == best) {
                current_witness = selected;
                selected.pop_back();
                undo(added);
                return true;
            }
            if (!query) record(child_weight, selected);
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
                if (cannot_improve(add_weight(add_weight(child_weight, kept_maximum), unchecked_maximum), query)) {
                    ++stats.bound_prunes;
                    pruned = true;
                    break;
                }
            }
            bool found = !pruned && search(child, child_weight, add_weight(child_weight, kept_maximum),
                                          selected, depth + 1, query);
            selected.pop_back();
            undo(added);
            if (found) return true;
        }
        ++stats.branches;
        if (cannot_improve(add_weight(weight, remaining_maximum), query)) ++stats.bound_prunes;
        else {
            std::vector<Domain> rest;
            rest.reserve(domains.size() - 1);
            for (std::size_t i = 0; i < domains.size(); ++i)
                if (i != chosen) rest.push_back(domains[i]);
            if (search(rest, weight, add_weight(weight, remaining_maximum), selected, depth + 1, query)) return true;
        }
        return false;
    }

    std::map<int, int> word_map(const std::vector<int> &indices) {
        std::map<int, int> mapping;
        for (int index : indices) for (const auto &pair : candidates[index].mapping) {
            check();
            mapping.emplace(pair);
        }
        return mapping;
    }
    void intersect_witness(const std::vector<int> &witness) {
        std::set<int> selected(witness.begin(), witness.end());
        for (auto it = common_candidates.begin(); it != common_candidates.end();) {
            check();
            if (selected.count(*it)) ++it; else it = common_candidates.erase(it);
        }
        auto mapping = word_map(witness);
        for (auto it = common_pairs.begin(); it != common_pairs.end();) {
            check();
            auto found = mapping.find(it->first);
            if (found != mapping.end() && found->second == it->second) ++it;
            else it = common_pairs.erase(it);
        }
    }
    bool run_query(Certificate certificate) {
        auto start = Clock::now();
        auto before_nodes = stats.nodes;
        bool found = false;
        if (certificate.pair_query) ++stats.pair_queries; else ++stats.candidate_queries;
        try {
            check(true);
            std::fill(forward.begin(), forward.end(), -1);
            std::fill(reverse.begin(), reverse.end(), -1);
            std::vector<Domain> domains;
            Weight upper = 0;
            for (const auto &old : initial_domains) {
                Domain next;
                next.paragraph = old.paragraph;
                next.candidates.reserve(old.candidates.size());
                for (int index : old.candidates) {
                    check();
                    bool excluded = index == certificate.candidate;
                    if (certificate.pair_query)
                        excluded = std::binary_search(candidates[index].mapping.begin(), candidates[index].mapping.end(),
                                                      std::make_pair(certificate.code, certificate.value));
                    if (!excluded) {
                        next.candidates.push_back(index);
                        next.maximum = std::max(next.maximum, candidates[index].weight);
                    }
                }
                if (!next.candidates.empty()) {
                    upper = add_weight(upper, next.maximum);
                    domains.push_back(std::move(next));
                }
            }
            std::vector<int> selected;
            found = search(domains, 0, upper, selected, 1, true);
            certificate.outcome = found ? "FOUND_WITNESS" : "EXHAUSTIVE_UNSAT";
            if (found) {
                certificate.witness = current_witness;
                std::sort(certificate.witness.begin(), certificate.witness.end());
            }
        } catch (const BudgetExpired &) {
            certificate.outcome = "UNKNOWN_BUDGET";
            certificate.nodes = stats.nodes - before_nodes;
            certificate.seconds = std::chrono::duration<double>(Clock::now() - start).count();
            certificates.push_back(std::move(certificate));
            throw;
        }
        certificate.nodes = stats.nodes - before_nodes;
        certificate.seconds = std::chrono::duration<double>(Clock::now() - start).count();
        certificates.push_back(certificate);
        // An intersection timeout leaves the completed query certificate valid;
        // it must not append a second, contradictory UNKNOWN for that query.
        if (found) intersect_witness(certificate.witness);
        return found;
    }
    void projection() {
        common_candidates.insert(one_optimum.begin(), one_optimum.end());
        common_pairs = word_map(one_optimum);
        while (true) {
            check(true);
            auto choice = std::find_if(common_candidates.begin(), common_candidates.end(),
                                      [&](int index) { return !proven_candidates.count(index); });
            if (choice == common_candidates.end()) break;
            int index = *choice;
            Certificate query;
            query.candidate = index;
            if (!run_query(query)) {
                proven_candidates.insert(index);
                for (const auto &pair : candidates[index].mapping) proven_pairs.insert(pair);
            }
        }
        while (true) {
            check(true);
            auto choice = std::find_if(common_pairs.begin(), common_pairs.end(),
                                      [&](const auto &pair) { return !proven_pairs.count(pair); });
            if (choice == common_pairs.end()) break;
            auto pair = *choice;
            Certificate query;
            query.pair_query = true;
            query.code = pair.first;
            query.value = pair.second;
            if (!run_query(query)) proven_pairs.insert(pair);
        }
    }
};

static std::int64_t parse_integer(const std::string &value) {
    std::size_t consumed = 0;
    auto parsed = std::stoll(value, &consumed);
    if (consumed != value.size()) throw std::runtime_error("Invalid integer argument");
    return parsed;
}
int main(int argc, char **argv) {
    try {
        if (argc >= 4 && std::string(argv[1]) == "--member") {
            Weight required = parse_integer(argv[3]);
            std::vector<int> indices;
            for (int i = 4; i < argc; ++i) {
                auto parsed = parse_integer(argv[i]);
                if (parsed < 0 || parsed > std::numeric_limits<int>::max()) {
                    std::cout << "{\"member\":false}\n";
                    return 0;
                }
                indices.push_back(static_cast<int>(parsed));
            }
            Solver solver(std::numeric_limits<double>::infinity());
            std::cout << "{\"member\":" << (solver.member(argv[2], required, indices) ? "true" : "false") << "}\n";
            return 0;
        }
        if (argc != 4) {
            std::cerr << "usage: solve_projection INPUT OUTPUT TIME_SECONDS\n"
                      << "   or: solve_projection --member INPUT OPTIMUM_WEIGHT [INDEX ...]\n";
            return 2;
        }
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
