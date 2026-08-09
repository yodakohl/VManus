#!/usr/bin/env python3
"""Refine the six favored family adjacencies into exact member-code pairs."""

from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL=RESULTS/"source_native_within_group_stage_masked.tsv";GROUPS=RESULTS/"source_sta_family_consensus_groups.tsv";FAMILY_ATLAS=RESULTS/"source_native_transition_atlas.tsv";FAMILY_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";RULES=BASE.parent.parent/"transcription"/"sources"/"sta"/"STA-Eva_def.bit";SPEC=BASE/"SOURCE_NATIVE_FAVORED_MEMBER_TRANSITION_SPEC.md";BUILDER=Path(__file__).resolve();OUT_TSV=RESULTS/"source_native_favored_member_transition_atlas.tsv";OUT_JSON=RESULTS/"source_native_favored_member_transition_atlas.json";OUT_REPORT=RESULTS/"source_native_favored_member_transition_atlas_report.md"
FROZEN={PANEL:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",GROUPS:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",FAMILY_ATLAS:"f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",FAMILY_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",RULES:"7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",SPEC:"8a996243bd31a69608494877115c68ea55dc3e804f44c2671d2e395ebb7c1481"};SHELLS=("AQ","DA","KJ","LJ","PK","QK");CAPACITY={"AQ":(6567,6361,94,1695,4666),"DA":(3535,3519,93,677,2842),"KJ":(2570,2565,92,450,2115),"LJ":(1282,1151,81,175,976),"PK":(547,534,78,119,415),"QK":(2834,2746,94,815,1931)}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inventory():
 codes=defaultdict(list);examples={}
 for raw in RULES.read_text().splitlines():
  line=raw.strip();parts=line.split(None,1)
  if line and not line.startswith('#') and len(parts)==2 and re.fullmatch(r'[A-Z][0-9A-Za-z]',parts[0]):codes[parts[0][0]].append(parts[0]);examples[parts[0]]=parts[1].strip()
 return dict(codes),examples
def folio(page):
 match=re.fullmatch(r'(f\d+)[rv]\d*',page)
 if match is None:raise ValueError('page')
 return match.group(1)
def load_events(codes):
 with PANEL.open(encoding='utf-8',newline='') as handle:panel=list(csv.DictReader(handle,delimiter='\t'))
 with GROUPS.open(encoding='utf-8',newline='') as handle:groups=list(csv.DictReader(handle,delimiter='\t'))
 eligible=[row for row in groups if row['strict_zero_alternative']=='1' and row['grammar_scope']=='CONFIRMED_PROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page'])]
 if len(panel)!=21899 or len(eligible)!=21899 or {row['unit_id'] for row in panel}!={row['consensus_group_id'] for row in eligible}:raise ValueError('scope')
 all_counts=Counter();exact_counts=Counter();exact_folios=defaultdict(set);exact_currier=Counter();events=[]
 for row in eligible:
  families=row['family_surface'];zl=row['zl_sta_codes'].split();it=row['it_sta_codes'].split();rf=row['rf_sta_codes'].split()
  if not len(families)==len(zl)==len(it)==len(rf)==int(row['symbol_count']):raise ValueError('geometry')
  held=folio(row['page'])
  for position in range(1,len(families)):
   shell=families[position-1:position+1]
   if shell not in SHELLS:continue
   all_counts[shell]+=1
   if not (zl[position-1]==it[position-1]==rf[position-1] and zl[position]==it[position]==rf[position]):continue
   left,right=zl[position-1],zl[position]
   if left not in codes[shell[0]] or right not in codes[shell[1]]:raise ValueError('member family')
   exact_counts[shell]+=1;exact_folios[shell].add(held);exact_currier[shell,row['currier']]+=1;events.append({'shell':shell,'folio':held,'currier':row['currier'],'length':len(families),'position':position,'left':left,'right':right})
 observed={shell:(all_counts[shell],exact_counts[shell],len(exact_folios[shell]),exact_currier[shell,'A'],exact_currier[shell,'B']) for shell in SHELLS}
 if observed!=CAPACITY or len(events)!=16876:raise ValueError('capacity')
 return events
