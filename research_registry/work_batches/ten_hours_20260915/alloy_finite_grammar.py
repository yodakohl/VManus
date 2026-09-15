#!/usr/bin/env python3
"""Source-only finite alloy-account examples and exact semantic checks.
No target data, target renderer, code search, or digit-permutation search.
"""
from fractions import Fraction as F
from pathlib import Path
import copy
import hashlib
import json

D = Path(__file__).resolve().parent
def N(s): return ["num", str(s)]
def W(value, spelling): return ["word_number", value, spelling]
def MX(whole, numerator, denominator): return ["mixed", N(whole), N(numerator), N(denominator)]
def X(op, *args): return [op, *args]
def Q(i): return ["qref", i]
def R(i): return ["rref", i]
def portion(kind, q): return ["portion", kind, q]
def mix(a,b): return ["mix",a,b]
def scale(q,r): return ["scale",q,r]
def row(i, page, layer, left, right, location, note=""):
    return {"id":i,"printed_page":page,"layer":layer,"left":left,"right":right,
            "location":location,"qualification":note}

EQS = [
row("E01",153,"PRINTED_ACTION",X("add",N(3),N(4)),N(7),"adde 3 cum 4, erunt 7"),
row("E02",153,"PRINTED_ACTION",X("div",N(7),N(2)),MX(3,1,2),"divide 7 per 2; mixed 3 and 1/2"),
row("E03",153,"NORMALIZATION_CLAIM",X("mul",MX(3,1,2),N(2)),N(7),"Vel integris: 7,12,10","Factor 2 is inferred from displayed common denominator, not a newly printed factor occurrence."),
row("E04",153,"NORMALIZATION_CLAIM",X("mul",N(6),N(2)),N(12),"Vel integris: 7,12,10","Same normalization qualification."),
row("E05",153,"NORMALIZATION_CLAIM",X("mul",N(5),N(2)),N(10),"Vel integris: 7,12,10","Same normalization qualification."),
row("E06",153,"PRINTED_ACTION",X("sub",N(10),N(7)),N(3),"difference from 7 to 10, namely 3"),
row("E07",153,"PRINTED_ACTION",X("sub",N(12),N(10)),N(2),"difference from 10 to 12, namely 2"),
row("E08",153,"LEXICAL_NUMBER_ACTION",X("div",N(2),W(2,"duo equa")),N(1),"divide 2 into duo equa; libra 1"),
row("E09",153,"PRINTED_ACCOUNT",X("add",N(1),N(1),N(3)),N(5),"summa libre 5; first marginal weight row"),
row("E10",153,"PRINTED_ACCOUNT",X("add",X("mul",N(1),N(3)),X("mul",N(1),N(4)),X("mul",N(3),N(6))),N(25),"sunt uncie 25 argenti","Products are semantic expansion of the written component weights and grades."),
row("E11",153,"COMMON_GRADE_CLAIM",X("div",N(25),N(5)),N(5),"target ad5 and ut oportet"),
row("P01",153,"PRINTED_ACCOUNT",X("add",N(2),N(5)),N(7),"sum of component pounds, scilicet per7"),
row("P02",153,"PRINTED_ACCOUNT",X("add",X("mul",N(2),N(3)),X("mul",N(5),N(4))),N(26),"uncias argenti ... scilicet26"),
row("P03",153,"PRINTED_ACTION",X("div",N(26),N(7)),MX(3,5,7),"result printed mixed 3 and 5/7"),
row("P04",153,"NORMALIZATION_CLAIM",X("mul",MX(3,5,7),N(7)),N(26),"hoc est:26,42,35","Factor7 inferred from displayed common denominator; no extra written numeral occurrence."),
row("P05",153,"NORMALIZATION_CLAIM",X("mul",N(6),N(7)),N(42),"hoc est:26,42,35","Same normalization qualification."),
row("P06",153,"NORMALIZATION_CLAIM",X("mul",N(5),N(7)),N(35),"hoc est:26,42,35","Same normalization qualification."),
row("P07",153,"PRINTED_ACTION",X("sub",N(35),N(26)),N(9),"difference26 to35 is9"),
row("P08",153,"PRINTED_ACTION",X("sub",N(42),N(35)),N(7),"difference35 to42 is7"),
row("P09",153,"PRINTED_ACTION",X("mul",X("div",N(5),N(7)),N(7)),N(5),"5/7 of previous7, namely5 pounds"),
row("P10",153,"PRINTED_ACTION",X("mul",X("div",N(2),N(7)),N(7)),N(2),"2/7 of same7, namely2 pounds"),
row("P11",153,"PRINTED_ACCOUNT",X("add",N(2),N(5),N(9)),N(16),"summa libra16"),
row("P12",153,"PRINTED_ACCOUNT",X("add",X("mul",N(2),N(3)),X("mul",N(5),N(4)),X("mul",N(9),N(6))),N(80),"sunt uncie argenti80"),
row("P13",153,"PRINTED_GRADE_ACTION",X("div",N(80),N(16)),N(5),"each pound receives ounces5"),
row("S01",153,"PRINTED_ACTION",X("div",X("mul",N(20),N(2)),N(16)),MX(2,1,2),"20 times2 divided16: mixed2 and1/2"),
row("S02",153,"PRINTED_ACTION",X("div",X("mul",N(20),N(5)),N(16)),MX(6,1,4),"20 times5 divided16: mixed6 and1/4"),
row("S03",153,"PRINTED_ACTION",X("sub",X("sub",N(20),MX(2,1,2)),MX(6,1,4)),MX(11,1,4),"residuum up to20: mixed11 and1/4"),
row("S04",153,"PRINTED_ACTION",X("div",X("mul",N(20),N(9)),N(16)),MX(11,1,4),"same result by20 times9 divided16"),
row("S05",153,"PRINTED_ACCOUNT",X("add",MX(2,1,2),MX(6,1,4),MX(11,1,4)),N(20),"requested whole amount20"),
row("S06",153,"COMMON_GRADE_CLAIM",X("div",X("add",X("mul",MX(2,1,2),N(3)),X("mul",MX(6,1,4),N(4)),X("mul",MX(11,1,4),N(6))),N(20)),N(5),"same desired alloy ad5","No inserted100 numeral: fine total is computed inside the expression."),
row("T01",153,"PRINTED_ACTION",X("div",X("mul",N(10),N(5)),N(2)),N(25),"fixed10 of grade3; other amount25"),
row("T02",153,"PRINTED_ACTION",X("div",X("mul",N(10),N(9)),N(2)),N(45),"fixed10 of grade3; other amount45"),
row("T03",153,"LEXICAL_NUMBER_ACTION",X("mul",W(5,"quincuplum"),N(2)),N(10),"10 sunt quincuplum de2"),
row("T04",153,"LEXICAL_NUMBER_ACTION",X("mul",W(5,"quincuplum"),N(5)),N(25),"quincuplum de libris5 gives25"),
row("T05",153,"LEXICAL_NUMBER_ACTION",X("mul",W(5,"quincuplum"),N(9)),N(45),"quincuplum de9 gives45"),
row("T06",153,"COMMON_GRADE_CLAIM",X("div",X("add",X("mul",N(10),N(3)),X("mul",N(25),N(4)),X("mul",N(45),N(6))),X("add",N(10),N(25),N(45))),N(5),"ut facias monetam ad5","Neither total80 nor fine400 inserted as written numerals."),
row("A01",154,"PRINTED_ACCOUNT",X("add",N(1),N(2)),N(3),"first standard batch1 of grade3 and2 of grade6; total3"),
row("A02",154,"COMMON_GRADE_CLAIM",X("div",X("add",X("mul",N(1),N(3)),X("mul",N(2),N(6))),N(3)),N(5),"first standard alloy ad5"),
row("A03",154,"PRINTED_ACCOUNT",X("add",N(1),N(1)),N(2),"second standard batch1 of grade4 and1 of grade6; total2"),
row("A04",154,"COMMON_GRADE_CLAIM",X("div",X("add",X("mul",N(1),N(4)),X("mul",N(1),N(6))),N(2)),N(5),"second standard alloy ad5"),
row("A05",154,"LEXICAL_NUMBER_ACTION",X("mul",W(2,"bis"),N(1)),N(2),"first standard batch twice yields2 of grade3"),
row("A06",154,"LEXICAL_NUMBER_ACTION",X("mul",W(2,"bis"),N(2)),N(4),"first standard batch twice yields4 of grade6"),
row("A07",154,"PRINTED_ACTION",X("sub",N(20),X("add",N(2),N(4))),N(14),"subtract these from20, remainder14","No extra written subtotal6 is inserted."),
row("A08",154,"PRINTED_ACTION",X("div",N(14),N(2)),N(7),"14 divided second total2 gives7"),
row("A09",154,"LEXICAL_NUMBER_ACTION",X("mul",W(7,"septies"),N(1)),N(7),"second batch seven times:7 of grade4"),
row("A10",154,"LEXICAL_NUMBER_ACTION",X("mul",W(7,"septies"),N(1)),N(7),"second batch seven times:7 of grade6"),
row("A11",154,"PRINTED_ACCOUNT",X("add",N(4),N(7)),N(11),"final grade6 amount11 combines the two written components"),
row("A12",154,"PRINTED_ACCOUNT",X("add",N(2),N(7),N(11)),N(20),"final weights2,7,11 and total20"),
row("A13",154,"PRINTED_ACCOUNT",X("add",X("mul",N(2),N(3)),X("mul",N(7),N(4)),X("mul",N(11),N(6))),N(100),"in quibus libris20 sunt argenti uncie100"),
row("A14",154,"COMMON_GRADE_CLAIM",X("div",N(100),N(20)),N(5),"common ad5 goal and final ut oportet")
]

