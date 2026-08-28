#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

static const string ALPHABET = "abcdefghijklmnopqrstuvwxyz ";
static const int SPACE_ID = 26;

vector<string> split(const string &s, char delimiter) {
    vector<string> out;
    string item;
    stringstream stream(s);
    while (getline(stream, item, delimiter)) out.push_back(item);
    if (!s.empty() && s.back() == delimiter) out.push_back("");
    return out;
}

vector<vector<string>> read_tsv(const string &path) {
    ifstream handle(path);
    if (!handle) throw runtime_error("cannot open " + path);
    vector<vector<string>> rows;
    string line;
    while (getline(handle, line)) rows.push_back(split(line, '\t'));
    return rows;
}

unordered_map<string, int> header_index(const vector<string> &header) {
    unordered_map<string, int> result;
    for (int i = 0; i < (int)header.size(); ++i) result[header[i]] = i;
    return result;
}

struct CharModel {
    int order = 4;
    double alpha = 0.25;
    vector<double> logp;

    static int char_id(char c) {
        if (c == ' ') return SPACE_ID;
        if (c >= 'a' && c <= 'z') return c - 'a';
        return -1;
    }

    void fit(const vector<string> &words) {
        const int size = 27;
        vector<int> ids;
        for (size_t wi = 0; wi < words.size(); ++wi) {
            if (wi) ids.push_back(SPACE_ID);
            for (char c : words[wi]) {
                int id = char_id(c);
                if (id >= 0) ids.push_back(id);
            }
        }
        vector<double> unigram(size, 0.0);
        for (int id : ids) unigram[id] += 1.0;
        double total = accumulate(unigram.begin(), unigram.end(), 0.0);
        vector<double> conditional(size);
        for (int i = 0; i < size; ++i) conditional[i] = (unigram[i] + 1.0) / (total + size);
        for (int context_order = 1; context_order < order; ++context_order) {
            int context_size = 1;
            for (int i = 0; i < context_order; ++i) context_size *= size;
            vector<double> counts((size_t)context_size * size, 0.0);
            if ((int)ids.size() > context_order) {
                int context = 0;
                for (int i = 0; i < context_order; ++i) context = context * size + ids[i];
                int modulus = context_size;
                for (int i = context_order; i < (int)ids.size(); ++i) {
                    counts[(size_t)context * size + ids[i]] += 1.0;
                    context = (context * size + ids[i]) % modulus;
                }
            }
            int lower_rows = conditional.size() / size;
            vector<double> next((size_t)context_size * size, 0.0);
            double strength = alpha * size;
            for (int context = 0; context < context_size; ++context) {
                double row_total = 0.0;
                for (int symbol = 0; symbol < size; ++symbol) row_total += counts[(size_t)context * size + symbol];
                int lower = context % lower_rows;
                for (int symbol = 0; symbol < size; ++symbol) {
                    double backoff = conditional[(size_t)lower * size + symbol];
                    next[(size_t)context * size + symbol] =
                        (counts[(size_t)context * size + symbol] + strength * backoff) / (row_total + strength);
                }
            }
            conditional.swap(next);
        }
        logp.resize(conditional.size());
        for (size_t i = 0; i < conditional.size(); ++i) logp[i] = log2(conditional[i]);
    }

    pair<double, int> score(const vector<string> &words) const {
        int letters = 0;
        for (auto &word : words) letters += word.size();
        if (!letters) return {-25.0, 0};
        int context = 0;
        for (int i = 0; i < order - 1; ++i) context = context * 27 + SPACE_ID;
        int modulus = 1;
        for (int i = 0; i < order - 1; ++i) modulus *= 27;
        double total = 0.0;
        for (size_t wi = 0; wi < words.size(); ++wi) {
            if (wi) {
                total += logp[(size_t)context * 27 + SPACE_ID];
                context = (context * 27 + SPACE_ID) % modulus;
            }
            for (char c : words[wi]) {
                int symbol = char_id(c);
                total += logp[(size_t)context * 27 + symbol];
                context = (context * 27 + symbol) % modulus;
            }
        }
        total += logp[(size_t)context * 27 + SPACE_ID];
        return {total, letters};
    }
};

