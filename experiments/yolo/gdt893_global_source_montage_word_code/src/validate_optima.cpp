// Independent exact optimizer: paragraph-domain enumeration and direct map joins.
// Does not construct or import the fitter's conflict graph or optimizer.
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using Clock = std::chrono::steady_clock;
struct Timeout {};
struct Candidate { int group,weight; std::vector<std::pair<int,int>> mapping; };
struct Domain { int weight; std::vector<int> choices; };
std::vector<Candidate> candidates;
std::vector<int> forward_map, reverse_map;
std::vector<std::vector<int>> solutions;
long long best=-1,nodes=0,checks=0;
Clock::time_point deadline;
void checkpoint(){if(Clock::now()>deadline)throw Timeout();}
bool compatible(int index){
    for(auto [c,p]:candidates[index].mapping)
        if((forward_map[c]>=0&&forward_map[c]!=p)||(reverse_map[p]>=0&&reverse_map[p]!=c))return false;
    return true;
}
void search(const std::vector<Domain>& domains,std::vector<int>& selected,long long weight){
    ++nodes;if((nodes&255)==0)checkpoint();
    long long upper=weight;for(const auto& d:domains)if(!d.choices.empty())upper+=d.weight;
    if(upper<best)return;
    if(domains.empty()){
        if(weight>best){best=weight;solutions.clear();}
        if(weight==best){auto solution=selected;std::sort(solution.begin(),solution.end());solutions.push_back(std::move(solution));}
        return;
    }
    size_t chosen=0;
    for(size_t d=1;d<domains.size();++d)if(domains[d].choices.size()<domains[chosen].choices.size())chosen=d;
    std::vector<Domain> remaining;
    for(size_t d=0;d<domains.size();++d)if(d!=chosen)remaining.push_back(domains[d]);
    for(int index:domains[chosen].choices){
        if((++checks&4095)==0)checkpoint();
        if(!compatible(index))throw std::runtime_error("domain contains incompatible candidate");
        std::vector<std::pair<int,int>> added;
        for(auto [c,p]:candidates[index].mapping)if(forward_map[c]<0){
            forward_map[c]=p;reverse_map[p]=c;added.push_back({c,p});
        }
        std::vector<Domain> filtered;
        for(const auto& d:remaining){
            Domain next{d.weight,{}};
            for(int other:d.choices){
                if((++checks&4095)==0)checkpoint();
                if(compatible(other))next.choices.push_back(other);
            }
            // An empty paragraph domain has only omission; eliminate that
            // deterministic choice rather than creating a spurious solution.
            if(!next.choices.empty())filtered.push_back(std::move(next));
        }
        selected.push_back(index);
        search(filtered,selected,weight+candidates[index].weight);
        selected.pop_back();
        for(auto [c,p]:added){forward_map[c]=-1;reverse_map[p]=-1;}
    }
    search(remaining,selected,weight); // Omission always remains a distinct option.
}
int main(int argc,char** argv){
    try{
        if(argc!=4)throw std::runtime_error("INPUT OUTPUT SECONDS required");
        double seconds=std::stod(argv[3]);deadline=Clock::now()+std::chrono::duration_cast<Clock::duration>(std::chrono::duration<double>(seconds));
        std::ifstream in(argv[1]);int n;if(!(in>>n)||n<0)throw std::runtime_error("invalid candidate count");
        int max_c=0,max_p=0;std::map<int,Domain> grouped;
        for(int index=0;index<n;++index){
            if((index&4095)==0)checkpoint();
            Candidate c;int count;if(!(in>>c.group>>c.weight>>count)||c.group<0||c.weight<=0||count<0)throw std::runtime_error("invalid candidate header");
            std::map<int,int> fm,rm;
            for(int j=0;j<count;++j){int a,b;if(!(in>>a>>b)||a<0||b<0)throw std::runtime_error("invalid pair");
                if(fm.count(a)||rm.count(b))throw std::runtime_error("noninjective or duplicate pair");
                fm[a]=b;rm[b]=a;c.mapping.push_back({a,b});max_c=std::max(max_c,a);max_p=std::max(max_p,b);
            }
            if(!grouped.count(c.group))grouped[c.group]=Domain{c.weight,{}};
            if(grouped[c.group].weight!=c.weight)throw std::runtime_error("paragraph weights differ");
            grouped[c.group].choices.push_back(index);candidates.push_back(std::move(c));
        }
        std::string extra;if(in>>extra)throw std::runtime_error("extra input tokens");
        forward_map.assign(max_c+1,-1);reverse_map.assign(max_p+1,-1);
        std::vector<Domain> domains;for(auto& item:grouped)domains.push_back(std::move(item.second));
        std::vector<int> selected;bool complete=true;
        try{search(domains,selected,0);checkpoint();}catch(const Timeout&){complete=false;}
        std::sort(solutions.begin(),solutions.end());
        std::ofstream out(argv[2]);if(!out)throw std::runtime_error("output unavailable");
        out<<"{\"status\":\""<<(complete?"COMPLETE":"UNKNOWN_BUDGET")<<"\",\"best_weight\":"<<best<<",\"optimal_solutions\":[";
        for(size_t i=0;i<solutions.size();++i){if(i)out<<',';out<<'[';for(size_t j=0;j<solutions[i].size();++j){if(j)out<<',';out<<solutions[i][j];}out<<']';}
        out<<"],\"stats\":{\"nodes\":"<<nodes<<",\"candidate_checks\":"<<checks<<"}}\n";
        if(!out)throw std::runtime_error("output write failed");
    }catch(const Timeout&){std::ofstream out(argv[2]);out<<"{\"status\":\"UNKNOWN_BUDGET\",\"stage\":\"INPUT\"}\n";}
    catch(const std::bad_alloc&){std::ofstream out(argv[2]);out<<"{\"status\":\"UNKNOWN_BUDGET\",\"stage\":\"MEMORY\"}\n";}
    catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
