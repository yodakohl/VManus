"""Small exposed teaching-case replay of IDEA972, not a native writer."""
import hashlib, json, re
from pathlib import Path
BASE = Path(__file__).parent
RAW = BASE / "COMMON_SUFFIX_BLOCK_WRITER_RAW_20261007.json"
EXPECTED_HASH = "ee09344d56bb446e44ae6d29c5959279ab62e1557e1550745ff61564d37f2326"
assert hashlib.sha256(RAW.read_bytes()).hexdigest() == EXPECTED_HASH
spec = json.loads(RAW.read_text())["design"]["source_contract"]
allowed = set(spec["lowercase_letters"] + "".join(spec["additional_characters"]))
def eligible(w):
    return bool(re.fullmatch("[a-z]+", w))
def suffix(a,b):
    k=0
    for x,y in zip(reversed(a),reversed(b)):
        if x!=y: break
        k+=1
    return a[-k:] if k else ""
def encode(text):
    words=text.split(" ")
    assert all(w and set(w)<=allowed for w in words)
    out=[]; i=0
    while i<len(words):
        s=suffix(words[i],words[i+1]) if i+1<len(words) and eligible(words[i]) and eligible(words[i+1]) else ""
        if len(s)<2:
            out.append(words[i]); i+=1; continue
        out.append("@{"+s+"}")
        while i<len(words) and eligible(words[i]) and words[i].endswith(s):
            out.append(words[i][:-len(s)] or "@0"); i+=1
        out.append("@}")
    return " ".join(out)
def decode(text):
    out=[]; active=None; n=0
    for g in text.split():
        if active is None:
            m=re.fullmatch(r"@\{([a-z]{2,})\}",g)
            if m: active=m[1]; n=0
            elif g and set(g)<=allowed: out.append(g)
            else: raise ValueError("bad outside group")
        elif g=="@}":
            if n<2: raise ValueError("short block")
            active=None
        elif g=="@0": out.append(active); n+=1
        elif eligible(g): out.append(g+active); n+=1
        else: raise ValueError("bad member")
    if active is not None: raise ValueError("unclosed block")
    return " ".join(out)
cases=[
 ("mahlen kochen sieben", "@{en} mahl koch sieb @}"),
 ("kochen mischen sieben", "@{chen} ko mis @} sieben"),
 ("salz salz salz", "@{salz} @0 @0 @0 @}"),
 ("holz salz salz salz", "@{lz} ho sa sa sa @}"),
 ("Wir sehen roten alten Stoff.", "Wir @{en} seh rot alt @} Stoff."),
 ("backpack pack", "@{pack} back @0 @}"),
 ("heating seating seating seating", "@{eating} h s s s @}"),
 ("station nation", "@{ation} st n @}"),
 ("staring daring", "@{aring} st d @}"),
 ("station", "station"),
]
rows=[]
for src, expected in cases:
    actual=encode(src)
    assert actual==expected and decode(actual)==src
    rows.append(dict(source=src, written=actual, readback=decode(actual),
                     source_characters=len(src), teaching_characters=len(actual),
                     net_characters_saved=len(src)-len(actual)))
noncanonical=[]
for written in ["@{en} koch koch @}", "@{en} mahl koch @} sieben"]:
    src=decode(written); canonical=encode(src)
    assert canonical!=written
    noncanonical.append(dict(written=written,readback=src,canonical=canonical))
try: decode("@{en} mahl koch")
except ValueError: unclosed_rejected=True
else: raise AssertionError("unclosed block accepted")
result=dict(status="ABSTRACT_INVERSE_AND_CANONICALITY_SUPPORTED_ONLY",
 raw_sha256=EXPECTED_HASH, cases=rows, noncanonical=noncanonical,
 unclosed_rejected=unclosed_rejected,
 proof="Each member p expands to p+s; empty members expand to s. Controls unambiguously scope s in the teaching alphabet. Literal tokens and emitted word order are unchanged.",
 first_pair_obligation="When BOTH of the first two member prefixes are nonempty, they have no nonempty common suffix; otherwise that suffix would belong to the first pair's longer common suffix. Do not skip empty members when identifying the first pair. In particular two identical nonempty first members are noncanonical. Later identical prefixes remain legal.",
 ascii_cost="For n words, suffix length k and z empty prefixes: net characters saved = (n-1)*k - 7 - 2*z, including teaching controls and extra spaces; physical glyph cost is unknown.",
 limits=["Invented examples, exposed design, no historical attestation", "Same-author replay, not independent source recovery", "No 22-sign carrier or native meanings/statistics", "Source paragraph input is normalized per RAW; no diplomatic whitespace recovery", "Paragraph/overwide physical realization not validated by this small replay" ])
print(json.dumps(result,ensure_ascii=False,indent=2))
