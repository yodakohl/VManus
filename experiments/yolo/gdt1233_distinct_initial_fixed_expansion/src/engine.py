"""Exact finite observed-use search for distinct-initial fixed codes."""
import time


def solve(words, alphabet, seconds=120):
    # words: ordered (stable identifier, tuple of working units) pairs.
    deadline = time.monotonic() + seconds
    order = {g:i for i,g in enumerate(alphabet)}
    stats = {'nodes':0,'contradictions':0,'identity_leaves':0,'positive_leaves':0,'max_depth':0}
    def visit(table):
        stats['nodes'] += 1
        stats['max_depth'] = max(stats['max_depth'],len(table))
        if time.monotonic() >= deadline:
            return 'UNKNOWN', {'kind':'timeout'}, None
        pending = {}
        used = set()
        for identifier, word in words:
            pos = 0
            while pos < len(word):
                head = word[pos]
                if head not in table:
                    pending.setdefault(head,[]).append(word[pos:])
                    break
                code = table[head]
                if word[pos:pos+len(code)] != code:
                    stats['contradictions'] += 1
                    return 'NEGATIVE', {'kind':'conflict','word_id':identifier,'offset':pos,'head':head,'code':list(code),'remainder':list(word[pos:])}, None
                used.add(head)
                pos += len(code)
        if not pending:
            longer = sorted(g for g in used if len(table[g]) > 1)
            if longer:
                stats['positive_leaves'] += 1
                witness = {g:list(table.get(g,(g,))) for g in alphabet}
                return 'NONTRIVIAL', {'kind':'positive','used_heads':sorted(used),'longer_used_heads':longer}, witness
            stats['identity_leaves'] += 1
            return 'NEGATIVE', {'kind':'identity_only','used_heads':sorted(used)}, None
        domains = {}
        for head, remainders in pending.items():
            prefix = remainders[0]
            for other in remainders[1:]:
                k = 0
                while k < min(len(prefix),len(other)) and prefix[k] == other[k]:
                    k += 1
                prefix = prefix[:k]
            assert prefix and prefix[0] == head
            domains[head] = [prefix[:n] for n in range(len(prefix),0,-1)]
        head = min(domains,key=lambda g:(len(domains[g]),order[g]))
        options = domains[head]
        node = {'kind':'branch','head':head,'options':[list(c) for c in options],'children':[]}
        for code in options:
            table[head] = code
            status, child, witness = visit(table)
            del table[head]
            node['children'].append({'code':list(code),'node':child})
            if status in {'NONTRIVIAL','UNKNOWN'}:
                node['search_status'] = status
                return status,node,witness
        node['search_status'] = 'NEGATIVE'
        return 'NEGATIVE',node,None
    status, proof, witness = visit({})
    return {'status':'ALL_USED_CODES_SINGLETON' if status=='NEGATIVE' else status,'certificate':proof,'witness':witness,'statistics':stats}