enum Role { LITERAL, SYLLABIC, PREFIX, SUFFIX, CONNECTOR, CONTEXT, WHOLE, NULL_ROLE, ROLE_COUNT };
static const array<string, ROLE_COUNT> ROLE_NAMES = {
    "literal_carrier", "syllabic_carrier", "prefix_operator", "suffix_operator",
    "connector", "context_abbreviation_mark", "wholeform_logogram", "null_layout"
};
static const array<string, ROLE_COUNT> CANDIDATE_NAMES = {
    "literal", "syllabic", "prefix", "suffix", "connector", "context", "whole", "null"
};

struct Primitive {
    int id;
    string name;
    int direct_n;
    double initial_rate;
    double final_rate;
    int leaf_n;
    double leaf_fraction;
};

struct Unit {
    int id;
    string name;
    bool primitive;
    int primitive_id;
    int left;
    int right;
    int merge_rank;
    string leaves;
};

struct Chunk {
    int id;
    int count;
    double weight;
    vector<int> units;
    string unit_names;
};

struct Piece {
    Role role;
    string text;
    int source_unit;
};

struct Key {
    vector<Role> roles;
    vector<string> outputs;
    vector<int> override_type;  // 0 none, 1 short, 2 whole
    vector<string> override_output;
};

struct Decoded {
    vector<string> words;
    int violations = 0;
    int letters = 0;
    int known_chars = 0;
    int overlong = 0;
};

struct Solver {
    string prepared;
    string language;
    string kind;
    uint64_t seed;
    int iterations;
    string output_dir;
    string train_chunks_path;
    mt19937_64 rng;
    vector<Primitive> primitives;
    vector<Unit> units;
    vector<Chunk> chunks;
    array<vector<string>, ROLE_COUNT> candidates;
    vector<string> override_short_candidates;
    vector<string> override_whole_candidates;
    CharModel positive_model;
    CharModel negative_model;
    unordered_set<string> lexicon;
    vector<vector<int>> affected;
    vector<vector<Piece>> unit_piece_cache;
    vector<char> cache_ready;
    vector<double> chunk_scores;
    double total_weight = 0.0;
    int accepted = 0;
    double best_objective = -1e300;
    Key best_key;

    Solver(string prepared_, string language_, string kind_, uint64_t seed_, int iterations_, string output_dir_, string train_chunks_path_)
        : prepared(move(prepared_)), language(move(language_)), kind(move(kind_)), seed(seed_), iterations(iterations_),
          output_dir(move(output_dir_)), train_chunks_path(move(train_chunks_path_)), rng(seed) {}

    vector<string> read_words(const string &path) {
        ifstream handle(path);
        if (!handle) throw runtime_error("cannot open words " + path);
        vector<string> words;
        string word;
        while (getline(handle, word)) if (!word.empty()) words.push_back(word);
        return words;
    }