def orientation_metrics(events,codes,reverse):
 folios=sorted({event['folio'] for event in events},key=lambda value:int(value[1:]));total=Counter();held=Counter();oriented=[]
 for event in events:
  if reverse:context=event['right'];current=event['left'];position=event['length']-event['position'];destination=event['shell'][0]
  else:context=event['left'];current=event['right'];position=event['position'];destination=event['shell'][1]
  key=(event['shell'],event['currier'],event['length'],position,current);total[key]+=1;held[(event['folio'],*key)]+=1;oriented.append((event,context,current,position,destination))
 observed=Counter();expected=defaultdict(float);opportunities=Counter();fobserved=Counter();fexpected=defaultdict(float);fopportunities=Counter();cobserved=Counter();cexpected=defaultdict(float);copportunities=Counter()
 for event,context,current,position,destination in oriented:
  vocabulary=codes[destination];counts=[total[(event['shell'],event['currier'],event['length'],position,value)]-held[(event['folio'],event['shell'],event['currier'],event['length'],position,value)] for value in vocabulary];denominator=sum(counts)+.5*len(vocabulary);probabilities={value:(count+.5)/denominator for value,count in zip(vocabulary,counts)}
  physical=(event['shell'],event['left'],event['right']);observed[physical]+=1;opportunities[(event['shell'],context)]+=1;fobserved[event['folio'],physical]+=1;fopportunities[event['folio'],event['shell'],context]+=1;cobserved[event['currier'],physical]+=1;copportunities[event['currier'],event['shell'],context]+=1
  for candidate,probability in probabilities.items():
   pair=(event['shell'],candidate,context) if reverse else (event['shell'],context,candidate);expected[pair]+=probability;fexpected[event['folio'],pair]+=probability;cexpected[event['currier'],pair]+=probability
 output={}
 for shell in SHELLS:
  for left in codes[shell[0]]:
   for right in codes[shell[1]]:
    pair=(shell,left,right);context=right if reverse else left;eligible=[held_folio for held_folio in folios if fopportunities[held_folio,shell,context]>=3];residual=[fobserved[held_folio,pair]-fexpected[held_folio,pair] for held_folio in eligible];positive=sum(value>0 for value in residual);negative=sum(value<0 for value in residual);number=len(eligible);record={'observed':observed[pair],'expected':expected[pair],'opportunities':opportunities[shell,context],'log_observed_expected':math.log((observed[pair]+.5)/(expected[pair]+.5)),'eligible_folios':number,'positive_folios':positive,'negative_folios':negative,'zero_folios':number-positive-negative,'positive_fraction':positive/number if number else 0.,'negative_fraction':negative/number if number else 0.}
    for currier in 'AB':record[f'currier_{currier}_observed']=cobserved[currier,pair];record[f'currier_{currier}_expected']=cexpected[currier,pair];record[f'currier_{currier}_opportunities']=copportunities[currier,shell,context];record[f'currier_{currier}_log_observed_expected']=math.log((cobserved[currier,pair]+.5)/(cexpected[currier,pair]+.5))
    output[pair]=record
 return output
