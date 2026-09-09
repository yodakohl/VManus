// Independent window oracle: explicit forward/reverse maps, no pattern hashing.
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <cstdint>
struct Record { std::string id; std::vector<int> words; };
std::vector<Record> read(const char* path) {
    std::ifstream in(path); int count;
    if (!(in >> count) || count < 0) throw std::runtime_error("invalid record count");
    std::vector<Record> records(count);
    for (auto& r : records) {
        int n; if (!(in >> r.id >> n) || n < 0) throw std::runtime_error("invalid record");
        r.words.resize(n);
        for (auto& x : r.words) if (!(in >> x) || x < 0) throw std::runtime_error("invalid word ID");
    }
    std::string extra; if (in >> extra) throw std::runtime_error("extra input tokens");
    return records;
}
int main(int argc, char** argv) {
    try {
        if (argc != 4) throw std::runtime_error("TARGET SOURCE OUTPUT required");
        auto targets=read(argv[1]), sources=read(argv[2]);
        int max_t=0,max_s=0;
        for (const auto& r:targets) for (int x:r.words) if(x>max_t) max_t=x;
        for (const auto& r:sources) for (int x:r.words) if(x>max_s) max_s=x;
        std::vector<int> forward(max_t+1),reverse(max_s+1);
        std::vector<uint64_t> ft(max_t+1,0),rt(max_s+1,0);
        uint64_t epoch=0,windows=0,matches=0;
        std::ofstream out(argv[3]); if(!out) throw std::runtime_error("output unavailable");
        out << "target_index,source_index,start,length\n";
        for(size_t ti=0;ti<targets.size();++ti) {
            const auto& t=targets[ti].words; if(t.empty()) continue;
            for(size_t si=0;si<sources.size();++si) {
                const auto& s=sources[si].words; if(s.size()<t.size()) continue;
                for(size_t start=0;start+t.size()<=s.size();++start) {
                    ++windows; ++epoch; bool ok=true;
                    for(size_t j=0;j<t.size();++j) {
                        int a=t[j],b=s[start+j];
                        if((ft[a]==epoch && forward[a]!=b)||(rt[b]==epoch && reverse[b]!=a)) {ok=false;break;}
                        ft[a]=epoch;forward[a]=b;rt[b]=epoch;reverse[b]=a;
                    }
                    if(ok){++matches;out<<ti<<','<<si<<','<<start<<','<<t.size()<<'\n';}
                }
            }
        }
        if(!out) throw std::runtime_error("output write failed");
        std::cout<<"{\"windows\":"<<windows<<",\"matches\":"<<matches<<"}\n";
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