    void load() {
        auto prows = read_tsv(prepared + "/primitives.tsv");
        auto ph = header_index(prows[0]);
        for (size_t row = 1; row < prows.size(); ++row) {
            primitives.push_back({
                stoi(prows[row][ph["primitive_id"]]), prows[row][ph["primitive"]],
                stoi(prows[row][ph["direct_train_n"]]), stod(prows[row][ph["direct_chunk_initial_rate"]]),
                stod(prows[row][ph["direct_chunk_final_rate"]]), stoi(prows[row][ph["leaf_train_occurrences"]]),
                stod(prows[row][ph["leaf_train_fraction"]])
            });
        }
        if (primitives.size() != 34) throw runtime_error("primitive capacity not 34");

        auto urows = read_tsv(prepared + "/units.tsv");
        auto uh = header_index(urows[0]);
        units.resize(urows.size() - 1);
        for (size_t row = 1; row < urows.size(); ++row) {
            Unit value{
                stoi(urows[row][uh["unit_id"]]), urows[row][uh["unit"]], stoi(urows[row][uh["is_primitive"]]) != 0,
                stoi(urows[row][uh["primitive_id"]]), stoi(urows[row][uh["left_unit_id"]]),
                stoi(urows[row][uh["right_unit_id"]]), stoi(urows[row][uh["merge_rank"]]), urows[row][uh["leaves"]]
            };
            units[value.id] = value;
        }
        if (units.size() != 98) throw runtime_error("unit capacity not 98");

        auto crows = read_tsv(train_chunks_path.empty() ? prepared + "/train_chunks.tsv" : train_chunks_path);
        auto ch = header_index(crows[0]);
        for (size_t row = 1; row < crows.size(); ++row) {
            Chunk chunk;
            chunk.id = stoi(crows[row][ch["chunk_id"]]);
            chunk.count = stoi(crows[row][ch["count"]]);
            chunk.weight = stod(crows[row][ch["weight"]]);
            for (const string &part : split(crows[row][ch["units"]], ',')) if (!part.empty()) chunk.units.push_back(stoi(part));
            chunk.unit_names = ch.count("unit_names") ? crows[row][ch["unit_names"]] : "";
            chunks.push_back(move(chunk));
        }
        for (auto &chunk : chunks) total_weight += chunk.weight;

        string opposite = kind == "real" ? "destroyed" : "real";
        vector<string> positive_words = read_words(prepared + "/packs/" + language + "_" + kind + "_words.txt");
        vector<string> negative_words = read_words(prepared + "/packs/" + language + "_" + opposite + "_words.txt");
        positive_model.fit(positive_words);
        negative_model.fit(negative_words);
        lexicon.insert(positive_words.begin(), positive_words.end());

        auto cand_rows = read_tsv(prepared + "/packs/" + language + "_" + kind + "_candidates.tsv");
        auto cand_h = header_index(cand_rows[0]);
        unordered_map<string, vector<pair<int, string>>> raw;
        for (size_t row = 1; row < cand_rows.size(); ++row) {
            raw[cand_rows[row][cand_h["category"]]].push_back({stoi(cand_rows[row][cand_h["rank"]]), cand_rows[row][cand_h["value"]]});
        }
        for (auto &entry : raw) sort(entry.second.begin(), entry.second.end());
        for (int role = 0; role < ROLE_COUNT - 1; ++role) {
            for (auto &item : raw[CANDIDATE_NAMES[role]]) candidates[role].push_back(item.second);
        }
        candidates[NULL_ROLE] = {""};
        for (auto &item : raw["override_short"]) override_short_candidates.push_back(item.second);
        for (auto &item : raw["override_whole"]) override_whole_candidates.push_back(item.second);

        build_affected();
        unit_piece_cache.resize(units.size());
        cache_ready.resize(units.size());
    }

    void collect_dependencies(int uid, set<int> &deps) const {
        const Unit &unit = units[uid];
        if (unit.primitive) {
            deps.insert(unit.primitive_id);
        } else {
            deps.insert(34 + uid);
            collect_dependencies(unit.left, deps);
            collect_dependencies(unit.right, deps);
        }
    }

    void build_affected() {
        affected.assign(34 + units.size(), {});
        for (int ci = 0; ci < (int)chunks.size(); ++ci) {
            set<int> deps;
            for (int uid : chunks[ci].units) collect_dependencies(uid, deps);
            for (int dep : deps) affected[dep].push_back(ci);
        }
    }

    double random01() { return generate_canonical<double, 64>(rng); }
    int randint(int limit) { return uniform_int_distribution<int>(0, limit - 1)(rng); }

    Key initialize_key() {
        static const array<int, ROLE_COUNT> counts = {18, 4, 3, 3, 2, 2, 1, 1};
        vector<Role> slots;
        for (int role = 0; role < ROLE_COUNT; ++role) for (int i = 0; i < counts[role]; ++i) slots.push_back((Role)role);
        Key key;
        key.roles.resize(34);
        key.outputs.resize(34);
        key.override_type.assign(units.size(), 0);
        key.override_output.assign(units.size(), "");
        bool valid = false;
        for (int attempt = 0; attempt < 10000 && !valid; ++attempt) {
            shuffle(slots.begin(), slots.end(), rng);
            valid = true;
            for (int i = 0; i < 34; ++i) {
                key.roles[i] = slots[i];
                if (slots[i] == NULL_ROLE && primitives[i].leaf_fraction > 0.03 + 1e-12) valid = false;
            }
        }
        if (!valid) throw runtime_error("cannot initialize legal null");
        for (int role = 0; role < ROLE_COUNT; ++role) {
            vector<int> ids;
            for (int pid = 0; pid < 34; ++pid) if (key.roles[pid] == role) ids.push_back(pid);
            vector<string> pool = candidates[role];
            shuffle(pool.begin(), pool.end(), rng);
            if (pool.size() < ids.size()) throw runtime_error("candidate pool too small");
            for (size_t i = 0; i < ids.size(); ++i) key.outputs[ids[i]] = pool[i];
        }
        return key;
    }

