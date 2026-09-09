"""Finite orthographic CV code; no observed Voynich key or linguistic claim."""
import re, unicodedata
VOWELS='aeiouy'
LETTERS='abcdefghijklmnopqrstuvwxyz'

def normalize(s):
    s=s.casefold().replace('æ','ae').replace('œ','oe')
    return ''.join(c for c in unicodedata.normalize('NFD',s) if not unicodedata.combining(c))

def alphabetic(s): return bool(re.fullmatch('[a-z]+',s))

def inventory(inherent):
    return tuple(['C:'+c for c in LETTERS if c not in VOWELS]+['V:'+v for v in VOWELS if v!=inherent]+['CARRIER','VIRAMA'])

def components(word,inherent):
    assert inherent in VOWELS and alphabetic(word)
    out=[];i=0
    while i<len(word):
        c=word[i]
        if c not in VOWELS:
            out.append('C:'+c)
            if i+1<len(word) and word[i+1] in VOWELS:
                v=word[i+1];i+=2
                if v!=inherent:out.append('V:'+v)
            else:out.append('VIRAMA');i+=1
        else:
            out.append('CARRIER')
            if c!=inherent:out.append('V:'+c)
            i+=1
    return tuple(out)

def decode_components(parts,inherent):
    out=[];i=0
    while i<len(parts):
        c=parts[i];i+=1
        if c=='CARRIER':consonant=''
        elif c.startswith('C:'):consonant=c[2:]
        else:raise ValueError('noninitial modifier')
        v=inherent
        if i<len(parts) and parts[i].startswith('V:'):
            v=parts[i][2:];i+=1
            if v==inherent:raise ValueError('redundant inherent mark')
        elif i<len(parts) and parts[i]=='VIRAMA':
            if not consonant:raise ValueError('vowel carrier with virama')
            v='';i+=1
        out.append(consonant+v)
    word=''.join(out)
    if components(word,inherent)!=tuple(parts):raise ValueError('noncanonical component stream')
    return word

def pattern(seq):
    seen={};return tuple(seen.setdefault(x,len(seen)) for x in seq)

def prefix_free(codes):
    codes=set(codes)
    return all(len(c) in (1,2) for c in codes) and all(c[:1] not in codes for c in codes if len(c)==2)

def segment(word,singletons):
    out=[];i=0
    while i<len(word):
        n=1 if word[i] in singletons else 2
        if i+n>len(word):return None
        out.append(word[i:i+n]);i+=n
    return tuple(out)

def complete_capacity(singletons,alphabet,used):
    # Codewords not observed must still be extendable to27 distinct components.
    return len(singletons)+len(alphabet)*(len(alphabet)-len(singletons))>=27 and len(set(used))<=27
