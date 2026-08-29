#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <mutex>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <variant>
#include <vector>

namespace fs = std::filesystem;

namespace {

constexpr int kMergeCount = 64;
constexpr int kPaidBudget = 8;
constexpr int kMaxSubstringLength = 12;
constexpr std::uint64_t kAllMerges = std::numeric_limits<std::uint64_t>::max();

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

std::string read_file(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) fail("cannot open input: " + path.string());
    std::ostringstream buffer;
    buffer << in.rdbuf();
    if (!in.good() && !in.eof()) fail("cannot read input: " + path.string());
    return buffer.str();
}

std::vector<std::string> split(const std::string& value, char delimiter) {
    std::vector<std::string> fields;
    std::size_t begin = 0;
    while (true) {
        const std::size_t end = value.find(delimiter, begin);
        fields.push_back(value.substr(begin, end == std::string::npos ? end : end - begin));
        if (end == std::string::npos) break;
        begin = end + 1;
    }
    return fields;
}

std::string lower_ascii(std::string value) {
    for (char& ch : value) ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
    return value;
}

std::string json_escape(const std::string& value) {
    std::ostringstream out;
    for (const unsigned char ch : value) {
        switch (ch) {
            case '\"': out << "\\\""; break;
            case '\\': out << "\\\\"; break;
            case '\b': out << "\\b"; break;
            case '\f': out << "\\f"; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (ch < 0x20) {
                    out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                        << static_cast<unsigned>(ch) << std::dec;
                } else {
                    out << static_cast<char>(ch);
                }
        }
    }
    return out.str();
}

// Minimal, strict JSON reader.  It deliberately implements no repository-specific shortcuts.
struct Json {
    using Array = std::vector<Json>;
    using Object = std::map<std::string, Json>;
    std::variant<std::nullptr_t, bool, double, std::string, Array, Object> value;

    bool is_object() const { return std::holds_alternative<Object>(value); }
    bool is_array() const { return std::holds_alternative<Array>(value); }
    bool is_string() const { return std::holds_alternative<std::string>(value); }
    bool is_number() const { return std::holds_alternative<double>(value); }
    bool is_bool() const { return std::holds_alternative<bool>(value); }
    const Object& object() const { return std::get<Object>(value); }
    const Array& array() const { return std::get<Array>(value); }
    const std::string& string() const { return std::get<std::string>(value); }
    double number() const { return std::get<double>(value); }
    bool boolean() const { return std::get<bool>(value); }
    const Json& at(const std::string& key) const {
        const auto& obj = object();
        const auto found = obj.find(key);
        if (found == obj.end()) fail("missing JSON key: " + key);
        return found->second;
    }
    const Json* find(const std::string& key) const {
        if (!is_object()) return nullptr;
        const auto found = object().find(key);
        return found == object().end() ? nullptr : &found->second;
    }
    int integer() const {
        const double x = number();
        const auto result = static_cast<int>(x);
        if (static_cast<double>(result) != x) fail("expected integral JSON number");
        return result;
    }
};

class JsonParser {
public:
    explicit JsonParser(const std::string& text) : text_(text) {}
    Json parse() {
        Json result = parse_value();
        whitespace();
        if (position_ != text_.size()) fail("trailing bytes in JSON");
        return result;
    }

private:
    const std::string& text_;
    std::size_t position_ = 0;

    void whitespace() {
        while (position_ < text_.size() && std::isspace(static_cast<unsigned char>(text_[position_]))) {
            ++position_;
        }
    }
    char peek() {
        whitespace();
        if (position_ >= text_.size()) fail("unexpected end of JSON");
        return text_[position_];
    }
    bool consume(char expected) {
        whitespace();
        if (position_ < text_.size() && text_[position_] == expected) {
            ++position_;
            return true;
        }
        return false;
    }
    void require(char expected) {
        if (!consume(expected)) fail(std::string("expected JSON byte: ") + expected);
    }
    Json parse_value() {
        switch (peek()) {
            case '{': return Json{parse_object()};
            case '[': return Json{parse_array()};
            case '"': return Json{parse_string()};
            case 't': literal("true"); return Json{true};
            case 'f': literal("false"); return Json{false};
            case 'n': literal("null"); return Json{nullptr};
            default: return Json{parse_number()};
        }
    }
    void literal(const std::string& expected) {
        whitespace();
        if (text_.substr(position_, expected.size()) != expected) fail("bad JSON literal");
        position_ += expected.size();
    }
    Json::Object parse_object() {
        Json::Object result;
        require('{');
        if (consume('}')) return result;
        while (true) {
            const std::string key = parse_string();
            require(':');
            if (!result.emplace(key, parse_value()).second) fail("duplicate JSON key: " + key);
            if (consume('}')) break;
            require(',');
        }
        return result;
    }
    Json::Array parse_array() {
        Json::Array result;
        require('[');
        if (consume(']')) return result;
        while (true) {
            result.push_back(parse_value());
            if (consume(']')) break;
            require(',');
        }
        return result;
    }
    static void append_utf8(std::string& out, unsigned codepoint) {
        if (codepoint <= 0x7f) out.push_back(static_cast<char>(codepoint));
        else if (codepoint <= 0x7ff) {
            out.push_back(static_cast<char>(0xc0 | (codepoint >> 6)));
            out.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        } else {
            out.push_back(static_cast<char>(0xe0 | (codepoint >> 12)));
            out.push_back(static_cast<char>(0x80 | ((codepoint >> 6) & 0x3f)));
            out.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        }
    }
    std::string parse_string() {
        require('"');
        std::string result;
        while (position_ < text_.size()) {
            const unsigned char ch = text_[position_++];
            if (ch == '"') return result;
            if (ch < 0x20) fail("control byte in JSON string");
            if (ch != '\\') {
                result.push_back(static_cast<char>(ch));
                continue;
            }
            if (position_ >= text_.size()) fail("bad JSON escape");
            switch (text_[position_++]) {
                case '"': result.push_back('"'); break;
                case '\\': result.push_back('\\'); break;
                case '/': result.push_back('/'); break;
                case 'b': result.push_back('\b'); break;
                case 'f': result.push_back('\f'); break;
                case 'n': result.push_back('\n'); break;
                case 'r': result.push_back('\r'); break;
                case 't': result.push_back('\t'); break;
                case 'u': {
                    if (position_ + 4 > text_.size()) fail("short JSON unicode escape");
                    unsigned codepoint = 0;
                    for (int i = 0; i < 4; ++i) {
                        const char digit = text_[position_++];
                        codepoint <<= 4;
                        if (digit >= '0' && digit <= '9') codepoint += digit - '0';
                        else if (digit >= 'a' && digit <= 'f') codepoint += digit - 'a' + 10;
                        else if (digit >= 'A' && digit <= 'F') codepoint += digit - 'A' + 10;
                        else fail("bad JSON unicode escape");
                    }
                    if (codepoint >= 0xd800 && codepoint <= 0xdfff) fail("surrogate JSON escape unsupported");
                    append_utf8(result, codepoint);
                    break;
                }
                default: fail("bad JSON escape");
            }
        }
        fail("unterminated JSON string");
    }
    double parse_number() {
        whitespace();
        const std::size_t begin = position_;
        if (position_ < text_.size() && text_[position_] == '-') ++position_;
        if (position_ >= text_.size()) fail("bad JSON number");
        if (text_[position_] == '0') ++position_;
        else {
            if (!std::isdigit(static_cast<unsigned char>(text_[position_]))) fail("bad JSON number");
            while (position_ < text_.size() && std::isdigit(static_cast<unsigned char>(text_[position_]))) ++position_;
        }
        if (position_ < text_.size() && text_[position_] == '.') {
            ++position_;
            if (position_ >= text_.size() || !std::isdigit(static_cast<unsigned char>(text_[position_]))) fail("bad JSON number");
            while (position_ < text_.size() && std::isdigit(static_cast<unsigned char>(text_[position_]))) ++position_;
        }
        if (position_ < text_.size() && (text_[position_] == 'e' || text_[position_] == 'E')) {
            ++position_;
            if (position_ < text_.size() && (text_[position_] == '+' || text_[position_] == '-')) ++position_;
            if (position_ >= text_.size() || !std::isdigit(static_cast<unsigned char>(text_[position_]))) fail("bad JSON number");
            while (position_ < text_.size() && std::isdigit(static_cast<unsigned char>(text_[position_]))) ++position_;
        }
        char* end = nullptr;
        const std::string token = text_.substr(begin, position_ - begin);
        const double result = std::strtod(token.c_str(), &end);
        if (!end || *end) fail("bad JSON number conversion");
        return result;
    }
};