    const vector<Piece> &pieces_for(int uid, const Key &key) {
        if (cache_ready[uid]) return unit_piece_cache[uid];
        cache_ready[uid] = 1;
        auto &out = unit_piece_cache[uid];
        out.clear();
        const Unit &unit = units[uid];
        if (unit.primitive) {
            int pid = unit.primitive_id;
            out.push_back({key.roles[pid], key.outputs[pid], uid});
        } else if (key.override_type[uid] != 0) {
            Role role = key.override_type[uid] == 2 ? WHOLE : SYLLABIC;
            out.push_back({role, key.override_output[uid], uid});
        } else {
            const auto &left = pieces_for(unit.left, key);
            out.insert(out.end(), left.begin(), left.end());
            const auto &right = pieces_for(unit.right, key);
            out.insert(out.end(), right.begin(), right.end());
        }
        return out;
    }

    void rebuild_cache() {
        fill(cache_ready.begin(), cache_ready.end(), 0);
        for (int uid = 0; uid < (int)units.size(); ++uid) pieces_for(uid, current_key_ref);
    }

    // current_key_ref is assigned before cache construction; it avoids threading a key through recursive references.
    Key current_key_ref;

    void build_cache(const Key &key) {
        current_key_ref = key;
        fill(cache_ready.begin(), cache_ready.end(), 0);
        for (int uid = 0; uid < (int)units.size(); ++uid) pieces_for(uid, current_key_ref);
    }

    void score_segment(const vector<Role> &roles, int &violations) const {
        if (roles.empty()) return;
        int first_core = -1, last_core = -1;
        for (int i = 0; i < (int)roles.size(); ++i) {
            if (roles[i] == LITERAL || roles[i] == SYLLABIC) {
                if (first_core < 0) first_core = i;
                last_core = i;
            }
        }
        if (first_core < 0) {
            violations += roles.size();
            return;
        }
        for (int i = 0; i < (int)roles.size(); ++i) {
            Role role = roles[i];
            if (role == PREFIX && i > first_core) ++violations;
            if (role == SUFFIX && i < last_core) ++violations;
            if (role == CONTEXT) {
                bool left_core = i > 0 && (roles[i - 1] == LITERAL || roles[i - 1] == SYLLABIC);
                bool right_core = i + 1 < (int)roles.size() && (roles[i + 1] == LITERAL || roles[i + 1] == SYLLABIC);
                if (!left_core && !right_core) ++violations;
            }
            if ((role == LITERAL || role == SYLLABIC || role == CONTEXT || role == PREFIX) && i > last_core) {
                bool suffix_before = false;
                for (int j = last_core + 1; j < i; ++j) if (roles[j] == SUFFIX) suffix_before = true;
                if (suffix_before) ++violations;
            }
        }
    }

    Decoded decode_chunk(const Chunk &chunk) const {
        Decoded decoded;
        string current;
        vector<Role> current_roles;
        auto flush = [&]() {
            if (!current.empty()) {
                decoded.words.push_back(current);
                score_segment(current_roles, decoded.violations);
            } else if (!current_roles.empty()) {
                score_segment(current_roles, decoded.violations);
            }
            current.clear();
            current_roles.clear();
        };
        for (int uid : chunk.units) {
            for (const Piece &piece : unit_piece_cache[uid]) {
                if (piece.role == NULL_ROLE || piece.text.empty()) continue;
                if (piece.role == WHOLE || piece.role == CONNECTOR) {
                    flush();
                    decoded.words.push_back(piece.text);
                } else {
                    current += piece.text;
                    current_roles.push_back(piece.role);
                }
            }
        }
        flush();
        for (const string &word : decoded.words) {
            decoded.letters += word.size();
            if (word.size() >= 2 && lexicon.count(word)) decoded.known_chars += word.size();
            if (word.size() > 12) decoded.overlong += (word.size() - 12) * (word.size() - 12);
        }
        return decoded;
    }

    double score_chunk(int index) const {
        Decoded decoded = decode_chunk(chunks[index]);
        if (!decoded.letters) return -25.0;
        auto positive = positive_model.score(decoded.words);
        auto negative = negative_model.score(decoded.words);
        double margin = (positive.first - negative.first) / decoded.letters;
        double lexicon_bonus = 0.12 * decoded.known_chars / decoded.letters;
        double overlong_penalty = 0.03 * decoded.overlong / decoded.letters;
        double grammar_penalty = 0.12 * decoded.violations;
        return margin + lexicon_bonus - overlong_penalty - grammar_penalty;
    }