def arith(e):
    op,*v=e
    if op=="num":
        assert v[0].isdigit() and (v[0]=="0" or not v[0].startswith("0"))
        return F(int(v[0]))
    if op=="word_number": return F(v[0])
    if op=="mixed": return arith(v[0])+arith(v[1])/arith(v[2])
    a=[arith(x) for x in v]
    if op=="add": return sum(a,F(0))
    if op=="sub": return a[0]-a[1]
    if op=="mul":
        z=F(1)
        for x in a: z*=x
        return z
    if op=="div": return a[0]/a[1]
    raise ValueError(op)

def account(mass, branches):
    return {"grades":[N(3),N(4),N(6)],"target":N(5),"mass":N(mass),"branches":branches}
scaled = [
 ["setr",0,mix(portion("A",N(2)),portion("B",N(5)))],
 ["assertq",["grade",R(0)],MX(3,5,7)],
 ["setq",0,X("mul",["mass",R(0)],X("sub",N(5),N(3)))], # useful quantity8, not used to form a recipe
 ["setr",1,mix(R(0),portion("C",N(9)))],
 ["assertq",["mass",R(1)],N(16)],
 ["assertq",["fine",R(1)],N(80)],
 ["setr",2,scale(X("div",N(20),["mass",R(1)]),R(1))],
 ["assertweights",R(2),MX(2,1,2),MX(6,1,4),MX(11,1,4)],
 ["yield",R(2)]
]
# No unused scalar declaration is allowed in complete accounts.
scaled.pop(2)
alternate = [
 ["setr",0,mix(portion("A",N(1)),portion("C",N(2)))],
 ["setr",1,mix(portion("B",N(1)),portion("C",N(1)))],
 ["assertq",["mass",R(0)],N(3)],
 ["assertq",["mass",R(1)],N(2)],
 ["setr",2,["repeat_fill",R(0),R(1),N(20),N(2)]],
 ["assertweights",R(2),N(2),N(7),N(11)],
 ["assertq",["fine",R(2)],N(100)],
 ["yield",R(2)]
]
generated = [
 ["setr",0,mix(portion("A",N(4)),portion("B",N(4)))],
 ["setr",1,mix(R(0),portion("C",N(12)))],
 ["assertweights",R(1),N(4),N(4),N(12)],
 ["yield",R(1)]
]
EXAMPLES={"two_source_alternatives":account(20,[scaled,alternate]),
          "new_4_4_12":account(20,[generated]),
          "three_alternative_account":account(20,[scaled,alternate,generated])}

