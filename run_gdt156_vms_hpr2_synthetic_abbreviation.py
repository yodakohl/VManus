#!/usr/bin/env python3
"""Apply frozen VMS_HPR2_ABBR_V1 to GDT155 readable external controls."""
from __future__ import annotations
import csv,hashlib,json,math,statistics,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LINES=ROOT/'gdt155_unblinded_lines.tsv';META=ROOT/'gdt155_blinded_diplomatic.tsv';TRUTH=ROOT/'gdt155_unblinded_record_truth.tsv';G155=ROOT/'gdt155_unblind_calibration_result.json';G155SUM=ROOT/'gdt155_unblind_retrieval_summary.tsv';METHOD=ROOT/'GDT156_VMS_HPR2_SYNTHETIC_ABBREVIATION_METHOD.md'
GROUPS=ROOT/'gdt156_encoded_groups.tsv';ARCH=ROOT/'gdt156_encoded_architecture.tsv';RECOVERY=ROOT/'gdt156_word_recovery.tsv';RECT=ROOT/'gdt156_synthetic_rectangles.tsv';PROPS=ROOT/'gdt156_property_attribution.tsv';RETR=ROOT/'gdt156_retrieval.tsv';RSUM=ROOT/'gdt156_retrieval_summary.tsv';COMP=ROOT/'gdt156_comparison.tsv';REPORT=ROOT/'GDT156_VMS_HPR2_SYNTHETIC_ABBREVIATION_REPORT.md';RESULT=ROOT/'gdt156_result.json'
BOOKS=('Band2','Band3','Band4','Band5');VOWELS=set('aeiouyäöü');FOLD=str.maketrans({'ſ':'s','ı':'i','ȷ':'j','ẜ':'s'})
REC_REPS=('SYNTHETIC_TOKEN_IDENTITY','SYNTHETIC_CHAR3','PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','COMPILER_SIGNATURE','HOST_PLUS_COMPILER','MARKER_AND_POSITION','UNBLINDED_EXPANDED_CHAR3_REFERENCE')

def read(p):
    with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
    assert rows
    with p.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def norm(s):return ''.join(ch for ch in unicodedata.normalize('NFC',s).translate(FOLD).lower() if ch.isalnum())
def char3(s):s='^'+s+'$';return {s[i:i+3] for i in range(max(1,len(s)-2))}
def words(s):return {x for part in s.split() if (x:=norm(part)) and x!='none'}
def jac(a,b):return len(a&b)/len(a|b) if a or b else 0.
def lexemes(s):
    out=[];buf=''
    for ch in unicodedata.normalize('NFC',s):
        if ch.isalnum():buf+=ch
        else:
            if buf:out.append(('WORD',buf));buf=''
            if not ch.isspace():out.append(('PUNCT',ch))
    if buf:out.append(('WORD',buf))
    return out
def host(word):
    letters=[ch for ch in norm(word) if ch.isalpha()]
    if not letters:
        digits=norm(word);return (digits[:1]+digits[-1:]) or 'x'
    cons=[ch for ch in letters[1:] if ch not in VOWELS][:2]
    return letters[0]+''.join(cons)+letters[-1]
def right(n):return 'al' if n<=3 else 'ar' if n<=5 else 'ain' if n<=7 else 'aiin'