    double key_prior(const Key &key) const {
        double value = 0.0;
        for (int pid = 0; pid < 34; ++pid) {
            const Primitive &p = primitives[pid];
            double directional = p.initial_rate - p.final_rate;
            Role role = key.roles[pid];
            if (role == PREFIX) value += 0.8 * directional;
            if (role == SUFFIX) value -= 0.8 * directional;
            if ((p.name == "C" || p.name == "d" || p.name == "q") && role == PREFIX) value += 0.30;
            if (p.name == "y" && role == SUFFIX) value += 0.30;
            if (p.name == "o" && role == CONNECTOR) value += 0.30;
            if (role == SYLLABIC || role == PREFIX || role == SUFFIX || role == CONNECTOR || role == CONTEXT)
                value -= 0.08 * max<int>(0, key.outputs[pid].size() - 1);
            if (role == WHOLE) value -= 0.35 + 0.08 * key.outputs[pid].size();
        }
        int active = 0, whole = 0;
        for (int uid = 0; uid < (int)units.size(); ++uid) {
            if (key.override_type[uid] == 1) {
                ++active;
                value -= 6.0 + 0.5 * key.override_output[uid].size();
            } else if (key.override_type[uid] == 2) {
                ++active;
                ++whole;
                value -= 10.0 + 0.75 * key.override_output[uid].size();
            }
        }
        if (active > 8 || whole > 4) return -1e300;
        return value;
    }

    bool output_used(const Key &key, Role role, const string &value, int except_pid) const {
        for (int pid = 0; pid < 34; ++pid) {
            if (pid != except_pid && key.roles[pid] == role && key.outputs[pid] == value) return true;
        }
        return false;
    }

    bool override_output_used(const Key &key, int type, const string &value, int except_uid) const {
        for (int uid = 0; uid < (int)units.size(); ++uid) {
            if (uid != except_uid && key.override_type[uid] == type && key.override_output[uid] == value) return true;
        }
        return false;
    }

    pair<int, int> override_counts(const Key &key) const {
        int active = 0, whole = 0;
        for (int type : key.override_type) {
            active += type != 0;
            whole += type == 2;
        }
        return {active, whole};
    }

    vector<int> legal_merge_units() const {
        vector<int> result;
        for (const Unit &unit : units) if (!unit.primitive) result.push_back(unit.id);
        return result;
    }

    bool propose(Key &key, vector<int> &changed_dependencies) {
        double move = random01();
        if (move < 0.55) {
            int a = randint(34), b = randint(34);
            if (a == b) return false;
            if (key.roles[a] == NULL_ROLE && primitives[b].leaf_fraction > 0.03 + 1e-12) return false;
            if (key.roles[b] == NULL_ROLE && primitives[a].leaf_fraction > 0.03 + 1e-12) return false;
            swap(key.roles[a], key.roles[b]);
            swap(key.outputs[a], key.outputs[b]);
            changed_dependencies = {a, b};
            return true;
        }
        if (move < 0.78) {
            int pid = randint(34);
            Role role = key.roles[pid];
            if (role == NULL_ROLE) return false;
            const auto &pool = candidates[role];
            for (int attempt = 0; attempt < 40; ++attempt) {
                string value = pool[randint(pool.size())];
                if (value != key.outputs[pid] && !output_used(key, role, value, pid)) {
                    key.outputs[pid] = value;
                    changed_dependencies = {pid};
                    return true;
                }
            }
            return false;
        }

        vector<int> merges = legal_merge_units();
        int uid = merges[randint(merges.size())];
        auto [active_count, whole_count] = override_counts(key);
        int type = key.override_type[uid];
        if (type == 0) {
            if (active_count >= 8) {
                vector<int> active;
                for (int candidate : merges) if (key.override_type[candidate]) active.push_back(candidate);
                if (active.empty()) return false;
                int source = active[randint(active.size())];
                if (units[uid].name == "qok" && key.override_type[source] == 2) return false;
                key.override_type[uid] = key.override_type[source];
                key.override_output[uid] = key.override_output[source];
                key.override_type[source] = 0;
                key.override_output[source].clear();
                changed_dependencies = {34 + uid, 34 + source};
                return true;
            }
            int new_type = (whole_count < 4 && random01() < 0.35) ? 2 : 1;
            if (units[uid].name == "qok" && new_type == 2) new_type = 1;
            const auto &pool = new_type == 2 ? override_whole_candidates : override_short_candidates;
            for (int attempt = 0; attempt < 50; ++attempt) {
                string value = pool[randint(pool.size())];
                if (!override_output_used(key, new_type, value, uid)) {
                    key.override_type[uid] = new_type;
                    key.override_output[uid] = value;
                    changed_dependencies = {34 + uid};
                    return true;
                }
            }
            return false;
        }
        double submove = random01();
        if (submove < 0.25) {
            key.override_type[uid] = 0;
            key.override_output[uid].clear();
            changed_dependencies = {34 + uid};
            return true;
        }
        if (submove < 0.80) {
            const auto &pool = type == 2 ? override_whole_candidates : override_short_candidates;
            for (int attempt = 0; attempt < 50; ++attempt) {
                string value = pool[randint(pool.size())];
                if (value != key.override_output[uid] && !override_output_used(key, type, value, uid)) {
                    key.override_output[uid] = value;
                    changed_dependencies = {34 + uid};
                    return true;
                }
            }
            return false;
        }
        int new_type = type == 1 ? 2 : 1;
        if (new_type == 2 && whole_count >= 4) return false;
        if (new_type == 2 && units[uid].name == "qok") return false;
        const auto &pool = new_type == 2 ? override_whole_candidates : override_short_candidates;
        for (int attempt = 0; attempt < 50; ++attempt) {
            string value = pool[randint(pool.size())];
            if (!override_output_used(key, new_type, value, uid)) {
                key.override_type[uid] = new_type;
                key.override_output[uid] = value;
                changed_dependencies = {34 + uid};
                return true;
            }
        }
        return false;
    }