// Compact SHA-256, used only to bind the three admitted input files.
class Sha256 {
public:
    void update(const unsigned char* data, std::size_t size) {
        bit_length_ += static_cast<std::uint64_t>(size) * 8;
        while (size) {
            const std::size_t take = std::min(size, block_.size() - block_size_);
            std::copy(data, data + take, block_.begin() + static_cast<std::ptrdiff_t>(block_size_));
            block_size_ += take;
            data += take;
            size -= take;
            if (block_size_ == block_.size()) {
                transform(block_.data());
                block_size_ = 0;
            }
        }
    }
    std::string finish() {
        block_[block_size_++] = 0x80;
        if (block_size_ > 56) {
            std::fill(block_.begin() + static_cast<std::ptrdiff_t>(block_size_), block_.end(), 0);
            transform(block_.data());
            block_size_ = 0;
        }
        std::fill(block_.begin() + static_cast<std::ptrdiff_t>(block_size_), block_.begin() + 56, 0);
        for (int i = 0; i < 8; ++i) block_[63 - i] = static_cast<unsigned char>(bit_length_ >> (8 * i));
        transform(block_.data());
        std::ostringstream out;
        out << std::hex << std::setfill('0');
        for (const auto word : state_) out << std::setw(8) << word;
        return out.str();
    }
    static std::string digest(const std::string& value) {
        Sha256 sha;
        sha.update(reinterpret_cast<const unsigned char*>(value.data()), value.size());
        return sha.finish();
    }

private:
    std::array<std::uint32_t, 8> state_ = {
        0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
        0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
    std::array<unsigned char, 64> block_{};
    std::size_t block_size_ = 0;
    std::uint64_t bit_length_ = 0;
    static constexpr std::array<std::uint32_t, 64> k_ = {
        0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
        0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
        0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
        0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
        0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
        0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
        0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
        0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u};
    static std::uint32_t rotate(std::uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
    void transform(const unsigned char* data) {
        std::array<std::uint32_t, 64> w{};
        for (int i = 0; i < 16; ++i) {
            w[i] = (static_cast<std::uint32_t>(data[4*i]) << 24) |
                   (static_cast<std::uint32_t>(data[4*i+1]) << 16) |
                   (static_cast<std::uint32_t>(data[4*i+2]) << 8) |
                   static_cast<std::uint32_t>(data[4*i+3]);
        }
        for (int i = 16; i < 64; ++i) {
            const std::uint32_t s0 = rotate(w[i-15],7) ^ rotate(w[i-15],18) ^ (w[i-15] >> 3);
            const std::uint32_t s1 = rotate(w[i-2],17) ^ rotate(w[i-2],19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        auto [a,b,c,d,e,f,g,h] = state_;
        for (int i = 0; i < 64; ++i) {
            const std::uint32_t s1 = rotate(e,6) ^ rotate(e,11) ^ rotate(e,25);
            const std::uint32_t choice = (e & f) ^ (~e & g);
            const std::uint32_t temp1 = h + s1 + choice + k_[i] + w[i];
            const std::uint32_t s0 = rotate(a,2) ^ rotate(a,13) ^ rotate(a,22);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temp2 = s0 + majority;
            h=g; g=f; f=e; e=d+temp1; d=c; c=b; b=a; a=temp1+temp2;
        }
        state_[0]+=a; state_[1]+=b; state_[2]+=c; state_[3]+=d;
        state_[4]+=e; state_[5]+=f; state_[6]+=g; state_[7]+=h;
    }
};

struct Card {
    std::string id;
    std::string role;
    std::string output;
};

struct Primitive {
    std::string id;
    std::string role;
    int group = -1;
};

struct RoleGroup {
    std::string role;
    std::vector<int> primitives;
    std::vector<Card> cards;
    std::vector<int> relevant_primitives;
};

struct Merge {
    int rank = 0;
    std::string left;
    std::string right;
    std::string name;
    std::vector<int> leaves;
    std::uint64_t subtree = 0;
};

struct Inputs {
    Json registered;
    std::string registered_bytes;
    std::string substring_bytes;
    std::string merge_bytes;
    std::string registered_sha;
    std::string substring_sha;
    std::string merge_sha;
    std::vector<Primitive> primitives;
    std::vector<RoleGroup> groups;
    std::unordered_map<std::string, int> primitive_index;
    std::unordered_map<std::string, int> group_index;
    std::vector<Merge> merges;
    std::array<std::vector<std::string>, kMaxSubstringLength + 1> substrings_by_length;
    std::array<std::unordered_set<std::string>, kMaxSubstringLength + 1> substring_sets;
    int literal_group = -1;
    std::vector<int> literal_relevant;
    std::vector<int> literal_var_of_primitive;
    std::array<int, 256> literal_card_by_char{};
    std::vector<std::vector<int>> small_tasks;
};

std::vector<std::string> read_lines_exact(const std::string& bytes) {
    std::vector<std::string> lines;
    std::size_t begin = 0;
    while (begin < bytes.size()) {
        const std::size_t end = bytes.find('\n', begin);
        std::string line = bytes.substr(begin, end == std::string::npos ? end : end - begin);
        if (!line.empty() && line.back() == '\r') line.pop_back();
        lines.push_back(std::move(line));
        if (end == std::string::npos) break;
        begin = end + 1;
    }
    return lines;
}

void validate_admitted_path(const fs::path& path, const std::string& kind) {
    const std::string lowered = lower_ascii(path.filename().string());
    if (kind == "registered" && lowered != "registered_search.json") fail("wrong registered-search basename");
    if (kind == "substrings" && lowered != "registered_train_substrings.txt") fail("wrong substring basename");
    if (kind == "merge" && lowered != "merge_tree.tsv") fail("wrong merge-tree basename");
}

Inputs load_inputs(const fs::path& registered_path, const fs::path& substring_path, const fs::path& merge_path) {
    validate_admitted_path(registered_path, "registered");
    validate_admitted_path(substring_path, "substrings");
    validate_admitted_path(merge_path, "merge");
    Inputs in;
    in.literal_card_by_char.fill(-1);
    in.registered_bytes = read_file(registered_path);
    in.substring_bytes = read_file(substring_path);
    in.merge_bytes = read_file(merge_path);
    in.registered_sha = Sha256::digest(in.registered_bytes);
    in.substring_sha = Sha256::digest(in.substring_bytes);
    in.merge_sha = Sha256::digest(in.merge_bytes);
    in.registered = JsonParser(in.registered_bytes).parse();
    if (in.registered.at("schema").string() != "gdt615-joint-output-binding-search-v1") fail("unexpected registered schema");

    const Json& train_meta = in.registered.at("registered_train_substrings");
    if (train_meta.at("sha256").string() != in.substring_sha) fail("registered train-substring SHA-256 mismatch");
    if (train_meta.at("minimum_length").integer() != 1 || train_meta.at("maximum_length").integer() != 12) {
        fail("unexpected registered substring length bounds");
    }
    std::string expected_merge_sha;
    for (const Json& row : in.registered.at("registered_inputs").array()) {
        if (fs::path(row.at("path").string()).filename() == "merge_tree.tsv") {
            expected_merge_sha = row.at("sha256").string();
        }
    }
    if (expected_merge_sha.empty() || expected_merge_sha != in.merge_sha) fail("registered merge-tree SHA-256 mismatch");

    for (const Json& row : in.registered.at("primitive_role_assignment").array()) {
        Primitive primitive{row.at("primitive_id").string(), row.at("role").string(), -1};
        if (!in.primitive_index.emplace(primitive.id, static_cast<int>(in.primitives.size())).second) {
            fail("duplicate primitive ID");
        }
        in.primitives.push_back(std::move(primitive));
    }
    if (in.primitives.size() != 34) fail("expected 34 primitive slots");

    const Json& deck = in.registered.at("primitive_output_deck");
    for (const auto& [role, rows] : deck.object()) {
        RoleGroup group;
        group.role = role;
        for (const Json& row : rows.array()) {
            group.cards.push_back(Card{row.at("card_id").string(), role, row.at("output").string()});
        }
        std::sort(group.cards.begin(), group.cards.end(), [](const Card& a, const Card& b) { return a.id < b.id; });
        if (!in.group_index.emplace(role, static_cast<int>(in.groups.size())).second) fail("duplicate role group");
        in.groups.push_back(std::move(group));
    }
    std::set<std::string> card_ids;
    for (int pi = 0; pi < static_cast<int>(in.primitives.size()); ++pi) {
        auto found = in.group_index.find(in.primitives[pi].role);
        if (found == in.group_index.end()) fail("primitive role has no deck");
        in.primitives[pi].group = found->second;
        in.groups[found->second].primitives.push_back(pi);
    }
    for (RoleGroup& group : in.groups) {
        if (group.cards.size() != group.primitives.size()) fail("role deck/slot cardinality mismatch: " + group.role);
        for (const Card& card : group.cards) {
            if (!card_ids.insert(card.id).second) fail("duplicate card ID across roles: " + card.id);
            for (char ch : card.output) if (ch < 'a' || ch > 'z') fail("non-lowercase card output");
        }
    }
    in.literal_group = in.group_index.at("literal_carrier");
    for (int ci = 0; ci < static_cast<int>(in.groups[in.literal_group].cards.size()); ++ci) {
        const std::string& output = in.groups[in.literal_group].cards[ci].output;
        if (output.size() != 1) fail("independent implementation requires registered one-byte literal cards");
        const unsigned char ch = static_cast<unsigned char>(output[0]);
        if (in.literal_card_by_char[ch] != -1) fail("duplicate literal output");
        in.literal_card_by_char[ch] = ci;
    }

    const std::vector<std::string> substring_lines = read_lines_exact(in.substring_bytes);
    if (static_cast<int>(substring_lines.size()) != train_meta.at("distinct_substring_count").integer()) {
        fail("registered substring row-count mismatch");
    }
    std::string previous;
    for (const std::string& value : substring_lines) {
        if (value.empty() || value.size() > kMaxSubstringLength) fail("invalid registered substring length");
        for (char ch : value) if (ch < 'a' || ch > 'z') fail("invalid registered substring character");
        if (!previous.empty()) {
            if (value.size() < previous.size() || (value.size() == previous.size() && value <= previous)) {
                fail("registered substrings are not strictly length/ASCII sorted");
            }
        }
        previous = value;
        in.substrings_by_length[value.size()].push_back(value);
        in.substring_sets[value.size()].insert(value);
    }

    const std::vector<std::string> merge_lines = read_lines_exact(in.merge_bytes);
    if (merge_lines.size() != 65) fail("expected header plus 64 merge rows");
    const auto header = split(merge_lines.front(), '\t');
    const std::vector<std::string> expected_header = {"rank","left","right","merged","train_occurrences","leaf_sequence","leaf_count","tree_depth"};
    if (header != expected_header) fail("unexpected merge-tree header");
    std::unordered_map<std::string, std::vector<int>> unit_leaves;
    std::unordered_map<std::string, int> merge_by_name;
    for (const auto& [id, index] : in.primitive_index) {
        unit_leaves[id] = std::vector<int>(1, index);
    }
    for (int row_index = 1; row_index <= kMergeCount; ++row_index) {
        const auto fields = split(merge_lines[row_index], '\t');
        if (fields.size() != 8) fail("malformed merge-tree row");
        Merge merge;
        merge.rank = std::stoi(fields[0]);
        merge.left = fields[1]; merge.right = fields[2]; merge.name = fields[3];
        if (merge.rank != row_index) fail("merge ranks must be exactly 1..64");
        if (!unit_leaves.contains(merge.left) || !unit_leaves.contains(merge.right)) fail("non-topological merge child");
        merge.leaves = unit_leaves.at(merge.left);
        merge.leaves.insert(merge.leaves.end(), unit_leaves.at(merge.right).begin(), unit_leaves.at(merge.right).end());
        const auto declared_leaf_ids = split(fields[5], ' ');
        if (declared_leaf_ids.size() != merge.leaves.size() || std::stoi(fields[6]) != static_cast<int>(merge.leaves.size())) {
            fail("merge leaf-count mismatch");
        }
        for (std::size_t i = 0; i < merge.leaves.size(); ++i) {
            if (declared_leaf_ids[i] != in.primitives[merge.leaves[i]].id) fail("merge recursive leaf-order mismatch");
        }
        merge.subtree = std::uint64_t{1} << (merge.rank - 1);
        const auto left_merge = merge_by_name.find(merge.left);
        if (left_merge != merge_by_name.end()) merge.subtree |= in.merges[left_merge->second].subtree;
        const auto right_merge = merge_by_name.find(merge.right);
        if (right_merge != merge_by_name.end()) merge.subtree |= in.merges[right_merge->second].subtree;
        if (unit_leaves.contains(merge.name)) fail("duplicate/colliding merged unit name");
        merge_by_name.emplace(merge.name, static_cast<int>(in.merges.size()));
        unit_leaves.emplace(merge.name, merge.leaves);
        in.merges.push_back(std::move(merge));
    }

    std::vector<bool> relevant(in.primitives.size(), false);
    for (const Merge& merge : in.merges) for (const int pi : merge.leaves) relevant[pi] = true;
    for (RoleGroup& group : in.groups) {
        for (const int pi : group.primitives) if (relevant[pi]) group.relevant_primitives.push_back(pi);
    }
    in.literal_relevant = in.groups[in.literal_group].relevant_primitives;
    in.literal_var_of_primitive.assign(in.primitives.size(), -1);
    for (int vi = 0; vi < static_cast<int>(in.literal_relevant.size()); ++vi) {
        in.literal_var_of_primitive[in.literal_relevant[vi]] = vi;
    }
    if (in.literal_relevant.size() > 18 || in.literal_relevant.empty()) fail("unexpected relevant literal capacity");

    // Generate every injective assignment on objective-relevant slots for every nonliteral role.
    // Objective-irrelevant slots receive the lexicographically least remaining cards, which is
    // exactly the required representative of their behavioral equivalence class.
    std::vector<std::vector<std::vector<std::pair<int,int>>>> role_variants;
    for (int gi = 0; gi < static_cast<int>(in.groups.size()); ++gi) {
        if (gi == in.literal_group) continue;
        const RoleGroup& group = in.groups[gi];
        std::vector<std::vector<std::pair<int,int>>> variants;
        std::vector<int> chosen(group.relevant_primitives.size(), -1);
        std::function<void(int,std::uint32_t)> generate = [&](int depth, std::uint32_t used) {
            if (depth == static_cast<int>(group.relevant_primitives.size())) {
                std::vector<std::pair<int,int>> assignment;
                for (int i = 0; i < depth; ++i) assignment.emplace_back(group.relevant_primitives[i], chosen[i]);
                std::vector<int> remaining_cards;
                for (int ci = 0; ci < static_cast<int>(group.cards.size()); ++ci) if (!(used & (1u << ci))) remaining_cards.push_back(ci);
                std::vector<int> irrelevant;
                for (const int pi : group.primitives) if (!relevant[pi]) irrelevant.push_back(pi);
                std::sort(irrelevant.begin(), irrelevant.end());
                if (remaining_cards.size() != irrelevant.size()) fail("canonical completion mismatch");
                for (std::size_t i = 0; i < irrelevant.size(); ++i) assignment.emplace_back(irrelevant[i], remaining_cards[i]);
                variants.push_back(std::move(assignment));
                return;
            }
            for (int ci = 0; ci < static_cast<int>(group.cards.size()); ++ci) {
                if (used & (1u << ci)) continue;
                chosen[depth] = ci;
                generate(depth + 1, used | (1u << ci));
            }
        };
        generate(0, 0);
        role_variants.push_back(std::move(variants));
    }
    std::vector<int> base(in.primitives.size(), -1);
    std::function<void(int,const std::vector<int>&)> combine = [&](int role, const std::vector<int>& mapping) {
        if (role == static_cast<int>(role_variants.size())) {
            in.small_tasks.push_back(mapping);
            return;
        }
        for (const auto& variant : role_variants[role]) {
            std::vector<int> next = mapping;
            for (const auto& [pi, ci] : variant) next[pi] = ci;
            combine(role + 1, next);
        }
    };
    combine(0, base);
    return in;
}

struct ExistsKey {
    std::uint64_t uncovered;
    std::uint64_t available;
    std::uint8_t slots;
    bool operator==(const ExistsKey&) const = default;
};

struct ExistsHash {
    std::size_t operator()(const ExistsKey& key) const {
        std::uint64_t x = key.uncovered ^ std::rotl(key.available, 23) ^ (static_cast<std::uint64_t>(key.slots) << 57);
        x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33;
        return static_cast<std::size_t>(x);
    }
};

class CoverSolver {
public:
    explicit CoverSolver(const std::vector<Merge>& merges) {
        for (int paid = 0; paid < kMergeCount; ++paid) {
            for (int affected = 0; affected < kMergeCount; ++affected) {
                if (merges[affected].subtree & (std::uint64_t{1} << paid)) {
                    covers_[paid] |= std::uint64_t{1} << affected;
                }
            }
            subtree_[paid] = merges[paid].subtree;
        }
    }

    int minimum_cardinality(std::uint64_t unsupported, int maximum) {
        for (int k = 0; k <= maximum; ++k) {
            memo_.clear();
            if (exists(unsupported, kAllMerges, k)) return k;
        }
        return maximum + 1;
    }

    std::optional<std::vector<int>> minimum_lex_witness(std::uint64_t unsupported, int maximum) {
        const int minimum = minimum_cardinality(unsupported, maximum);
        if (minimum > maximum) return std::nullopt;
        std::vector<int> result;
        std::uint64_t uncovered = unsupported;
        int previous = -1;
        for (int position = 0; position < minimum; ++position) {
            bool selected = false;
            const int remaining = minimum - position - 1;
            for (int candidate = previous + 1; candidate < kMergeCount; ++candidate) {
                if (kMergeCount - candidate - 1 < remaining) break;
                const std::uint64_t after = uncovered & ~covers_[candidate];
                const std::uint64_t available = candidate == 63 ? 0 : (kAllMerges << (candidate + 1));
                memo_.clear();
                if (exists(after, available, remaining)) {
                    result.push_back(candidate + 1);
                    uncovered = after;
                    previous = candidate;
                    selected = true;
                    break;
                }
            }
            if (!selected) fail("internal error constructing lexicographic minimum cover");
        }
        if (uncovered) fail("internal uncovered residue after witness construction");
        return result;
    }

private:
    std::array<std::uint64_t, kMergeCount> covers_{};
    std::array<std::uint64_t, kMergeCount> subtree_{};
    std::unordered_map<ExistsKey, bool, ExistsHash> memo_;

    bool exists(std::uint64_t uncovered, std::uint64_t available, int slots) {
        if (!uncovered) return true;
        if (slots <= 0 || !available) return false;
        const ExistsKey key{uncovered, available, static_cast<std::uint8_t>(slots)};
        const auto known = memo_.find(key);
        if (known != memo_.end()) return known->second;
        std::uint64_t union_cover = 0;
        int max_gain = 0;
        for (std::uint64_t bits = available; bits; bits &= bits - 1) {
            const int candidate = std::countr_zero(bits);
            union_cover |= covers_[candidate];
            max_gain = std::max(max_gain, std::popcount(covers_[candidate] & uncovered));
        }
        if ((uncovered & ~union_cover) || max_gain == 0 || (std::popcount(uncovered) + max_gain - 1) / max_gain > slots) {
            memo_[key] = false;
            return false;
        }
        int pivot = -1;
        int pivot_choices = 65;
        for (std::uint64_t bits = uncovered; bits; bits &= bits - 1) {
            const int element = std::countr_zero(bits);
            const int choices = std::popcount(subtree_[element] & available);
            if (choices < pivot_choices) { pivot = element; pivot_choices = choices; }
        }
        if (pivot_choices == 0) {
            memo_[key] = false;
            return false;
        }
        std::uint64_t pivot_candidates = subtree_[pivot] & available;
        std::uint64_t branch_available = available;
        while (pivot_candidates) {
            const int candidate = std::countr_zero(pivot_candidates);
            const std::uint64_t bit = std::uint64_t{1} << candidate;
            if (exists(uncovered & ~covers_[candidate], branch_available & ~bit, slots - 1)) {
                memo_[key] = true;
                return true;
            }
            branch_available &= ~bit;
            pivot_candidates &= ~bit;
        }
        memo_[key] = false;
        return false;
    }
};

struct Constraint {
    std::vector<int> variables;
    std::vector<std::vector<std::uint8_t>> tuples;
    std::vector<std::vector<std::vector<std::uint64_t>>> masks;
    std::size_t blocks = 0;

    void build_masks(int literal_card_count) {
        blocks = (tuples.size() + 63) / 64;
        masks.assign(variables.size(), std::vector<std::vector<std::uint64_t>>(
            literal_card_count, std::vector<std::uint64_t>(blocks, 0)));
        for (std::size_t row = 0; row < tuples.size(); ++row) {
            for (std::size_t pos = 0; pos < variables.size(); ++pos) {
                masks[pos][tuples[row][pos]][row / 64] |= std::uint64_t{1} << (row % 64);
            }
        }
    }

    bool possible(const std::vector<int>& assignment, std::uint32_t globally_used) const {
        if (tuples.empty()) return false;
        for (std::size_t block = 0; block < blocks; ++block) {
            std::uint64_t candidates = kAllMerges;
            if (block + 1 == blocks && tuples.size() % 64) {
                candidates = (std::uint64_t{1} << (tuples.size() % 64)) - 1;
            }
            for (std::size_t pos = 0; pos < variables.size() && candidates; ++pos) {
                const int assigned = assignment[variables[pos]];
                if (assigned >= 0) candidates &= masks[pos][assigned][block];
            }
            while (candidates) {
                const int offset = std::countr_zero(candidates);
                const std::size_t row = block * 64 + offset;
                bool valid = true;
                for (std::size_t pos = 0; pos < variables.size(); ++pos) {
                    if (assignment[variables[pos]] < 0 && (globally_used & (1u << tuples[row][pos]))) {
                        valid = false;
                        break;
                    }
                }
                if (valid) return true;
                candidates &= candidates - 1;
            }
        }
        return false;
    }
};

struct Candidate {
    bool valid = false;
    int support = -1;
    int cover = kPaidBudget + 1;
    std::vector<std::string> mapping_ids;
    std::vector<int> mapping_choices;
    std::vector<int> cover_ranks;
    std::uint64_t support_mask = 0;
};

bool better_candidate(const Candidate& a, const Candidate& b) {
    if (!a.valid) return false;
    if (!b.valid) return true;
    if (a.support != b.support) return a.support > b.support;
    if (a.cover != b.cover) return a.cover < b.cover;
    if (a.mapping_ids != b.mapping_ids) return a.mapping_ids < b.mapping_ids;
    return a.cover_ranks < b.cover_ranks;
}

struct SharedState {
    std::mutex best_mutex;
    Candidate best;
    std::atomic<int> best_support{-1};
    std::atomic<int> best_cover{kPaidBudget + 1};
    std::atomic<std::size_t> next_task{0};
    std::atomic<std::uint64_t> nodes{0};
    std::atomic<std::uint64_t> pruned_cover{0};
    std::atomic<std::uint64_t> pruned_support{0};
    std::atomic<std::uint64_t> leaves{0};
    std::atomic<std::size_t> completed_tasks{0};
    std::atomic<bool> timeout{false};
};

struct Analysis {
    bool feasible = true;
    int support_upper = 0;
    int cover_lower = 0;
    std::uint64_t possible_mask = 0;
};

class TaskSearcher {
public:
    TaskSearcher(const Inputs& inputs, SharedState& shared,
                 const std::chrono::steady_clock::time_point deadline)
        : in_(inputs), shared_(shared), deadline_(deadline), cover_solver_(inputs.merges) {
        const int variables = static_cast<int>(in_.literal_relevant.size());
        assignment_.assign(variables, -1);
        incidence_.assign(variables, 0);
        for (const Merge& merge : in_.merges) {
            std::set<int> seen;
            for (const int pi : merge.leaves) {
                const int vi = in_.literal_var_of_primitive[pi];
                if (vi >= 0) seen.insert(vi);
            }
            for (const int vi : seen) incidence_[vi] += 1 + (merge.leaves.size() <= 2 ? 8 : 0);
        }
        variable_order_.resize(variables);
        std::iota(variable_order_.begin(), variable_order_.end(), 0);
        std::sort(variable_order_.begin(), variable_order_.end(), [&](int a, int b) {
            if (incidence_[a] != incidence_[b]) return incidence_[a] > incidence_[b];
            return in_.literal_relevant[a] < in_.literal_relevant[b];
        });
    }

    ~TaskSearcher() {
        shared_.nodes.fetch_add(local_nodes_ & 4095u, std::memory_order_relaxed);
    }

    void run(std::size_t task_index) {
        base_mapping_ = in_.small_tasks[task_index];
        build_constraints();
        cover_cache_.clear();
        const Analysis root = analyze();
        if (root.feasible) dfs(0, root);
    }

private:
    const Inputs& in_;
    SharedState& shared_;
    std::chrono::steady_clock::time_point deadline_;
    CoverSolver cover_solver_;
    std::vector<int> base_mapping_;
    std::vector<int> assignment_;
    std::vector<int> variable_order_;
    std::vector<int> incidence_;
    std::uint32_t used_ = 0;
    std::array<Constraint, kMergeCount> constraints_;
    std::unordered_map<std::uint64_t, std::uint8_t> cover_cache_;
    std::uint64_t local_nodes_ = 0;

    const Card& chosen_card(int primitive_index) const {
        const Primitive& primitive = in_.primitives[primitive_index];
        int choice = base_mapping_[primitive_index];
        if (primitive.group == in_.literal_group) {
            const int vi = in_.literal_var_of_primitive[primitive_index];
            if (vi < 0 || assignment_[vi] < 0) fail("requested unresolved literal card");
            choice = assignment_[vi];
        }
        if (choice < 0) fail("requested unresolved fixed card");
        return in_.groups[primitive.group].cards[choice];
    }

    void build_constraints() {
        const int literal_cards = static_cast<int>(in_.groups[in_.literal_group].cards.size());
        for (int mi = 0; mi < kMergeCount; ++mi) {
            Constraint constraint;
            std::set<int> vars;
            int length = 0;
            for (const int pi : in_.merges[mi].leaves) {
                if (in_.primitives[pi].group == in_.literal_group) {
                    vars.insert(in_.literal_var_of_primitive[pi]);
                    ++length;
                } else {
                    const int choice = base_mapping_[pi];
                    if (choice < 0) fail("small-role task left relevant primitive unresolved");
                    length += static_cast<int>(in_.groups[in_.primitives[pi].group].cards[choice].output.size());
                }
            }
            constraint.variables.assign(vars.begin(), vars.end());
            if (length >= 1 && length <= kMaxSubstringLength) {
                std::unordered_map<int,int> position;
                for (int i = 0; i < static_cast<int>(constraint.variables.size()); ++i) position[constraint.variables[i]] = i;
                for (const std::string& substring : in_.substrings_by_length[length]) {
                    std::vector<std::uint8_t> tuple(constraint.variables.size(), 255);
                    std::uint32_t local_used = 0;
                    std::size_t offset = 0;
                    bool valid = true;
                    for (const int pi : in_.merges[mi].leaves) {
                        if (in_.primitives[pi].group == in_.literal_group) {
                            const int card = in_.literal_card_by_char[static_cast<unsigned char>(substring[offset++])];
                            if (card < 0) { valid = false; break; }
                            const int pos = position.at(in_.literal_var_of_primitive[pi]);
                            if (tuple[pos] != 255 && tuple[pos] != card) { valid = false; break; }
                            if (tuple[pos] == 255) {
                                if (local_used & (1u << card)) { valid = false; break; }
                                tuple[pos] = static_cast<std::uint8_t>(card);
                                local_used |= 1u << card;
                            }
                        } else {
                            const std::string& fixed = chosen_card(pi).output;
                            if (substring.compare(offset, fixed.size(), fixed) != 0) { valid = false; break; }
                            offset += fixed.size();
                        }
                    }
                    if (valid && offset == substring.size()) constraint.tuples.push_back(std::move(tuple));
                }
                // A tuple uniquely renders one substring because literal-card outputs are
                // globally distinct one-byte strings.  The registered substring list itself
                // is unique, so duplicate tuple elimination is neither needed nor permitted
                // to hide an input-contract violation.
            }
            constraint.build_masks(literal_cards);
            constraints_[mi] = std::move(constraint);
        }
    }

    int cover_lower(std::uint64_t forced_unsupported) {
        const auto known = cover_cache_.find(forced_unsupported);
        if (known != cover_cache_.end()) return known->second;
        const int value = cover_solver_.minimum_cardinality(forced_unsupported, kPaidBudget);
        if (cover_cache_.size() > 250000) cover_cache_.clear();
        cover_cache_[forced_unsupported] = static_cast<std::uint8_t>(value);
        return value;
    }

    Analysis analyze() {
        Analysis result;
        for (int mi = 0; mi < kMergeCount; ++mi) {
            if (constraints_[mi].possible(assignment_, used_)) result.possible_mask |= std::uint64_t{1} << mi;
        }
        result.support_upper = std::popcount(result.possible_mask);
        result.cover_lower = cover_lower(kAllMerges & ~result.possible_mask);
        if (result.cover_lower > kPaidBudget) result.feasible = false;
        const int incumbent_support = shared_.best_support.load(std::memory_order_relaxed);
        const int incumbent_cover = shared_.best_cover.load(std::memory_order_relaxed);
        if (result.support_upper < incumbent_support ||
            (result.support_upper == incumbent_support && result.cover_lower > incumbent_cover)) {
            result.feasible = false;
        }
        return result;
    }

    void dfs(int depth, const Analysis& state) {
        if (!state.feasible || shared_.timeout.load(std::memory_order_relaxed)) return;
        ++local_nodes_;
        if ((local_nodes_ & 4095) == 0) {
            shared_.nodes.fetch_add(4096, std::memory_order_relaxed);
            if (std::chrono::steady_clock::now() >= deadline_) {
                shared_.timeout.store(true, std::memory_order_relaxed);
                return;
            }
        }
        if (depth == static_cast<int>(variable_order_.size())) {
            shared_.leaves.fetch_add(1, std::memory_order_relaxed);
            evaluate_leaf(state.possible_mask);
            return;
        }
        const int variable = variable_order_[depth];
        struct Branch { int card; Analysis state; };
        std::vector<Branch> branches;
        const RoleGroup& literals = in_.groups[in_.literal_group];
        for (int card = 0; card < static_cast<int>(literals.cards.size()); ++card) {
            if (used_ & (1u << card)) continue;
            assignment_[variable] = card;
            used_ |= 1u << card;
            Analysis child = analyze();
            used_ &= ~(1u << card);
            assignment_[variable] = -1;
            if (!child.feasible) {
                if (child.cover_lower > kPaidBudget) shared_.pruned_cover.fetch_add(1, std::memory_order_relaxed);
                else shared_.pruned_support.fetch_add(1, std::memory_order_relaxed);
            } else {
                branches.push_back(Branch{card, child});
            }
        }
        std::sort(branches.begin(), branches.end(), [&](const Branch& a, const Branch& b) {
            if (a.state.support_upper != b.state.support_upper) return a.state.support_upper > b.state.support_upper;
            if (a.state.cover_lower != b.state.cover_lower) return a.state.cover_lower < b.state.cover_lower;
            return literals.cards[a.card].id < literals.cards[b.card].id;
        });
        for (const Branch& branch : branches) {
            assignment_[variable] = branch.card;
            used_ |= 1u << branch.card;
            dfs(depth + 1, branch.state);
            used_ &= ~(1u << branch.card);
            assignment_[variable] = -1;
            if (shared_.timeout.load(std::memory_order_relaxed)) break;
        }
    }

    void evaluate_leaf(std::uint64_t support_mask) {
        const std::uint64_t unsupported = kAllMerges & ~support_mask;
        auto witness = cover_solver_.minimum_lex_witness(unsupported, kPaidBudget);
        if (!witness) return;
        Candidate candidate;
        candidate.valid = true;
        candidate.support = std::popcount(support_mask);
        candidate.cover = static_cast<int>(witness->size());
        candidate.cover_ranks = *witness;
        candidate.support_mask = support_mask;
        candidate.mapping_choices = base_mapping_;
        for (int vi = 0; vi < static_cast<int>(in_.literal_relevant.size()); ++vi) {
            candidate.mapping_choices[in_.literal_relevant[vi]] = assignment_[vi];
        }
        const RoleGroup& literals = in_.groups[in_.literal_group];
        std::uint32_t used = used_;
        std::vector<int> remaining;
        for (int ci = 0; ci < static_cast<int>(literals.cards.size()); ++ci) if (!(used & (1u << ci))) remaining.push_back(ci);
        std::vector<int> irrelevant;
        for (const int pi : literals.primitives) if (in_.literal_var_of_primitive[pi] < 0) irrelevant.push_back(pi);
        std::sort(irrelevant.begin(), irrelevant.end());
        if (remaining.size() != irrelevant.size()) fail("literal canonical completion mismatch");
        for (std::size_t i = 0; i < irrelevant.size(); ++i) candidate.mapping_choices[irrelevant[i]] = remaining[i];
        for (int pi = 0; pi < static_cast<int>(in_.primitives.size()); ++pi) {
            const int choice = candidate.mapping_choices[pi];
            if (choice < 0) fail("candidate mapping incomplete");
            candidate.mapping_ids.push_back(in_.groups[in_.primitives[pi].group].cards[choice].id);
        }
        std::lock_guard<std::mutex> lock(shared_.best_mutex);
        if (better_candidate(candidate, shared_.best)) {
            const bool objective_improvement = !shared_.best.valid ||
                candidate.support != shared_.best.support || candidate.cover != shared_.best.cover;
            shared_.best = candidate;
            shared_.best_support.store(candidate.support, std::memory_order_relaxed);
            shared_.best_cover.store(candidate.cover, std::memory_order_relaxed);
            if (objective_improvement) {
                std::cerr << "INCUMBENT support=" << candidate.support << " cover=" << candidate.cover << '\n';
            }
        }
    }
};

std::vector<int> positional_mapping(const Inputs& in) {
    std::vector<int> mapping(in.primitives.size(), -1);
    for (const RoleGroup& group : in.groups) {
        if (group.cards.size() != group.primitives.size()) fail("positional control cardinality mismatch");
        for (std::size_t i = 0; i < group.primitives.size(); ++i) mapping[group.primitives[i]] = static_cast<int>(i);
    }
    return mapping;
}

struct DirectEvaluation {
    int support = 0;
    int cover = 65;
    std::uint64_t support_mask = 0;
    std::vector<int> cover_ranks;
    std::vector<std::string> renders;
};

DirectEvaluation evaluate_direct(const Inputs& in, const std::vector<int>& mapping, int cover_maximum) {
    DirectEvaluation result;
    for (int mi = 0; mi < kMergeCount; ++mi) {
        std::string render;
        for (const int pi : in.merges[mi].leaves) {
            const Primitive& primitive = in.primitives[pi];
            const int choice = mapping[pi];
            if (choice < 0) fail("direct evaluation mapping incomplete");
            render += in.groups[primitive.group].cards[choice].output;
        }
        result.renders.push_back(render);
        if (render.size() <= kMaxSubstringLength && in.substring_sets[render.size()].contains(render)) {
            result.support_mask |= std::uint64_t{1} << mi;
        }
    }
    result.support = std::popcount(result.support_mask);
    CoverSolver solver(in.merges);
    const auto witness = solver.minimum_lex_witness(kAllMerges & ~result.support_mask, cover_maximum);
    if (witness) {
        result.cover = static_cast<int>(witness->size());
        result.cover_ranks = *witness;
    } else {
        result.cover = cover_maximum + 1;
    }
    return result;
}

struct Options {
    fs::path registered;
    fs::path substrings;
    fs::path merge_tree;
    fs::path output;
    int threads = 1;
    int time_limit = 14400;
    bool control_only = false;
    bool self_test = false;
};

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto value = [&]() -> std::string {
            if (++i >= argc) fail("missing value after " + arg);
            return argv[i];
        };
        if (arg == "--registered-search") options.registered = value();
        else if (arg == "--substrings") options.substrings = value();
        else if (arg == "--merge-tree") options.merge_tree = value();
        else if (arg == "--output") options.output = value();
        else if (arg == "--threads") options.threads = std::stoi(value());
        else if (arg == "--time-limit") options.time_limit = std::stoi(value());
        else if (arg == "--control-only") options.control_only = true;
        else if (arg == "--self-test") options.self_test = true;
        else fail("unknown argument: " + arg);
    }
    if (!options.self_test && (options.registered.empty() || options.substrings.empty() || options.merge_tree.empty())) {
        fail("--registered-search, --substrings, and --merge-tree are required");
    }
    if (options.threads < 1 || options.threads > 32) fail("--threads must be in 1..32");
    if (options.time_limit < 1) fail("--time-limit must be positive");
    return options;
}

void run_self_test() {
    if (Sha256::digest("abc") != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") {
        fail("SHA-256 self-test failed");
    }
    const Json parsed = JsonParser("{\"x\":[1,true,\"z\"],\"y\":null}").parse();
    if (parsed.at("x").array()[0].integer() != 1 || !parsed.at("x").array()[1].boolean() || parsed.at("x").array()[2].string() != "z") {
        fail("JSON self-test failed");
    }
    // Every unsupported subset of a six-node miniature DAG is compared with
    // exhaustive paid-card combinations, including the lexicographic witness.
    std::vector<Merge> merges(64);
    for (int i = 0; i < 64; ++i) { merges[i].rank = i + 1; merges[i].subtree = std::uint64_t{1} << i; }
    merges[2].subtree |= merges[0].subtree | merges[1].subtree;
    merges[4].subtree |= merges[2].subtree | merges[3].subtree;
    merges[5].subtree |= merges[1].subtree;
    CoverSolver solver(merges);
    std::array<std::uint64_t, 6> covers{};
    for (int paid = 0; paid < 6; ++paid) {
        for (int affected = 0; affected < 6; ++affected) {
            if (merges[affected].subtree & (std::uint64_t{1} << paid)) {
                covers[paid] |= std::uint64_t{1} << affected;
            }
        }
    }
    for (std::uint64_t unsupported = 0; unsupported < 64; ++unsupported) {
        int brute_size = 7;
        std::vector<int> brute_witness;
        for (std::uint64_t chosen = 0; chosen < 64; ++chosen) {
            std::uint64_t covered = 0;
            for (int paid = 0; paid < 6; ++paid) {
                if (chosen & (std::uint64_t{1} << paid)) covered |= covers[paid];
            }
            if (unsupported & ~covered) continue;
            const int size = std::popcount(chosen);
            std::vector<int> ranks;
            for (int paid = 0; paid < 6; ++paid) {
                if (chosen & (std::uint64_t{1} << paid)) ranks.push_back(paid + 1);
            }
            if (size < brute_size || (size == brute_size && ranks < brute_witness)) {
                brute_size = size;
                brute_witness = std::move(ranks);
            }
        }
        const auto exact = solver.minimum_lex_witness(unsupported, 6);
        if (!exact || static_cast<int>(exact->size()) != brute_size || *exact != brute_witness) {
            fail("exhaustive miniature-DAG cover parity failed");
        }
    }
    std::cout << "SELF_TEST_PASS\n";
}

std::string render_result_json(const Inputs& in, const SharedState& shared,
                               const DirectEvaluation& control, bool complete,
                               bool control_only, bool winner_direct_replay,
                               double elapsed_seconds) {
    Candidate best;
    {
        std::lock_guard<std::mutex> lock(const_cast<std::mutex&>(shared.best_mutex));
        best = shared.best;
    }
    const Json& negative = in.registered.at("negative_control");
    const int expected_control_support = negative.at("gdt615_train_only_raw_supported_merge_count").integer();
    const int expected_control_cover = negative.at("gdt615_train_only_expected_exact_minimum").integer();
    std::ostringstream out;
    out << "{\n";
    out << "  \"schema\": \"gdt615-stage0-independent-result-v1\",\n";
    const std::string status = control_only ? "NEGATIVE_CONTROL_COMPLETE" :
        (complete ? (best.valid ? "GLOBAL_OPTIMUM_COMPLETE" : "NO_EIGHT_HIT_BINDING") : "SEARCH_INCOMPLETE");
    out << "  \"status\": \"" << status << "\",\n";
    out << "  \"complete\": " << (complete ? "true" : "false") << ",\n";
    out << "  \"input_sha256\": {\n";
    out << "    \"REGISTERED_SEARCH.json\": \"" << in.registered_sha << "\",\n";
    out << "    \"REGISTERED_TRAIN_SUBSTRINGS.txt\": \"" << in.substring_sha << "\",\n";
    out << "    \"merge_tree.tsv\": \"" << in.merge_sha << "\"\n  },\n";
    out << "  \"negative_control\": {\n";
    out << "    \"mapping_derivation\": \"role-local positional card order; independently checked against both registered expected values\",\n";
    out << "    \"raw_supported_merge_count\": " << control.support << ",\n";
    out << "    \"minimum_inclusive_dag_cover\": " << control.cover << ",\n";
    out << "    \"matches_registered_expectation\": " << ((control.support == expected_control_support && control.cover == expected_control_cover) ? "true" : "false") << ",\n";
    out << "    \"minimum_cover_ranks\": [";
    for (std::size_t i = 0; i < control.cover_ranks.size(); ++i) { if (i) out << ','; out << control.cover_ranks[i]; }
    out << "]\n  },\n";
    out << "  \"search\": {\n";
    out << "    \"small_role_tasks_total\": " << in.small_tasks.size() << ",\n";
    out << "    \"small_role_tasks_completed\": " << shared.completed_tasks.load() << ",\n";
    out << "    \"literal_relevant_slot_count\": " << in.literal_relevant.size() << ",\n";
    out << "    \"nodes_at_last_flush\": " << shared.nodes.load() << ",\n";
    out << "    \"evaluated_leaves\": " << shared.leaves.load() << ",\n";
    out << "    \"pruned_cover\": " << shared.pruned_cover.load() << ",\n";
    out << "    \"pruned_support\": " << shared.pruned_support.load() << ",\n";
    out << "    \"elapsed_seconds\": " << std::fixed << std::setprecision(3) << elapsed_seconds << "\n  },\n";
    out << "  \"winner_direct_replay_matches\": " << (winner_direct_replay ? "true" : "false") << ",\n";
    if (best.valid) {
        out << "  \"objective\": {\"raw_supported_merge_count\": " << best.support
            << ", \"minimum_inclusive_dag_cover\": " << best.cover << "},\n";
        out << "  \"mapping\": [\n";
        for (int pi = 0; pi < static_cast<int>(in.primitives.size()); ++pi) {
            const int choice = best.mapping_choices[pi];
            const Card& card = in.groups[in.primitives[pi].group].cards[choice];
            out << "    {\"primitive_id\": \"" << json_escape(in.primitives[pi].id)
                << "\", \"role\": \"" << json_escape(in.primitives[pi].role)
                << "\", \"card_id\": \"" << json_escape(card.id)
                << "\", \"output\": \"" << json_escape(card.output) << "\"}";
            out << (pi + 1 == static_cast<int>(in.primitives.size()) ? "\n" : ",\n");
        }
        out << "  ],\n";
        out << "  \"supported_merge_ranks\": [";
        bool first = true;
        for (int mi = 0; mi < kMergeCount; ++mi) if (best.support_mask & (std::uint64_t{1} << mi)) {
            if (!first) out << ',';
            first = false;
            out << mi + 1;
        }
        out << "],\n  \"minimum_cover_ranks\": [";
        for (std::size_t i = 0; i < best.cover_ranks.size(); ++i) { if (i) out << ','; out << best.cover_ranks[i]; }
        out << "]\n";
    } else {
        out << "  \"objective\": null,\n  \"mapping\": null,\n  \"supported_merge_ranks\": [],\n  \"minimum_cover_ranks\": []\n";
    }
    out << "}\n";
    return out.str();
}

} // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.self_test) { run_self_test(); return 0; }
        const Inputs inputs = load_inputs(options.registered, options.substrings, options.merge_tree);
        std::cerr << "INPUTS_OK primitives=" << inputs.primitives.size()
                  << " merges=" << inputs.merges.size()
                  << " train_substrings=" << inputs.registered.at("registered_train_substrings").at("distinct_substring_count").integer()
                  << " small_tasks=" << inputs.small_tasks.size()
                  << " literal_relevant=" << inputs.literal_relevant.size() << '\n';

