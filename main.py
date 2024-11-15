from debugpy.common.timestamp import current

REPETITION_LIMIT = 1000

def regex_parse(r):
    current_parse, node = parse_split(r,0)
    if current_parse != len(r):
        raise Exception ('unexpected")"')
    return node

def parse_split(r, current_parse):
    current_parse, prev = parse_concat(r, current_parse)
    while current_parse < len(r):
        if r[current_parse] == ')':
            break
        if r[current_parse] != '|':
            raise Exception('Exception "|" operator')
        current_parse, node = parse_concat(r, current_parse + 1)
        prev = ('split', prev,node)
    return current_parse, prev

def parse_concat(r, current_parse):
    prev = None
    while current_parse < len(r):
        if r[current_parse] in '|)':
            break
        current_parse, node = parse_node(r, current_parse)
        if prev is None:
            prev = node
        else:
            prev = ('cat', prev, node)
    return current_parse, prev

def parse_node(r, current_parse):
    ch = r[current_parse]
    current_parse += 1

    if ch in '|)':
        raise Exception(f'Unexpected "{ch}"')
    if ch == '(':
        current_parse, node = parse_split(r, current_parse)
        if current_parse < len(r) and r[current_parse] == ')':
            current_parse += 1
        else:
            raise Exception('Unbalanced parenthesis')

    elif ch == '.':
        node = 'dot'
    elif ch in '*+{':
        raise Exception('Nothing to repeat')
    else:
        node = ch

    current_parse, node = parse_postfix(r, current_parse, node)
    return current_parse, node

def parse_postfix(r, current_parse, node):
    if current_parse == len(r) or r[current_parse] not in '*+{':
        return current_parse, node

    ch = r[current_parse]
    current_parse += 1

    if ch == '*':
        rmin, rmax = 0, float('inf')
    elif ch == '+':
        rmin, rmax = 1, float('inf')
    else:
        current_parse, rmin = parse_int(r, current_parse)
        if rmin is None:
            raise Exception('Excepted integer in {}')
        rmax = rmin

        if current_parse < len(r) and r[current_parse] == ',':
            current_parse, rmax_val = parse_int(r, current_parse + 1)
            rmax = rmax_val if rmax_val is not None else float('inf')

        if current_parse < len(r) and r[current_parse] == '}':
            current_parse += 1
        else:
            raise Exception('Unbalanced brace')


        if rmax != float('inf') and rmax > REPETITION_LIMIT:
            raise Exception('Repetition number too large')
        if rmin > REPETITION_LIMIT:
            raise Exception('Repetition number too large')


    if rmax < rmin:
        raise Exception('Min repeat greater than max repeat')

    return current_parse, ('repeat', node, rmin, rmax)

def parse_int(r, current_parse):
    start = current_parse
    while current_parse < len(r) and r[current_parse].isdigit():
        current_parse += 1
    return current_parse, int(r[start:current_parse]) if start != current_parse else None

def run_tests():
    test_cases = [
        ('', None),
        ('.', 'dot'),
        ('a', 'a'),
        ('ab', ('cat', 'a', 'b')),
        ('a|b', ('split', 'a', 'b')),
        ('a+', ('repeat', 'a', 1, float('inf'))),
        ('a*', ('repeat', 'a', 0, float('inf'))),
        ('a{3}', ('repeat', 'a', 3, 3)),
        ('a{3,6}', ('repeat', 'a', 3, 6)),
        ('a{3,}', ('repeat', 'a', 3, float('inf'))),
        ('(a|b)c', ('cat', ('split', 'a', 'b'), 'c')),
        ('a|bc', ('split', 'a', ('cat', 'b', 'c'))),
        ('(a|b)*c', ('cat', ('repeat', ('split', 'a', 'b'), 0, float('inf')), 'c')),
    ]

    for pattern, expected in test_cases:
        try:
            result = regex_parse(pattern)
            assert  result == expected, f"Test failed for '{pattern}'\nExpected: {expected}\nGot: {result}"
            print(f"Test passed for '{pattern}'")
        except Exception as e:
            print(f"Test failed for '{pattern}': {str(e)}")

if __name__ == "__main__":
    run_tests()