def favored(record):return record['observed']>=20 and record['expected']>=5 and record['log_observed_expected']>=math.log(2) and record['eligible_folios']>=10 and record['positive_fraction']>=.70 and all(record[f'currier_{currier}_opportunities']>=15 and record[f'currier_{currier}_expected']>=2 and record[f'currier_{currier}_log_observed_expected']>=math.log(1.2) for currier in 'AB')
def disfavored(record):return record['expected']>=15 and record['log_observed_expected']<=-math.log(2) and record['eligible_folios']>=10 and record['negative_fraction']>=.70 and all(record[f'currier_{currier}_opportunities']>=15 and record[f'currier_{currier}_expected']>=5 and record[f'currier_{currier}_log_observed_expected']<=-math.log(1.2) for currier in 'AB')
def main():
 if any(path.exists() for path in (OUT_TSV,OUT_JSON,OUT_REPORT)):raise SystemExit('refusing overwrite')
 for path,expected in FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen input mismatch: {path.name}')
 if json.loads(FAMILY_VALIDATION.read_text())['favored_pairs']!=['PK','LJ','KJ','QK','AQ','DA']:raise SystemExit('family atlas drift')
 codes,examples=inventory();events=load_events(codes);forward=orientation_metrics(events,codes,False);backward=orientation_metrics(events,codes,True);rows=[]
 for shell in SHELLS:
  for left in codes[shell[0]]:
   for right in codes[shell[1]]:
    pair=(shell,left,right);first=forward[pair];second=backward[pair]
    if first['observed']!=second['observed']:raise ValueError('physical count')
    label='FAVORED_MEMBER_PAIR' if favored(first) and favored(second) else ('DISFAVORED_MEMBER_PAIR' if disfavored(first) and disfavored(second) else 'UNRESOLVED')
    row={'pair_id':left+'>'+right,'family_shell':shell,'left_member':left,'right_member':right,'left_official_example':examples[left],'right_official_example':examples[right],'observed_physical_count':first['observed'],'structural_label':label}
    for prefix,record in (('forward',first),('reversed',second)):
     for field,value in record.items():row[f'{prefix}_{field}']=value
    rows.append(row)
 with OUT_TSV.open('w',encoding='utf-8',newline='') as handle:writer=csv.DictWriter(handle,fieldnames=tuple(rows[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
 labels=Counter(row['structural_label'] for row in rows);favored_rows=sorted((row for row in rows if row['structural_label']=='FAVORED_MEMBER_PAIR'),key=lambda row:(-min(row['forward_log_observed_expected'],row['reversed_log_observed_expected']),row['pair_id']));disfavored_rows=sorted((row for row in rows if row['structural_label']=='DISFAVORED_MEMBER_PAIR'),key=lambda row:(max(row['forward_log_observed_expected'],row['reversed_log_observed_expected']),row['pair_id']))
 compact=lambda row:{'pair_id':row['pair_id'],'family_shell':row['family_shell'],'examples':row['left_official_example']+' > '+row['right_official_example'],'observed':row['observed_physical_count'],'forward_log_observed_expected':row['forward_log_observed_expected'],'reversed_log_observed_expected':row['reversed_log_observed_expected'],'forward_positive_fraction':row['forward_positive_fraction'],'reversed_positive_fraction':row['reversed_positive_fraction']}
 result={'experiment':'SOURCE_NATIVE_FAVORED_MEMBER_TRANSITION_ATLAS','status':'PASS_DESCRIPTIVE_EXACT_MEMBER_REFINEMENT','inputs':{path.name:sha(path) for path in (*FROZEN,BUILDER)},'counts':{'favored_family_shells':len(SHELLS),'all_shell_occurrences':17335,'exact_all_three_member_occurrences':len(events),'excluded_member_disagreements':17335-len(events),'official_candidate_member_pairs':len(rows),'labels':dict(sorted(labels.items()))},'capacity':{shell:{'all_events':values[0],'exact_events':values[1],'folios':values[2],'currier_A':values[3],'currier_B':values[4]} for shell,values in CAPACITY.items()},'strongest_favored':[compact(row) for row in favored_rows[:24]],'strongest_disfavored':[compact(row) for row in disfavored_rows[:24]],'tsv_sha256':sha(OUT_TSV),'english_glosses':0,'claim_ceiling':'Descriptive all-three-reading exact-member refinement inside six already confirmed neutral family adjacencies. Labels are not sounds, letters, syllables, morphemes, words, syntax, language, cipher operations, meanings, plaintext, or translation.'};OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');favored_text=', '.join(row['pair_id'] for row in favored_rows[:16]) or 'none';disfavored_text=', '.join(row['pair_id'] for row in disfavored_rows[:16]) or 'none';OUT_REPORT.write_text(f"""# Exact-member refinement of favored family transitions

Status: **{result['status']}**

The six frozen family shells contain **17,335** occurrences; **{len(events):,}**
retain exact adjacent member codes in all three readings. Of **{len(rows)}**
official within-shell member pairs, the frozen two-orientation rules classify
**{labels['FAVORED_MEMBER_PAIR']}** as favored and
**{labels['DISFAVORED_MEMBER_PAIR']}** as disfavored. Strongest favored:
{favored_text}. Strongest disfavored: {disfavored_text}.

Every label is conditional on its already favored family shell, Currier,
complete length, exact position, held folio, and the opposite orientation. The
readings provide a confidence filter, not replications. This is a descriptive
decomposition, not hundreds of new tests, and supplies no sound, letter,
syllable, morpheme, word, syntax, language, cipher operation, meaning,
plaintext, or translation.
""");print(json.dumps({'status':result['status'],'counts':result['counts'],'favored':favored_text,'disfavored':disfavored_text},sort_keys=True))
if __name__=='__main__':main()
