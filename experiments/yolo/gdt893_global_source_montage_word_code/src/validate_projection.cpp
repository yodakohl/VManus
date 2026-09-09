// Independent universal-projection proof by exact direct-map constraint search.
// Complete optimum family is implicit: fixed candidate constraints AND weight=W.
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using Clock=std::chrono::steady_clock;
using Pair=std::pair<int,int>;
struct Timeout{};
struct Candidate{int group,weight;std::vector<Pair> mapping;};
struct Domain{int weight;std::vector<int> choices;};
struct Query{std::string kind,status;int candidate=-1;Pair pair={-1,-1};std::vector<int> witness;};
std::vector<Candidate> candidates;
std::vector<int> forward_map,reverse_map,witness;
std::vector<Query> queries;
std::set<int> possible_candidates,forced_candidates;
std::set<Pair> possible_pairs,forced_pairs;
long long best=-1,nodes=0,checks=0;
Clock::time_point deadline;
void checkpoint(){if(Clock::now()>deadline)throw Timeout();}
bool compatible(int index){for(auto [c,p]:candidates[index].mapping)
 if((forward_map[c]>=0&&forward_map[c]!=p)||(reverse_map[p]>=0&&reverse_map[p]!=c))return false;return true;}
// In goal mode, the very first weight=goal witness terminates the search.
// Otherwise maximize exactly, pruning ties because only one witness is needed.
bool search(const std::vector<Domain>& domains,std::vector<int>& selected,long long weight,long long goal){
 ++nodes;if((nodes&255)==0)checkpoint();
 long long upper=weight;for(const auto& d:domains)if(!d.choices.empty())upper+=d.weight;
 if(goal>=0 ? upper<goal : upper<=best)return false;
 if(domains.empty()){
  if(goal>=0){if(weight==goal){witness=selected;std::sort(witness.begin(),witness.end());return true;}}
  else if(weight>best){best=weight;witness=selected;std::sort(witness.begin(),witness.end());}
  return false;
 }
 size_t chosen=0;for(size_t i=1;i<domains.size();++i)
  if(domains[i].choices.size()<domains[chosen].choices.size())chosen=i;
 std::vector<Domain> remaining;for(size_t i=0;i<domains.size();++i)if(i!=chosen)remaining.push_back(domains[i]);
 for(int index:domains[chosen].choices){
  if((++checks&4095)==0)checkpoint();
  std::vector<Pair> added;
  for(auto [c,p]:candidates[index].mapping)if(forward_map[c]<0){forward_map[c]=p;reverse_map[p]=c;added.push_back({c,p});}
  std::vector<Domain> filtered;
  for(const auto& d:remaining){Domain next{d.weight,{}};for(int other:d.choices){
    if((++checks&4095)==0)checkpoint();if(compatible(other))next.choices.push_back(other);}
   if(!next.choices.empty())filtered.push_back(std::move(next));}
  selected.push_back(index);bool found=search(filtered,selected,weight+candidates[index].weight,goal);selected.pop_back();
  for(auto [c,p]:added){forward_map[c]=-1;reverse_map[p]=-1;}
  if(found)return true;
 }
 return search(remaining,selected,weight,goal);
}
std::vector<Domain> domains_without(int banned,Pair pair){
 std::map<int,Domain> groups;
 for(size_t i=0;i<candidates.size();++i){
  if((++checks&4095)==0)checkpoint();
  if(int(i)==banned)continue;
  const auto& c=candidates[i];
  if(pair.first>=0&&std::find(c.mapping.begin(),c.mapping.end(),pair)!=c.mapping.end())continue;
  if(!groups.count(c.group))groups[c.group]=Domain{c.weight,{}};
  groups[c.group].choices.push_back(i);
 }
 std::vector<Domain> result;for(auto& item:groups)result.push_back(std::move(item.second));return result;
}
std::set<Pair> map_of(const std::vector<int>& solution){std::set<Pair> result;for(int i:solution)
 for(Pair pair:candidates[i].mapping)result.insert(pair);return result;}