    vector<int> union_affected(const vector<int> &deps) const {
        vector<int> result;
        vector<char> seen(chunks.size(), 0);
        for (int dep : deps) {
            for (int index : affected[dep]) if (!seen[index]) {
                seen[index] = 1;
                result.push_back(index);
            }
        }
        return result;
    }

    void anneal() {
        Key key = initialize_key();
        build_cache(key);
        chunk_scores.resize(chunks.size());
        double total = key_prior(key);
        for (int i = 0; i < (int)chunks.size(); ++i) {
            chunk_scores[i] = score_chunk(i);
            total += chunks[i].weight * chunk_scores[i];
        }
        best_objective = total;
        best_key = key;
        double start_temp = 20.0, end_temp = 0.01;
        for (int iteration = 0; iteration < iterations; ++iteration) {
            Key proposed = key;
            vector<int> deps;
            if (!propose(proposed, deps)) continue;
            double proposed_prior = key_prior(proposed);
            if (proposed_prior < -1e200) continue;
            vector<int> indices = union_affected(deps);
            build_cache(proposed);
            double old_part = 0.0, new_part = 0.0;
            vector<double> new_scores;
            new_scores.reserve(indices.size());
            for (int index : indices) {
                old_part += chunks[index].weight * chunk_scores[index];
                double value = score_chunk(index);
                new_scores.push_back(value);
                new_part += chunks[index].weight * value;
            }
            double old_prior = key_prior(key);
            double delta = new_part - old_part + proposed_prior - old_prior;
            double fraction = iteration / max(1.0, iterations - 1.0);
            double temperature = start_temp * pow(end_temp / start_temp, fraction);
            bool accept = delta >= 0.0 || random01() < exp(delta / temperature);
            if (accept) {
                key = move(proposed);
                total += delta;
                for (size_t cursor = 0; cursor < indices.size(); ++cursor) chunk_scores[indices[cursor]] = new_scores[cursor];
                ++accepted;
                if (total > best_objective) {
                    best_objective = total;
                    best_key = key;
                }
            } else {
                build_cache(key);
            }
            if ((iteration + 1) % 5000 == 0) {
                cerr << language << "\t" << kind << "\t" << seed << "\t" << (iteration + 1)
                     << "\t" << fixed << setprecision(6) << total / total_weight << "\t" << accepted << "\n";
            }
        }
        build_cache(best_key);
    }

    static string join_words(const vector<string> &words, const string &separator) {
        string result;
        for (size_t i = 0; i < words.size(); ++i) {
            if (i) result += separator;
            result += words[i];
        }
        return result;
    }