        const std::vector<int> control_mapping = positional_mapping(inputs);
        const DirectEvaluation control = evaluate_direct(inputs, control_mapping, 20);
        const Json& negative = inputs.registered.at("negative_control");
        const int expected_support = negative.at("gdt615_train_only_raw_supported_merge_count").integer();
        const int expected_cover = negative.at("gdt615_train_only_expected_exact_minimum").integer();
        std::cerr << "NEGATIVE_CONTROL support=" << control.support << " cover=" << control.cover
                  << " expected=" << expected_support << '/' << expected_cover << '\n';
        if (control.support != expected_support || control.cover != expected_cover) {
            fail("positional negative-control reconstruction does not match registered expectation; explicit mapping is required");
        }

        SharedState shared;
        const auto started = std::chrono::steady_clock::now();
        if (!options.control_only) {
            const auto deadline = started + std::chrono::seconds(options.time_limit);
            std::vector<std::thread> workers;
            for (int worker = 0; worker < options.threads; ++worker) {
                workers.emplace_back([&]() {
                    TaskSearcher searcher(inputs, shared, deadline);
                    while (!shared.timeout.load(std::memory_order_relaxed)) {
                        const std::size_t task = shared.next_task.fetch_add(1, std::memory_order_relaxed);
                        if (task >= inputs.small_tasks.size()) break;
                        searcher.run(task);
                        shared.completed_tasks.fetch_add(1, std::memory_order_relaxed);
                    }
                });
            }
            for (auto& worker : workers) worker.join();
        }
        const bool complete = options.control_only ||
            (!shared.timeout.load() && shared.completed_tasks.load() == inputs.small_tasks.size());
        bool winner_direct_replay = true;
        if (!options.control_only) {
            Candidate winner;
            {
                std::lock_guard<std::mutex> lock(shared.best_mutex);
                winner = shared.best;
            }
            if (winner.valid) {
                const DirectEvaluation replay = evaluate_direct(inputs, winner.mapping_choices, kPaidBudget);
                winner_direct_replay = replay.support == winner.support &&
                    replay.cover == winner.cover && replay.support_mask == winner.support_mask &&
                    replay.cover_ranks == winner.cover_ranks;
                if (!winner_direct_replay) fail("direct winner replay disagrees with constraint-table search");
            }
        }
        const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
        const std::string result = render_result_json(
            inputs, shared, control, complete, options.control_only, winner_direct_replay, elapsed);
        if (!options.output.empty()) {
            fs::create_directories(options.output.parent_path());
            std::ofstream out(options.output, std::ios::binary | std::ios::trunc);
            if (!out) fail("cannot create output: " + options.output.string());
            out << result;
            if (!out) fail("cannot write output: " + options.output.string());
        }
        std::cout << result;
        return complete ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
