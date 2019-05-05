"""
by:  Andrew Parsadayan

The following website can be used to check my results, use ~ && || -> to maintain compatibility.
http://web.stanford.edu/class/cs103/tools/truth-table-tool/

Note: multiple consecutive NOTs (~ ~ x) ARE VALID, other consecutive actions are not valid
Note: input MUST be space delimited
Note: look for "##--##" (5 of them) to change spacing on output table

"""


def process_statement(original_input):
    NOT, AND, OR, IMPLIES = ['~', '!'], ['&', '&&', '^', '/\\'], ['|', '||', '\\/'], ['->', '=>']
    ACTIONS_LIST = NOT + AND + OR + IMPLIES
    DEFAULT = (False, '|', False)
    # original_input = '~ x & ( ~ y | ~ z ) -> z'
    variables = sorted(list(set([a for a in original_input.split() if a.isalpha()])))
    vals_table = []
    output_lines = []

    def action(v1, op, v2):
        return (v1 & v2) if op in AND else (v1 | v2) if op in OR else (not v1) | v2 if op in IMPLIES else 'ERROR: '+op

    for i in range(2**len(variables))[::-1]:
        n, a, v, q = *DEFAULT, []
        for symb in original_input.split():
            if   symb == '(': n, a, v, q = *DEFAULT, q+[[n, a, v]]
            elif symb == ')': v, a, n = action(*(lambda n, a, v, tv: (v, a, (tv+n) % 2))(*q[-1], v)), q.pop()[1], False
            elif symb in NOT: n = not n
            elif symb in ACTIONS_LIST: a = symb
            elif symb in variables: v, n = action(v, a, (i//2**(variables[::-1].index(symb)) % 2 + n) % 2), False
            else: output_lines.append(f'BAD VALUE @ {i} = "{symb}"')
        vals_table.append([i//2**x % 2 for x in range(len(variables))[::-1]]+[v])

    ft = variables + [original_input]
    output_lines.append('\n'.join(['Input: '+original_input, '', ' | '.join(ft), '-+-'.join(['-'*len(a) for a in ft])]))
    output_lines.append('\n'.join(' | '.join([('{:^%d}'%(len(tx))).format(v) for tx, v in zip(ft, val)]) for val in vals_table))
    return '\n'.join(output_lines)