    string piece_trace(int uid) const {
        string result;
        const auto &pieces = unit_piece_cache[uid];
        for (size_t i = 0; i < pieces.size(); ++i) {
            if (i) result += ";";
            result += ROLE_NAMES[pieces[i].role] + ":" + pieces[i].text;
        }
        return result;
    }

    vector<string> unit_words(int uid) const {
        Chunk pseudo{0, 1, 1.0, {uid}, units[uid].name};
        return decode_chunk(pseudo).words;
    }

    void write_outputs() {
        string mkdir_cmd = "mkdir -p '" + output_dir + "'";
        if (system(mkdir_cmd.c_str()) != 0) throw runtime_error("mkdir failed");
        {
            ofstream out(output_dir + "/primitive_mapping.tsv");
            out << "primitive_id\tprimitive\trole\toutput\tleaf_train_fraction\tdirect_chunk_initial_rate\tdirect_chunk_final_rate\n";
            for (int pid = 0; pid < 34; ++pid) {
                out << pid << '\t' << primitives[pid].name << '\t' << ROLE_NAMES[best_key.roles[pid]] << '\t'
                    << (best_key.outputs[pid].empty() ? "<EMPTY>" : best_key.outputs[pid]) << '\t'
                    << setprecision(12) << primitives[pid].leaf_fraction << '\t' << primitives[pid].initial_rate << '\t'
                    << primitives[pid].final_rate << '\n';
            }
        }
        {
            ofstream out(output_dir + "/merge_overrides.tsv");
            out << "unit_id\tmerge_rank\tunit\ttype\toutput\tleaves\n";
            for (const Unit &unit : units) if (best_key.override_type[unit.id]) {
                out << unit.id << '\t' << unit.merge_rank << '\t' << unit.name << '\t'
                    << (best_key.override_type[unit.id] == 2 ? "wholeform" : "short") << '\t'
                    << best_key.override_output[unit.id] << '\t' << unit.leaves << '\n';
            }
        }
        {
            ofstream out(output_dir + "/unit_mapping.tsv");
            out << "unit_id\tunit\tis_primitive\tmerge_rank\texact_override\tdecoded_words\tdecoded_text\tpiece_trace\tleaves\n";
            for (const Unit &unit : units) {
                vector<string> words = unit_words(unit.id);
                out << unit.id << '\t' << unit.name << '\t' << (unit.primitive ? 1 : 0) << '\t' << unit.merge_rank << '\t'
                    << (best_key.override_type[unit.id] ? 1 : 0) << '\t' << join_words(words, "|") << '\t'
                    << join_words(words, " ") << '\t' << piece_trace(unit.id) << '\t' << unit.leaves << '\n';
            }
        }
        int active = 0, whole = 0;
        for (int type : best_key.override_type) { active += type != 0; whole += type == 2; }
        int null_pid = -1;
        for (int pid = 0; pid < 34; ++pid) if (best_key.roles[pid] == NULL_ROLE) null_pid = pid;
        {
            ofstream out(output_dir + "/summary.tsv");
            out << "language\tkind\tseed\titerations\taccepted_moves\ttrain_objective_per_sqrt_weight\tactive_overrides\twholeform_overrides\tnull_primitive\tnull_leaf_mass\n";
            out << language << '\t' << kind << '\t' << seed << '\t' << iterations << '\t' << accepted << '\t'
                << setprecision(12) << best_objective / total_weight << '\t' << active << '\t' << whole << '\t'
                << primitives[null_pid].name << '\t' << primitives[null_pid].leaf_fraction << '\n';
        }
    }
};

int main(int argc, char **argv) {
    try {
        unordered_map<string, string> args;
        for (int i = 1; i + 1 < argc; i += 2) args[argv[i]] = argv[i + 1];
        for (string required : {"--prepared", "--language", "--kind", "--seed", "--iterations", "--output"})
            if (!args.count(required)) throw runtime_error("missing " + required);
        string train = args.count("--train-chunks") ? args["--train-chunks"] : "";
        Solver solver(args["--prepared"], args["--language"], args["--kind"], stoull(args["--seed"]),
                      stoi(args["--iterations"]), args["--output"], train);
        solver.load();
        solver.anneal();
        solver.write_outputs();
        return 0;
    } catch (const exception &error) {
        cerr << "ERROR\t" << error.what() << "\n";
        return 2;
    }
}
