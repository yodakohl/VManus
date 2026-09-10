"""Select phase-approved IT2a JSON objects without parsing other bodies."""
import hashlib
import json
import mmap
import re


def skip_space(buf, i):
    while buf[i] in b' \t\r\n': i += 1
    return i


def string_end(buf, i):
    assert buf[i] == 34
    i += 1
    while True:
        j = buf.find(b'"', i)
        assert j >= 0
        k = j - 1
        while buf[k] == 92: k -= 1
        if (j - 1 - k) % 2 == 0: return j + 1
        i = j + 1


def value_end(buf, i):
    i = skip_space(buf, i)
    if buf[i] == 34: return string_end(buf, i)
    if buf[i] not in (91, 123):
        while buf[i] not in b',]} \t\r\n': i += 1
        return i
    depth = 1
    i += 1
    while depth:
        c = buf[i]
        if c == 34: i = string_end(buf, i); continue
        if c in (91, 123): depth += 1
        if c in (93, 125): depth -= 1
        i += 1
    return i


def fields(buf, start):
    """Only top-level keys decoded; values returned as byte spans."""
    assert buf[start] == 123
    i = skip_space(buf, start + 1)
    while buf[i] != 125:
        end = string_end(buf, i)
        key = json.loads(buf[i:end])
        i = skip_space(buf, end)
        assert buf[i] == 58
        begin = skip_space(buf, i + 1)
        end = value_end(buf, begin)
        yield key, (begin, end)
        i = skip_space(buf, end)
        if buf[i] == 44: i = skip_space(buf, i + 1)
        else: assert buf[i] == 125


def select_frames(path, expected_sha, approved):
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    assert digest == expected_sha, 'legacy cache changed'
    allowed = {h['paragraph_id']: h for h in approved}
    assert len(allowed) == len(approved)
    for h in approved:
        assert not h['page'].startswith('f84')
        assert h['physical_folio'] == re.match(r'f[0-9]+', h['page']).group()
    out = []
    with path.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as buf:
        frames_span = dict(fields(buf, skip_space(buf, 0)))['frames']
        i = skip_space(buf, frames_span[0] + 1)
        while buf[i] != 93:
            end = value_end(buf, i)
            frame_fields = dict(fields(buf, i))
            def scalar(key):
                a, b = frame_fields[key]
                return json.loads(buf[a:b])
            # The raw selector is checked before any readings payload is parsed.
            page = scalar('page')
            assert not page.startswith('f84'), 'sealed selector in supposedly guarded cache'
            pid = scalar('paragraph_id')
            if pid in allowed:
                h = allowed[pid]
                physical = scalar('physical_folio')
                assert page == h['page'] and physical == h['physical_folio']
                readings = dict(fields(buf, frame_fields['readings'][0]))
                a, b = readings['IT2a']
                reading = json.loads(buf[a:b])
                assert reading['eligible'] and reading['groups'][0]['sta'] == h['head']
                out.append(dict(paragraph_id=pid, page=page, physical_folio=physical,
                                head=h['head'], groups=reading['groups']))
            i = skip_space(buf, end)
            if buf[i] == 44: i = skip_space(buf, i + 1)
            else: assert buf[i] == 93
    assert {f['paragraph_id'] for f in out} == set(allowed)
    return sorted(out, key=lambda f: f['paragraph_id'])