lines=read(LINES);meta={x['line_id']:x for x in read(META)};truth=read(TRUTH)
assert len(lines)==48347 and all(not any(v.lower().startswith('f84') for v in row.values()) for table in (lines,list(meta.values()),truth) for row in table)
byrec=defaultdict(list)
for row in lines:byrec[row['record_id']].append(row)
for vals in byrec.values():vals.sort(key=lambda r:int(meta[r['line_id']]['line_index']))
encoded=[];record_features={};pages={};record_book={};record_words={}
for record,vals in sorted(byrec.items()):
    book=vals[0]['book_or_ms'];record_book[record]=book;pages[record]={meta[x['line_id']]['page_id'] for x in vals}
    line_lex=[lexemes('' if x['expanded_diplomatic']=='EMPTY' else x['expanded_diplomatic']) for x in vals];total=sum(kind=='WORD' for lx in line_lex for kind,_ in lx);ordinal=0;seen=set();field_start=True;record_words[record]=[]
    features={rep:set() for rep in REC_REPS}
    for li,(row,lx) in enumerate(zip(vals,line_lex),1):
        word_positions=[i for i,(kind,_) in enumerate(lx) if kind=='WORD']
        for wi,pos in enumerate(word_positions,1):
            surface=lx[pos][1];expanded=norm(surface);ordinal+=1;h=host(surface);first_host=int(h not in seen)
            if first_host:frame='o' if ordinal<=math.ceil(total/2) else 'ot';seen.add(h)
            else:frame='NONE'
            outer='q' if ordinal==1 else 's' if wi==1 and li>1 else 'd' if field_start else 'NONE'
            between=lx[pos+1:(word_positions[wi] if wi<len(word_positions) else len(lx))]
            punct=''.join(value for kind,value in between if kind=='PUNCT');dy=int(any(ch in './;:?!' for ch in punct));m=int(ordinal==total);rf=right(len(expanded));closure=('dy' if dy else '')+('m' if m else '')
            token=('' if outer=='NONE' else outer)+('' if frame=='NONE' else frame)+h+rf+closure
            sig='|'.join((outer,frame,rf,str(dy),str(m)));lq=min(3,4*(li-1)//max(1,len(vals)));tq=min(3,4*(ordinal-1)//max(1,total))
            gid=f'{record}_G{ordinal:04d}';encoded.append({'group_id':gid,'corpus':row['corpus'],'book_or_ms':book,'record_id':record,'line_id':row['line_id'],'line_index':li,'group_index_in_line':wi,'group_index_in_record':ordinal,'expanded_source_group':surface,'normalized_expanded_group':expanded,'outer_wrapper':outer,'local_frame':frame,'page_host':h,'right_family':rf,'dy_closure':dy,'record_closure_m':m,'compiler_signature':sig,'synthetic_token':token,'property_source':'DETERMINISTIC_VMS_HPR2_ABBR_V1'})
            record_words[record].append(expanded)
            features['SYNTHETIC_TOKEN_IDENTITY'].add('W='+token);features['SYNTHETIC_CHAR3'].update('C='+x for x in char3(token));features['PAGE_HOST_IDENTITY'].add('H='+h);features['PAGE_HOST_CHAR3'].update('HC='+x for x in char3(h));features['COMPILER_SIGNATURE'].add('S='+sig);features['HOST_PLUS_COMPILER'].add('J='+h+'@'+sig);features['MARKER_AND_POSITION'].add(f'O={outer}|F={frame}|LQ={lq}|TQ={tq}');features['UNBLINDED_EXPANDED_CHAR3_REFERENCE'].update('EC='+x for x in char3(expanded))
            field_start=dy
    record_features[record]=features

# Architecture and compression.
arch=[]
for book in ('Ste1',)+BOOKS:
    rows=[x for x in encoded if x['book_or_ms']==book];chars=sum(len(x['synthetic_token']) for x in rows);source=sum(len(x['normalized_expanded_group']) for x in rows);hostchars=sum(len(x['page_host']) for x in rows);atoms=sum(len(x['page_host'])+(x['outer_wrapper']!='NONE')+(x['local_frame']!='NONE')+1+int(x['dy_closure'])+int(x['record_closure_m']) for x in rows)
    arch.append({'book_or_ms':book,'records':len({x['record_id'] for x in rows}),'groups':len(rows),'source_characters':source,'page_host_characters':hostchars,'page_host_per_source_character':f'{hostchars/max(1,source):.12g}','synthetic_codepoints':chars,'synthetic_codepoints_per_source_character':f'{chars/max(1,source):.12g}','synthetic_abstract_atoms':atoms,'synthetic_atoms_per_source_character':f'{atoms/max(1,source):.12g}','distinct_source_groups':len({x['normalized_expanded_group'] for x in rows}),'distinct_page_hosts':len({x['page_host'] for x in rows}),'distinct_synthetic_tokens':len({x['synthetic_token'] for x in rows}),'q_groups':sum(x['outer_wrapper']=='q' for x in rows),'s_groups':sum(x['outer_wrapper']=='s' for x in rows),'d_groups':sum(x['outer_wrapper']=='d' for x in rows),'dy_groups':sum(int(x['dy_closure']) for x in rows),'m_groups':sum(int(x['record_closure_m']) for x in rows)})

# Held-book recovery of known source groups from encoded layers.
recovery=[]
for held in BOOKS+('Ste1',):
    trainbooks=BOOKS if held=='Ste1' else tuple(x for x in BOOKS if x!=held);train=[x for x in encoded if x['book_or_ms'] in trainbooks];test=[x for x in encoded if x['book_or_ms']==held]
    specs={'GLOBAL_FREQUENCY':lambda x:'ALL','PAGE_HOST_IDENTITY':lambda x:x['page_host'],'COMPILER_SIGNATURE':lambda x:x['compiler_signature'],'PAGE_HOST_PLUS_RIGHT':lambda x:x['page_host']+'@'+x['right_family'],'HOST_PLUS_COMPILER':lambda x:x['page_host']+'@'+x['compiler_signature'],'SYNTHETIC_TOKEN_IDENTITY':lambda x:x['synthetic_token']}
    for rep,keyfn in specs.items():
        table=defaultdict(Counter)
        for x in train:table[keyfn(x)][x['normalized_expanded_group']]+=1
        ranked={key:tuple(v for v,_ in sorted(count.items(),key=lambda z:(-z[1],z[0]))[:3]) for key,count in table.items()};made=one=three=0
        for x in test:
            pred=ranked.get(keyfn(x),())
            if pred:made+=1;one+=pred[0]==x['normalized_expanded_group'];three+=x['normalized_expanded_group'] in pred
        recovery.append({'held_book_or_ms':held,'training_books':';'.join(trainbooks),'representation':rep,'test_groups':len(test),'predictions_made':made,'coverage':f'{made/max(1,len(test)):.12g}','top1_correct':one,'top1_accuracy':f'{one/max(1,made):.12g}','top3_correct':three,'top3_accuracy':f'{three/max(1,made):.12g}'})

# Predeclared wrapper x closure and wrapper x right-family rectangles.
vocab={x['synthetic_token'] for x in encoded if x['corpus']=='NUREMBERG'};rectangle=[]
for left in ('q','d','s','o','ot'):
    for rgt in ('dy','m'):
        complete=partial3=0;hosts=[]
        for base in sorted(vocab):
            if base.startswith(left) or base.endswith(rgt):continue
            cells=(base,left+base,base+rgt,left+base+rgt);n=sum(c in vocab for c in cells)
            if n==4:complete+=1;hosts.append(base)
            elif n==3:partial3+=1
        rectangle.append({'test_family':'EXACT_EDGE_RECTANGLE','left_operation':left,'right_operation':rgt,'completion_requirement':'4_OF_4','complete_hosts':complete,'partial_hosts':partial3,'example_complete_hosts':';'.join(hosts[:5]) or 'NONE','attribution':'MIXED_IMPOSED_OPERATOR_PLUS_EMERGENT_HOST_REUSE'})
for left in ('q','d','s','o','ot'):
    masks=defaultdict(set)
    for x in encoded:
        wrapper=(('' if x['outer_wrapper']=='NONE' else x['outer_wrapper'])+('' if x['local_frame']=='NONE' else x['local_frame']))
        if wrapper in ('',left):masks[x['page_host']].add((wrapper or 'BARE',x['right_family']))
    complete=sum(all((w,r) in cells for w in ('BARE',left) for r in ('al','ar','ain','aiin')) for cells in masks.values())
    rectangle.append({'test_family':'WRAPPER_BY_RIGHT_FAMILY_COMPATIBILITY','left_operation':left,'right_operation':'AL_AR_AIN_AIIN','completion_requirement':'8_OF_8','complete_hosts':complete,'partial_hosts':'NOT_APPLICABLE','example_complete_hosts':'NONE','attribution':'MIXED_IMPOSED_OPERATOR_PLUS_EMERGENT_HOST_REUSE'})

# Full-pool retrieval against known record truth.
trows={x['record_id']:x for x in truth if x['corpus']=='NUREMBERG'};tsets={r:{'CONTENT':words(x['regularized_content']),'ADDRESSEE':words(x['regularized_addressee'])} for r,x in trows.items()};retr=[];agg=defaultdict(lambda:{'n':0,'rr':0.,'one':0,'ten':0,'dec':0,'nr':[]})
for book in BOOKS:
    records=sorted(r for r in trows if record_book[r]==book)
    for query in records:
        candidates=[c for c in records if c!=query and not(pages[query]&pages[c])];ranks={}
        for rep in REC_REPS:ranks[rep]={c:i for i,c in enumerate(sorted(candidates,key=lambda c:(-jac(record_features[query][rep],record_features[c][rep]),c)),1)}
        for dim in ('CONTENT','ADDRESSEE'):
            if not tsets[query][dim]:continue
            scores=[(jac(tsets[query][dim],tsets[c][dim]),c) for c in candidates if tsets[c][dim]]
            if not scores:continue
            best,target=max(scores,key=lambda z:(z[0],-int(z[1].split('R')[-1])))
            if best<=0:continue
            for rep in REC_REPS:
                rank=ranks[rep][target];pool=len(candidates);dec=max(1,math.ceil(pool/10));retr.append({'book':book,'query_record':query,'truth_dimension':dim,'truth_target_record':target,'truth_set_jaccard':f'{best:.12g}','representation':rep,'candidate_pool':pool,'model_rank':rank,'reciprocal_rank':f'{1/rank:.12g}','top1':int(rank==1),'top10':int(rank<=10),'top_decile':int(rank<=dec),'normalized_rank':f'{rank/pool:.12g}'})
                for key in ((book,dim,rep),('ALL',dim,rep)):
                    z=agg[key];z['n']+=1;z['rr']+=1/rank;z['one']+=rank==1;z['ten']+=rank<=10;z['dec']+=rank<=dec;z['nr'].append(rank/pool)
rsum=[]
for (book,dim,rep),z in sorted(agg.items()):
    n=z['n'];rsum.append({'book':book,'truth_dimension':dim,'representation':rep,'queries':n,'mean_reciprocal_rank':f'{z["rr"]/n:.12g}','top1':z['one'],'top1_rate':f'{z["one"]/n:.12g}','top10':z['ten'],'top10_rate':f'{z["ten"]/n:.12g}','top_decile':z['dec'],'top_decile_rate':f'{z["dec"]/n:.12g}','median_normalized_rank':f'{statistics.median(z["nr"]):.12g}'})

properties=[
 {'property':'OUTER_WRAPPER_RECORD_LINE_FIELD_POSITION','attribution':'IMPOSED_BY_ENCODER','measurement':'q/s/d precedence and positions','interpretation':'NOT_EVIDENCE'},
 {'property':'O_OT_FIRST_PAGE_HOST_MENTION','attribution':'IMPOSED_BY_ENCODER','measurement':'first host occurrence split by record midpoint','interpretation':'NOT_EVIDENCE'},
 {'property':'RIGHT_FAMILY_LENGTH_CLASS','attribution':'IMPOSED_BY_ENCODER','measurement':'al/ar/ain/aiin by source length','interpretation':'NOT_EVIDENCE'},
 {'property':'DY_PUNCTUATION_FIELD_CLOSURE','attribution':'IMPOSED_BY_ENCODER','measurement':'dy at frozen punctuation boundaries','interpretation':'NOT_EVIDENCE'},
 {'property':'M_RECORD_CLOSURE','attribution':'IMPOSED_BY_ENCODER','measurement':'m on final group','interpretation':'NOT_EVIDENCE'},
 {'property':'PAGE_HOST_RECURRENCE_AND_COLLISION','attribution':'EMERGENT_AFTER_ENCODING','measurement':'source-dependent repeated lossy projections','interpretation':'CALIBRATION_SIGNAL'},
 {'property':'EXACT_OPERATOR_RECTANGLES','attribution':'MIXED_IMPOSED_OPERATOR_PLUS_EMERGENT_HOST_REUSE','measurement':'fixed operators need repeated compatible hosts','interpretation':'CALIBRATION_SIGNAL'},
 {'property':'KNOWN_CONTENT_RETRIEVAL','attribution':'EMERGENT_AFTER_ENCODING','measurement':'same-book non-co-page known-content target ranks','interpretation':'CALIBRATION_SIGNAL'},
 {'property':'LITERAL_AND_ATOM_COMPRESSION','attribution':'EMERGENT_FAILURE_OF_ENCODER_DESIGN','measurement':'full V1 exceeds expanded source length despite PAGE_HOST shortening','interpretation':'V1_IS_STRUCTURAL_CODE_NOT_EFFICIENT_ABBREVIATION'},
]

write(GROUPS,encoded);write(ARCH,arch);write(RECOVERY,recovery);write(RECT,rectangle);write(PROPS,properties);write(RETR,retr);write(RSUM,rsum)
g155=read(G155SUM)
def rr(rows,rep,dim='CONTENT'):return next(float(x['mean_reciprocal_rank']) for x in rows if x['book']=='ALL' and x['truth_dimension']==dim and x['representation']==rep)
comparison=[]
for label,oldrep,newrep in [('RAW_OR_COMPLETE_TOKEN','RAW_CHAR3','SYNTHETIC_CHAR3'),('PAGE_HOST','PAGE_HOST_CHAR3','PAGE_HOST_CHAR3'),('COMPILER','COMPILER_SIGNATURE','COMPILER_SIGNATURE')]:
    old=rr(g155,oldrep);new=rr(rsum,newrep);comparison.append({'endpoint':'KNOWN_CONTENT_RETRIEVAL_MRR','layer':label,'diplomatic_control':f'{old:.12g}','synthetic_encoder':f'{new:.12g}','synthetic_minus_diplomatic':f'{new-old:.12g}','comparison_scope':'SAME_3172_MECHANICAL_TRUTH_QUERIES'})
oracle=rr(rsum,'UNBLINDED_EXPANDED_CHAR3_REFERENCE');comparison.append({'endpoint':'KNOWN_CONTENT_RETRIEVAL_MRR','layer':'UNBLINDED_EXPANDED_REFERENCE','diplomatic_control':'NOT_APPLICABLE','synthetic_encoder':f'{oracle:.12g}','synthetic_minus_diplomatic':'NOT_APPLICABLE','comparison_scope':'UPPER_REFERENCE_NOT_ENCODED_PREDICTOR'})
write(COMP,comparison)

def allrow(rep,dim='CONTENT'):return next(x for x in rsum if x['book']=='ALL' and x['truth_dimension']==dim and x['representation']==rep)
syn=allrow('SYNTHETIC_CHAR3');hrow=allrow('PAGE_HOST_CHAR3');crow=allrow('COMPILER_SIGNATURE');oracle_row=allrow('UNBLINDED_EXPANDED_CHAR3_REFERENCE')
nbarch=[x for x in arch if x['book_or_ms']!='Ste1'];src_total=sum(int(x['source_characters']) for x in nbarch);code_total=sum(int(x['synthetic_codepoints']) for x in nbarch);atom_total=sum(int(x['synthetic_abstract_atoms']) for x in nbarch);host_total=sum(int(x['page_host_characters']) for x in nbarch)
result={'schema':'GDT156_VMS_HPR2_SYNTHETIC_ABBREVIATION_RESULT_V1','status':'SYNTHETIC_HPR2_CONTROL_COMPLETE','encoder':'VMS_HPR2_ABBR_V1','freeze_provenance':{'published_in_commit':'d62de97','method_before_gdt155_unblind_scoring':True},'counts':{'records':len(byrec),'groups':len(encoded),'nuremberg_groups':sum(x['corpus']=='NUREMBERG' for x in encoded),'ste1_groups':sum(x['corpus']=='STE1' for x in encoded),'retrieval_rows':len(retr)},'compression':{'nuremberg_source_characters':src_total,'page_host_ratio':f'{host_total/src_total:.12g}','literal_codepoint_ratio':f'{code_total/src_total:.12g}','abstract_atom_ratio':f'{atom_total/src_total:.12g}','verdict':'PAGE_HOST_COMPRESSES_BUT_FULL_V1_EXPANDS'},'content_retrieval':{'synthetic_char3':syn,'page_host_char3':hrow,'compiler':crow,'expanded_reference':oracle_row},'interpretation':'The fixed encoder is sufficient to manufacture wrapper/frame/right/closure architecture and mixed operator rectangles; only recurrence and retrieval effects depend on source content. V1 is not an efficient physical abbreviation because compiler overhead exceeds PAGE_HOST shortening.','claim_ceiling':'Constructive external positive control only; no Voynich word, morpheme, sound, part of speech, language, plaintext, meaning, or translation.','f84':{'voynich_inputs':0,'accessed':False},'inputs':{p.name:sha(p) for p in (LINES,META,TRUTH,G155,G155SUM)},'documents':{METHOD.name:sha(METHOD)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (GROUPS,ARCH,RECOVERY,RECT,PROPS,RETR,RSUM,COMP)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
rawrec=next(x for x in recovery if x['held_book_or_ms']=='Band2' and x['representation']=='SYNTHETIC_TOKEN_IDENTITY')
REPORT.write_text(f'''# GDT156 — synthetic Voynich-style abbreviation control

## Outcome

**SYNTHETIC_HPR2_CONTROL_COMPLETE**

The encoder emitted {len(encoded):,} groups from {len(byrec):,} readable
external records.  Every `q/d/s`, `o/ot`, right-family, `dy`, and `m` placement
is imposed by the frozen compiler and is therefore not evidence.  PAGE_HOST
recurrence, collisions, compatible rectangles, and record-retrieval quality
remain source-dependent measurements.

On the full known-content retrieval target, synthetic-token character MRR is
{float(syn['mean_reciprocal_rank']):.4f}, PAGE_HOST-character MRR is
{float(hrow['mean_reciprocal_rank']):.4f}, compiler-only MRR is
{float(crow['mean_reciprocal_rank']):.4f}, and the unencoded expanded-character
reference is {float(oracle_row['mean_reciprocal_rank']):.4f}.  The comparison
table puts these beside the diplomatic control on the same mechanical truth
queries.

The constructive result is strong but narrow: a compact position/first-mention/
length/closure compiler can make ordinary medieval text look highly regular,
factorized, line-aware, and rectangle-rich.  Those imposed signatures cannot
be used as independent evidence for a Voynich interpretation.  The remaining
high-value signals are effects not guaranteed by the compiler: repeated-host
distribution, cross-record retrieval, and any held association with external
content that exceeds both raw-string and synthetic-control benchmarks.

This first invented encoder is not an efficient physical abbreviation:
PAGE_HOST alone uses {float(result['compression']['page_host_ratio']):.3f}
characters per source character, but the complete readable token uses
{float(result['compression']['literal_codepoint_ratio']):.3f} codepoints, or
{float(result['compression']['abstract_atom_ratio']):.3f} units even when each
multiletter compiler marker is counted as one abstract glyph.  Its value is as
a structural generative control, not as a claim about scribal economy.

No Voynich corpus or image was loaded, and no f84 material was accessed.
''',encoding='utf-8')
print(json.dumps({'status':result['status'],'groups':len(encoded),'synthetic_content_mrr':syn['mean_reciprocal_rank'],'host_content_mrr':hrow['mean_reciprocal_rank'],'expanded_reference_mrr':oracle_row['mean_reciprocal_rank']},sort_keys=True))
