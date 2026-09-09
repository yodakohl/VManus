#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <omp.h>

struct Row { uint32_t one=0, two=0; };
Row add(Row a, Row b, uint32_t all) {
    uint32_t za=all^(a.one|a.two), zb=all^(b.one|b.two);
    return {(za&b.one)|(a.one&zb)|(a.two&b.two),
            (za&b.two)|(a.two&zb)|(a.one&b.one)};
}
Row neg(Row a) { return {a.two,a.one}; }
Row coefficients(const std::vector<int>& word, uint32_t mask) {
    Row r;
    bool negative=false;
    for (auto it=word.rbegin(); it!=word.rend(); ++it) {
        uint32_t bit=1u<<*it;
        if (!negative) {
            if (r.one&bit) { r.one^=bit; r.two|=bit; }
            else if (r.two&bit) r.two^=bit;
            else r.one|=bit;
        } else {
            if (r.two&bit) { r.two^=bit; r.one|=bit; }
            else if (r.one&bit) r.one^=bit;
            else r.two|=bit;
        }
        negative ^= bool(mask&bit);
    }
    return r;
}
int rank_for(const std::vector<std::vector<int>>& words, uint32_t mask, int n) {
    Row reference=coefficients(words[0],mask);
    std::array<Row,24> basis{};
    uint32_t all=(1u<<n)-1;
    int rank=0;
    for (size_t k=1;k<words.size();++k) {
        Row row=add(coefficients(words[k],mask),neg(reference),all);
        while (row.one|row.two) {
            int pivot=__builtin_ctz(row.one|row.two);
            if (!(basis[pivot].one|basis[pivot].two)) {
                if (row.two&(1u<<pivot)) row=neg(row);
                basis[pivot]=row;
                ++rank;
                break;
            }
            row=add(row,(row.one&(1u<<pivot))?neg(basis[pivot]):basis[pivot],all);
        }
        if (rank==n) return n;
    }
    return rank;
}
int main(int argc,char**argv) {
    if (argc!=4) throw std::runtime_error("usage: enumerate input.tsv output.json ranks.bin");
    std::ifstream in(argv[1]);
    std::string line;
    std::getline(in,line);
    if (line!="locus\tliteral") throw std::runtime_error("header");
    std::vector<std::string> strings;
    std::set<char> alphabet_set;
    while (std::getline(in,line)) {
        auto tab=line.find('\t');
        if (tab==std::string::npos) throw std::runtime_error("input");
        std::string w=line.substr(tab+1);
        if (w.empty()) throw std::runtime_error("empty word");
        strings.push_back(w);
        alphabet_set.insert(w.begin(),w.end());
    }
    std::string alphabet(alphabet_set.begin(),alphabet_set.end());
    int n=alphabet.size();
    if (n<1||n>24||strings.empty()) throw std::runtime_error("scope");
    std::vector<std::vector<int>> words;
    for (const auto&w:strings) {
        std::vector<int> v;
        for(char c:w) v.push_back(alphabet.find(c));
        words.push_back(v);
    }
    // Exhaustively verify the field bit operations, independently of target ranks.
    for(int a=0;a<3;++a) for(int b=0;b<3;++b) {
        Row x{uint32_t(a==1),uint32_t(a==2)},y{uint32_t(b==1),uint32_t(b==2)};
        Row z=add(x,y,1);
        if(int(z.one)+2*int(z.two)!=(a+b)%3) throw std::runtime_error("field fixture");
    }
    uint32_t total=1u<<n;
    std::vector<unsigned char> ranks(total,255);
    auto start=std::chrono::steady_clock::now();
    #pragma omp parallel for schedule(dynamic,256) num_threads(16)
    for(uint32_t mask=0;mask<total;++mask) {
        double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        if(seconds<1200) ranks[mask]=rank_for(words,mask,n);
    }
    std::array<uint64_t,256> counts{};
    for(auto r:ranks) ++counts[r];
    std::ofstream binary(argv[3],std::ios::binary);
    binary.write(reinterpret_cast<const char*>(ranks.data()),ranks.size());
    std::ofstream out(argv[2]);
    out<<"{\"alphabet\":\""<<alphabet<<"\",\"total\":"<<total
       <<",\"unprocessed\":"<<counts[255]<<",\"rank_counts\":{";
    bool first=true;
    for(int r=0;r<256;++r) if(counts[r]) {
        if(!first) out<<",";
        first=false;
        out<<"\""<<r<<"\":"<<counts[r];
    }
    double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    out<<"},\"elapsed_seconds\":"<<seconds<<"}\n";
    std::cout<<"masks="<<total-counts[255]<<" full_rank="<<counts[n]<<" seconds="<<seconds<<"\n";
}