void intersect_witness(const std::vector<int>& solution){
 std::set<int> ids(solution.begin(),solution.end());auto pairs=map_of(solution);
 for(auto it=possible_candidates.begin();it!=possible_candidates.end();)if(!ids.count(*it))it=possible_candidates.erase(it);else ++it;
 for(auto it=possible_pairs.begin();it!=possible_pairs.end();)if(!pairs.count(*it))it=possible_pairs.erase(it);else ++it;
}
void print_ids(std::ostream& out,const std::vector<int>& ids){out<<'[';for(size_t i=0;i<ids.size();++i){if(i)out<<',';out<<ids[i];}out<<']';}
int main(int argc,char** argv){
 bool max_complete=false,projection_complete=false;std::vector<int> initial;
 try{
  if(argc!=4)throw std::runtime_error("INPUT OUTPUT SECONDS required");
  deadline=Clock::now()+std::chrono::duration_cast<Clock::duration>(std::chrono::duration<double>(std::stod(argv[3])));
  std::ifstream in(argv[1]);int n;if(!(in>>n)||n<0)throw std::runtime_error("invalid count");
  int mc=0,mp=0;std::map<int,int> weights;
  for(int i=0;i<n;++i){if((i&4095)==0)checkpoint();Candidate c;int count;
   if(!(in>>c.group>>c.weight>>count)||c.group<0||c.weight<=0||count<0)throw std::runtime_error("invalid candidate");
   std::set<int> seen_c,seen_p;
   for(int j=0;j<count;++j){int a,b;if(!(in>>a>>b)||a<0||b<0||!seen_c.insert(a).second||!seen_p.insert(b).second)throw std::runtime_error("invalid bijection");
    c.mapping.push_back({a,b});mc=std::max(mc,a);mp=std::max(mp,b);}
   if(weights.count(c.group)&&weights[c.group]!=c.weight)throw std::runtime_error("paragraph weights differ");
   weights[c.group]=c.weight;candidates.push_back(std::move(c));
  }
  std::string extra;if(in>>extra)throw std::runtime_error("extra tokens");
  forward_map.assign(mc+1,-1);reverse_map.assign(mp+1,-1);
  auto all=domains_without(-1,{-1,-1});std::vector<int> selected;
  search(all,selected,0,-1);checkpoint();max_complete=true;initial=witness;
  possible_candidates=std::set<int>(initial.begin(),initial.end());possible_pairs=map_of(initial);
  while(true){
   auto it=std::find_if(possible_candidates.begin(),possible_candidates.end(),[](int i){return !forced_candidates.count(i);});
   if(it==possible_candidates.end())break;int index=*it;
   auto restricted=domains_without(index,{-1,-1});bool sat=search(restricted,selected,0,best);checkpoint();
   queries.push_back(Query{"candidate",sat?"SAT":"UNSAT",index,{-1,-1},sat?witness:std::vector<int>{}});
   if(sat)intersect_witness(witness);
   else{forced_candidates.insert(index);for(Pair p:candidates[index].mapping)forced_pairs.insert(p);}
  }
  while(true){
   auto it=std::find_if(possible_pairs.begin(),possible_pairs.end(),[](Pair p){return !forced_pairs.count(p);});
   if(it==possible_pairs.end())break;Pair pair=*it;
   auto restricted=domains_without(-1,pair);bool sat=search(restricted,selected,0,best);checkpoint();
   queries.push_back(Query{"pair",sat?"SAT":"UNSAT",-1,pair,sat?witness:std::vector<int>{}});
   if(sat)intersect_witness(witness);else forced_pairs.insert(pair);
  }
  projection_complete=true;
 }catch(const Timeout&){}
 catch(const std::bad_alloc&){}
 catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
 std::ofstream out(argv[2]);if(!out)return 1;
 out<<"{\"status\":\""<<(projection_complete?"COMPLETE":"UNKNOWN_BUDGET")<<"\",\"max_complete\":"<<(max_complete?"true":"false")
    <<",\"projection_complete\":"<<(projection_complete?"true":"false")<<",\"best_weight\":"<<best<<",\"witness\":";print_ids(out,initial);
 out<<",\"forced_candidates\":";print_ids(out,std::vector<int>(forced_candidates.begin(),forced_candidates.end()));
 out<<",\"forced_word_values\":[";bool first=true;for(auto [c,p]:forced_pairs){if(!first)out<<',';first=false;out<<"{\"cipher_word_id\":"<<c<<",\"source_word_id\":"<<p<<'}';}
 out<<"],\"queries\":[";for(size_t i=0;i<queries.size();++i){if(i)out<<',';const auto&q=queries[i];out<<"{\"kind\":\""<<q.kind<<"\",\"status\":\""<<q.status<<"\",\"candidate\":"<<q.candidate
 <<",\"pair\":["<<q.pair.first<<','<<q.pair.second<<"],\"witness\":";print_ids(out,q.witness);out<<'}';}
 out<<"],\"stats\":{\"nodes\":"<<nodes<<",\"candidate_checks\":"<<checks<<"},\"representation\":\"All optima are the implicit constraint family at proved maximum weight; no optimum count is claimed.\"}\n";
 return out?0:1;
}
