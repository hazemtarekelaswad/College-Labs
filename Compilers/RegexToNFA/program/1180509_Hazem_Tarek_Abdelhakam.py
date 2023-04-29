from distutils.log import error
import enum
import json
import sys
import graphviz as gv

CONCAT_SYMBOL = '#'
EPS = 'EPSILON'

def is_letter(symbol):
    letters = r'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/=_&^%$!{}`2,~<>?\'":'
    return (symbol in letters)


def is_unary(symbol):
    unary_operators = r'*+'
    return (symbol in unary_operators)


def is_binary(symbol):
    binary_operators = '|' + CONCAT_SYMBOL
    return (symbol in binary_operators)


def is_operator(symbol): return (is_unary(symbol) or is_binary(symbol))


def get_priority(operator):
    priority = {
        '*': 3,
        '+': 3,
        CONCAT_SYMBOL: 2,
        '|': 1,
        '(': 0,  # lowest priority
    }
    if operator not in priority:
        error(f'get_priority(op): {operator} is not an operator')
        exit(0)

    return priority[operator]


def validate_regex(regex):
    if regex == '':
        return (False, 'INVALID REGEX: empty regex')

    for i in range(len(regex)):
        if regex[i] == ' ' or regex[i] == '\t':
            return (False, 'INVALID REGEX: contains white spaces')

        if is_operator(regex[i]) and i == 0:
            return (False, f'INVALID REGEX: Operator {regex[i]} at the beginning')

        if is_binary(regex[i]) and i == len(regex) - 1:
            return (False, f'INVALID REGEX: Operator {regex[i]} at the end')

        if is_unary(regex[i]) and (is_operator(regex[i - 1]) or regex[i - 1] == '(' or regex[i - 1] == '['):
            return (False, f'INVALID REGEX: Operator {regex[i]} has invalid operand')

        if is_binary(regex[i]) and (is_binary(regex[i - 1]) or regex[i - 1] == '(' or regex[i - 1] == '[' or is_operator(regex[i + 1]) or regex[i + 1] == ')' or regex[i + 1] == ']'):
            return (False, f'INVALID REGEX: Operator {regex[i]} has invalid operands')

    return (True, 'VALID REGEX')

def resolve_charset(charset):
    result = ''
    for i in range(len(charset)):
        if charset[i] == '-' and (not is_letter(charset[i - 1]) or not is_letter(charset[i + 1])):
            error('INVALID REGEX: Charset contains invalid syntax')
            exit(0)
        if charset[i] == '-' and ord(charset[i - 1]) > ord(charset[i + 1]):
            error('INVALID REGEX: Charset range is invalid')
            exit(0)
        if charset[i] == '-':
            result += f'[{charset[i - 1]}-{charset[i + 1]}]|'
        elif is_letter(charset[i]) and (charset[i + 1] != '-' and charset[i - 1] != '-'):
            result += charset[i] + '|'

    result = result.removesuffix('|')
    print(result)
    return result

def resolve_all_charsets(regex):

    class Status(enum.Enum):
        NORMAL = 0
        OPEN = 1
        CLOSING = 2

    first = 0
    last = 0
    status = Status.NORMAL
    is_opened = False
    result = ''

    for last in range(len(regex)):
        pack = ''
        if regex[last] == '[':
            first = last
            status = Status.OPEN
            is_opened = True
        elif regex[last] == ']':
            pack = resolve_charset(regex[first: last + 1])
            status = Status.CLOSING

        if status == Status.NORMAL:
            result += regex[last]
        elif status == Status.CLOSING:
            result += f'({pack})'
            if is_opened:
                status = Status.NORMAL

    if status != Status.NORMAL:
        error('INVALID REGEX: Brackets are not balanced')
        exit(0)
    print(result)
    return result


def replace_concat(regex):
    modified_regex = ''
    for i in range(len(regex) - 1):
        if (is_letter(regex[i]) or regex[i] == ']') and (is_letter(regex[i + 1]) or regex[i + 1] == '[') \
                or is_unary(regex[i]) and (is_letter(regex[i + 1]) or regex[i + 1] == '[' or regex[i + 1] == '(') \
                or (is_letter(regex[i]) or regex[i] == ']') and regex[i + 1] == '(' \
                or regex[i] == ')' and (is_letter(regex[i + 1]) or regex[i + 1] == '[') \
                or regex[i] == ')' and regex[i + 1] == '(':

            modified_regex += regex[i] + CONCAT_SYMBOL
        else:
            modified_regex += regex[i]

    modified_regex += regex[-1]
    return modified_regex