def evaluate(a):
    """Finite typed recipe-account semantics; references denote recipes, not stock."""
    assert set(a)=={"grades","target","mass","branches"} and len(a["grades"])==3
    assert all(x[0]=="num" and len(x)==2 and 0<=int(x[1])<=400 for x in a["grades"]+[a["target"],a["mass"]])
    grades=[arith(x) for x in a["grades"]]; target=arith(a["target"]); goal=arith(a["mass"])
    assert 0<grades[0]<grades[1]<target<grades[2]<=400 and goal>0
    assert 1<=len(a["branches"])<=3
    arities={"num":1,"mixed":3,"qref":1,"rref":1,"portion":2,"mix":2,"scale":2,
             "repeat_fill":4,"add":2,"sub":2,"mul":2,"div":2,"mass":1,"fine":1,"grade":1,
             "setq":2,"setr":2,"assertq":2,"assertweights":4,"yield":1}
    def shape(node):
        assert isinstance(node,list) and node and node[0] in arities
        op,*v=node; assert len(v)==arities[op]
        if op=="num": assert isinstance(v[0],str); return
        if op in ("qref","rref","setq","setr"):
            assert type(v[0]) is int and 0<=v[0]<8
            v=v[1:]
        if op=="portion": assert v[0] in ("A","B","C"); v=v[1:]
        for child in v:shape(child)
    outputs=[]
    for branch in a["branches"]:
        qr,rr={},{}
        assert 1<=len(branch)<=20 and branch[-1][0]=="yield"
        for statement in branch:shape(statement)
        def rec(e, depth=0):
            assert depth<=6
            op,*v=e
            if op=="rref": assert v[0] in rr; return rr[v[0]]
            if op=="portion":
                z=[F(0)]*3; amount=q(v[1],depth+1); assert amount>0
                z["ABC".index(v[0])]=amount; return tuple(z)
            if op=="mix": return tuple(x+y for x,y in zip(rec(v[0],depth+1),rec(v[1],depth+1)))
            if op=="scale":
                amount=q(v[0],depth+1); assert amount>0
                return tuple(amount*x for x in rec(v[1],depth+1))
            if op=="repeat_fill":
                left,right=rec(v[0],depth+1),rec(v[1],depth+1)
                total,k=q(v[2],depth+1),q(v[3],depth+1)
                j=(total-k*sum(left))/sum(right)
                assert k.denominator==1 and k>=1 and j.denominator==1 and j>=0
                return tuple(k*x+j*y for x,y in zip(left,right))
            raise ValueError(op)
        def q(e,depth=0):
            assert depth<=6
            op,*v=e
            if op=="qref": assert v[0] in qr; return qr[v[0]]
            if op in ("mass","fine","grade"):
                z=rec(v[0],depth+1); mass=sum(z); fine=sum(x*g for x,g in zip(z,grades))
                return mass if op=="mass" else fine if op=="fine" else fine/mass
            if op=="num":
                assert 0<=int(v[0])<=400
                return arith(e)
            if op in ("add","mul"): assert len(v)==2
            if op=="mixed":
                assert len(v)==3 and all(t[0]=="num" for t in v)
                assert 0<arith(v[1])<arith(v[2])
                value=q(v[0],depth+1)+q(v[1],depth+1)/q(v[2],depth+1)
            elif op=="add": value=sum(q(x,depth+1) for x in v)
            elif op=="sub": value=q(v[0],depth+1)-q(v[1],depth+1)
            elif op=="mul":
                value=F(1)
                for x in v:value*=q(x,depth+1)
            elif op=="div":value=q(v[0],depth+1)/q(v[1],depth+1)
            else:raise ValueError(op)
            assert abs(value)<=400 and value.denominator<=400
            return value
        for i,s in enumerate(branch):
            op,*v=s
            if op=="setq": assert v[0]==len(qr) and len(qr)<8; qr[v[0]]=q(v[1])
            elif op=="setr": assert v[0]==len(rr) and len(rr)<8; rr[v[0]]=rec(v[1])
            elif op=="assertq":
                assert v[0][0] in ("mass","fine","grade") and v[0]!=v[1]
                assert q(v[0])==q(v[1])
            elif op=="assertweights": assert rec(v[0])==tuple(q(x) for x in v[1:])
            elif op=="yield":
                assert i==len(branch)-1
                out=rec(v[0]); mass=sum(out); fine=sum(x*g for x,g in zip(out,grades))
                assert mass==goal and fine==goal*target
                outputs.append({"weights":[str(x) for x in out],"mass":str(mass),"fine":str(fine),"grade":str(fine/mass)})
            else:raise ValueError(op)
        def references(node):
            if not isinstance(node,list):return []
            if node and isinstance(node[0],str) and node[0] in ("qref","rref"):return [(node[0],node[1])]
            return [ref for child in node for ref in references(child)]
        used=set(references(branch))
        assert all(("qref",i) in used for i in qr) and all(("rref",i) in used for i in rr)
    # Shared header explicitly compares final states, not their ingredient vectors or identities.
    assert len({(x["mass"],x["fine"]) for x in outputs})==1
    return outputs

