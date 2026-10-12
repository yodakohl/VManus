"""Source-free finite checks for the unchanged IDEA001035 reader theorem."""
from itertools import product
import json


def initial_run(word):
    return next((i for i, char in enumerate(word) if char != word[0]), len(word))


def encode_left(left, right):
    if left[-1] != right[0]:
        return left
    removed = min(initial_run(left[::-1]), initial_run(right), len(left) - 1)
    return left[:-removed] if removed else left


def main():
    words = [''.join(w) for n in range(1, 5) for w in product('ab', repeat=n)]
    local_cases = record_cases = 0
    for output in words:
        for right in words:
            char, run = right[0], initial_run(right)
            actual = {output + char * j for j in range(run + 1)
                      if encode_left(output + char * j, right) == output}
            expected = ({output + char * run}
                        if len(output) >= 2 and output[-1] == char
                        else {output + char * j for j in range(run + 1)})
            assert actual == expected
            local_cases += 1
    for n in range(1, 4):
        for written in product(words[:6], repeat=n):
            candidates = [(written[-1],)]
            for output in written[-2::-1]:
                candidates = [(output + right[0][0] * j,) + right
                              for right in candidates
                              for j in range(initial_run(right[0]) + 1)
                              if encode_left(output + right[0][0] * j, right[0]) == output]
            branches = sum(len(a) == 1 or a[-1] != b[0]
                           for a, b in zip(written, written[1:]))
            assert len(set(candidates)) == len(candidates) >= 2 ** branches
            assert (len(candidates) == 1) == (branches == 0)
            assert all(tuple(encode_left(a, b) for a, b in zip(c, c[1:])) + (c[-1],) == written
                       for c in candidates)
            record_cases += 1
    print(json.dumps({'status': 'PASS', 'source_free': True, 'native_data_read': False,
                      'local_cases': local_cases, 'record_cases': record_cases}, sort_keys=True))


if __name__ == '__main__':
    main()