def regex_to_postfix(regex):    

    regex = replace_concat(regex)

    output_queue = []
    operator_stack = []

    i = 0
    while (i < len(regex)):
        if is_letter(regex[i]):
            output_queue.append(regex[i])

        elif regex[i] == '[':
            char = ''
            pointer = i
            while regex[pointer] != ']':
                char += regex[pointer]
                pointer += 1
            char += ']'
            output_queue.append(char)
            i = pointer

        elif is_operator(regex[i]):
            while len(operator_stack) and get_priority(regex[i]) <= get_priority(operator_stack[-1]):
                output_queue.append(operator_stack.pop())
            operator_stack.append(regex[i])

        elif regex[i] == '(':
            operator_stack.append(regex[i])

        elif regex[i] == ')':
            while len(operator_stack) and operator_stack[-1] != '(':
                output_queue.append(operator_stack.pop())
            if not len(operator_stack):
                error(
                    'INVALID REGEX: regex_to_postfix(re): parentheses are not balanced in the passed regex')
                exit(0)
            operator_stack.pop()
        else:
            error(f'INVALID REGEX: Invalid character ({regex[i]}) in regex')
            exit(0)

        i += 1

    while len(operator_stack):
        popped = operator_stack.pop()
        if popped == '(':
            error(
                'INVALID REGEX: regex_to_postfix(re): parentheses are not balanced in the passed regex')
            exit(0)
        output_queue.append(popped)

    return ''.join(output_queue)



# postfix of A + B * C: AB*C+


def postfix_to_nfa(postfix):
    stack = []

    states = []
    start_state = 0
    accepting_state = 1

    counter = -1
    first_state = 0
    second_state = 0

    i = 0
    while (i < len(postfix)):
        if is_letter(postfix[i]):
            counter += 1
            first_state = counter
            counter += 1
            second_state = counter

            states.append({})
            states.append({})

            stack.append([first_state, second_state])
            states[first_state][postfix[i]] = [second_state]

        elif postfix[i] == '[':
            char = ''
            pointer = i
            while postfix[pointer] != ']':
                char += postfix[pointer]
                pointer += 1
            char += ']'

            counter += 1
            first_state = counter
            counter += 1
            second_state = counter

            states.append({})
            states.append({})

            stack.append([first_state, second_state])
            states[first_state][char] = [second_state]

            i = pointer

        elif postfix[i] in '*+':
            frst, sec = stack.pop()
            counter += 1
            first_state = counter
            counter += 1
            second_state = counter

            states.append({})
            states.append({})

            stack.append([first_state, second_state])

            states[sec][EPS] = [frst, second_state]
            if postfix[i] == '*':
                states[first_state][EPS] = [frst, second_state]
            else:  # (+)
                states[first_state][EPS] = [frst]

            if start_state == frst:
                start_state = first_state
            if accepting_state == sec:
                accepting_state = second_state

        elif postfix[i] == CONCAT_SYMBOL:
            frst_frst, frst_sec = stack.pop()
            sec_frst, sec_sec = stack.pop()

            stack.append([sec_frst, frst_sec])
            states[sec_sec][EPS] = [frst_frst]

            if start_state == frst_frst:
                start_state = sec_frst
            if accepting_state == sec_sec:
                accepting_state = frst_sec

        else:   # (|)
            counter += 1
            first_state = counter
            counter += 1
            second_state = counter

            states.append({})
            states.append({})

            frst_frst, frst_sec = stack.pop()
            sec_frst, sec_sec = stack.pop()

            stack.append([first_state, second_state])

            states[first_state][EPS] = [sec_frst, frst_frst]
            states[frst_sec][EPS] = [second_state]
            states[sec_sec][EPS] = [second_state]

            if start_state == frst_frst or start_state == sec_frst:
                start_state = first_state
            if accepting_state == sec_sec or accepting_state == frst_sec:
                accepting_state = second_state
        i += 1
    return (start_state, accepting_state, states)


def nfa_to_json(nfa, file):
    json_data = {}
    json_data['startingState'] = f'S{nfa[0]}'
    for index in range(len(nfa[2])):
        json_data[f'S{index}'] = {'isTerminatingState': nfa[1] == index}
        for key, value in nfa[2][index].items():
            dist = [f'S{item}' for item in value]
            json_data[f'S{index}'].update({key: dist})

    with open(file, 'w') as json_file:
        json.dump(json_data, json_file, indent = 2)
    return json_data

def draw(json_data):
    nfa_dot = gv.Digraph()
    
    nfa_dot.node(json_data['startingState'].removeprefix('S'), json_data['startingState'], style='filled', color='lightgrey')
    for key, val in json_data.items():
        if key == 'startingState': continue
        for alpha, dest in val.items():
            if alpha == 'isTerminatingState' and dest:
                nfa_dot.node(key.removeprefix('S'), key, shape='doublecircle', style='filled', color='lightgreen')
            elif alpha == 'isTerminatingState' and not dest:
                nfa_dot.node(key.removeprefix('S'), key, shape='circle')
            else:
                for d in dest:
                    nfa_dot.edge(key.removeprefix('S'), d.removeprefix('S'), label = 'ε' if alpha == EPS else alpha)
    nfa_dot.render('nfa', view=True)
    


def main():
    if sys.argv[1] != 'convert':
        error('the word "convert" is missing,\nplease type the command as: python <file_name> convert "<regex>"')
        return

    regex = sys.argv[2]
    regex = regex.removeprefix('"').removesuffix('"')

    is_valid, msg = validate_regex(regex)
    if not is_valid:
        error(msg)
        exit(0)

    regex = resolve_all_charsets(regex)
    # print(regex)
    postfix = regex_to_postfix(regex)
    # print(postfix)
    nfa = postfix_to_nfa(postfix)
    print(nfa)
    json_data = nfa_to_json(nfa, 'nfa.json')

    draw(json_data)


if __name__ == '__main__':
    main()