def words(x):
    """Fully explicit token stream, prior to any unknown script realization."""
    if isinstance(x,str): return [x]
    op,*v=x
    if op=="num": return ["NUM:"+v[0]]
    if op=="word_number": return ["WORDNUM:"+v[1]]
    if op in ("qref","rref"):return [op.upper()+":"+str(v[0])]
    if op in ("setq","setr"):return [op.upper()+":"+str(v[0])]+words(v[1])
    out=[op.upper()]
    for a in v:out+=words(a) if isinstance(a,list) else [str(a)]
    return out

def render(a):
    """Reviewable metalanguage, not a Voynich ciphertext or historical Latin text."""
    out=["GRADES"]
    for kind,g in zip("ABC",a["grades"]):out+=[kind]+words(g)
    out+=["TARGET"]+words(a["target"])+["TOTAL"]+words(a["mass"])
    for i,branch in enumerate(a["branches"]):
        out+=["FIRST" if i==0 else "ALTERNATIVELY"]
        for s in branch:out+=words(s)
    return " ".join(out)

def main():
    for e in EQS:assert arith(e["left"])==arith(e["right"]),e["id"]
    results={name:evaluate(a) for name,a in EXAMPLES.items()}
    mutations={}
    def reject(name,a):
        try:evaluate(a)
        except (AssertionError,ValueError,ZeroDivisionError):mutations[name]="REJECTED";return
        raise AssertionError("Accepted invalid fixture "+name)
    wrong=copy.deepcopy(EXAMPLES["new_4_4_12"]);wrong["branches"][0][1][2][2][1]="A"
    wrong["branches"][0][2]=["assertweights",R(1),N(16),N(4),N(0)]
    reject("put12_on_lowest_grade",wrong)
    wrong=copy.deepcopy(EXAMPLES["two_source_alternatives"]);wrong["branches"][0][1][2]=MX(3,1,2)
    reject("unweighted_lower_mean",wrong)
    wrong=copy.deepcopy(EXAMPLES["two_source_alternatives"]);wrong["branches"][1][4][2][-1]=N(1)
    reject("one_first_batch_leaves_noninteger_second_repeat",wrong)
    wrong=copy.deepcopy(EXAMPLES["new_4_4_12"]);wrong["branches"][0][1][2][1]=R(7)
    reject("undeclared_reference",wrong)
    wrong=copy.deepcopy(EXAMPLES["new_4_4_12"]);wrong["mass"]=N(19)
    reject("hidden_mass_loss",wrong)
    wrong=copy.deepcopy(EXAMPLES["two_source_alternatives"]);wrong["grades"]=[N(3),N(4),N(7)]
    reject("grade_gap_countermodel_with_written_weights_fixed",wrong)
    wrong=copy.deepcopy(EXAMPLES["new_4_4_12"]);wrong["branches"][0][0][2].append(N(99))
    reject("unconsumed_extra_argument",wrong)
    source={"status":"SOURCE_ONLY_NATIVE_REVIEWED_EQUATION_INVENTORY",
            "scope":"Whole printed pp152-154 subsection; mathematical action/result inventory, not diplomatic word-occurrence transcript.",
            "native_view_utc_interval":["2026-09-15T13:42:27Z","2026-09-15T13:45:06Z"],
            "printed_mixed_numbers_preserved":True,
            "lexical_numerical_words_separate_from_digits":True,
            "equations":EQS,
            "external_references":["partnership method","smaller book"],
            "general_advice":"Repeat first standard batch one or more integral times until the remainder, if possible, is integrally divisible by the second batch mass.",
            "generated_only_checks":["fixed10 total mass80","fixed10 fine content400","new weights4,4,12"],
            "source_pdf_sha256":"e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a"}
    source["native_render_sha256_by_printed_page"]={
        "152":"f28a569d4cead306a4c78377010fd95ff27419dd498dcc576a7ac543bf51a5c8",
        "153":"68890d859ebf5b0db09423bc5ebc8d91ef7d311c393a78341b2cdfcec3558b85",
        "154":"3c20175c4394c09420bb46e540d23781a5f87d980040d9af50005399ef1e79ba"}
    (D/"ALLOY_SOURCE_EQUATIONS.json").write_text(json.dumps(source,indent=2)+"\n")
    grammar={"status":"SOURCE_ONLY_SEMANTIC_CARD_WITH_CONDITIONAL_RENDERER",
             "limits":{"branches":3,"statements_per_branch":20,"registers_per_type":8,"expression_depth":6,
                       "numeric_literal_max":400,"rational_denominator_max":400},
             "examples":EXAMPLES,"metalanguage_accounts":{name:render(a) for name,a in EXAMPLES.items()}}
    atoms=list("0123456789")+["A","B","C","GRADES","TARGET","TOTAL","FIRST","ALTERNATIVELY",
          "NUM","SETQ","SETR","QREF","RREF","MIXED","ADD","SUB","MUL","DIV","MASS","FINE","GRADE",
          "PORTION","MIX","SCALE","REPEAT_FILL","ASSERTQ","ASSERTWEIGHTS","YIELD"]
    assert len(atoms)==len(set(atoms))==38
    grammar["renderer"]={"id":"R0","status":"HYPOTHETICAL_NOT_FIT","atoms":atoms,
        "atom_code_alphabet":"abcdefghijklmnopqrstuvwxyz","min_atom_code_length":1,"max_atom_code_length":8,
        "one_global_prefix_free_code":True,"digit_codes_shared_across_numerals_and_references":True,
        "word_separator":" ","prefix_traversal":True,"free_commentary":False,
        "source_omissions_enumerated_in":"ALLOY_FINITE_GRAMMAR.md"}
    (D/"ALLOY_FINITE_GRAMMAR.json").write_text(json.dumps(grammar,indent=2)+"\n")
    receipt={"status":"PASS_SOURCE_ONLY","source_equations":len(EQS),"complete_accounts":results,
             "mutations":mutations,"target_access":False,"digit_permutation_search":False,
             "historical_writing_rule_identified":False,
             "code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (D/"ALLOY_GRAMMAR_CHECKS.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"status":receipt["status"],"equations":len(EQS),"accounts":len(results),"rejected":len(mutations)}))
if __name__=="__main__":main()
