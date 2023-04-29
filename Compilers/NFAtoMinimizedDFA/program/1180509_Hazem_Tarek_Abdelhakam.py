import json
import sys
from ordered_set import OrderedSet
import graphviz as gv
from distutils.log import error


big_dfa = []

# perform DFS on the passed state and fill @eps_closure with the visited states
def get_eps_closure(nfa, state, eps_closure):
    eps_closure.add(state)
    if 'EPSILON' not in nfa[state]:
        return

    for dest in nfa[state]['EPSILON']:
        get_eps_closure(nfa, dest, eps_closure)

# Given a dfa state, construct other dfa states from it 
def generate_states(nfa, alphabet, dfa_state, id):
    generated_states = []
    for alpha in alphabet:
        st = OrderedSet()
        for state in dfa_state:
            if alpha not in nfa[state]: continue
            for dest in nfa[state][alpha]:
                get_eps_closure(nfa, dest, st)
        

        for item in big_dfa:
            if st == item[1]:
                generated_states.append(item + (1,)) # append the found state with its id
                break
        else: # create new state with new id
            if st:
                generated_states.append((id[0], st, 0))
                big_dfa.append((id[0], st))
                id[0] += 1
            else:
                generated_states.append(('PHI', st, 0))
                big_dfa.append(('PHI', st))
                id[0] += 1

    return generated_states

# given the starting state of NFA, construct the DFA from it
def generate_all_states(nfa, alphabet, accepting_state, accepting_states, first_dfa_state, states, id):
    if len(first_dfa_state) == 0: return
    for item in first_dfa_state:
        if len(item[1]): break  
    else: return

    new_states = []
    for item in first_dfa_state:
        if item[2]: continue
        new_states.append(item)
    
    if len(new_states) == 0: return 
    
    for item in new_states:
        gen_states = generate_states(nfa, alphabet, item[1], id)
        states.append({item[0]: {}})
        for index in range(len(gen_states)):
            states[-1][item[0]][alphabet[index]] = gen_states[index][0]
            if accepting_state in gen_states[index][1]:
                accepting_states.add(gen_states[index][0])

        print(f'{item[0]} {item[1]}:  {gen_states}')
        print()

        generate_all_states(nfa, alphabet, accepting_state, accepting_states, gen_states, states, id)

# Convert nfa to dfa
def nfa_to_dfa(nfa, alphabet, starting_state, accepting_state):
    first_dfa_state = OrderedSet()
    accepting_states = OrderedSet()
    get_eps_closure(nfa, starting_state, first_dfa_state)


    id = [0]
    first_dfa_state = (id[0], first_dfa_state)

    if accepting_state in first_dfa_state[1]:
        accepting_states.add(first_dfa_state[0])

    big_dfa.append(first_dfa_state)
    id[0] += 1

    states = []
    generate_all_states(nfa, alphabet, accepting_state, accepting_states, [first_dfa_state + (0,)], states, id)
    # print(states)
    print('Accepting ',  accepting_states)
    return (states, starting_state, accepting_states)

# Get non-accepting states from a given dfa
def get_non_accepting_states(dfa, accepting):
    non_accepting = OrderedSet()
    for state in  dfa:
        key = list(state.keys())[0]
        if key not in accepting and key != 'PHI':
            non_accepting.add(key)
    return non_accepting

# Get the destnation state from a given input
def get_dest(dfa, state, inp):
    for st in dfa:
        key = list(st.keys())[0] 
        if key == state: return st[key][inp]
    return -1   # NOT FOUND

# Find which partition a given state in
def find_partition(partitions, state):
    for i in range(len(partitions)):
        if state in partitions[i]:
            return i
    return -1   # NOT FOUND

# Split or partition the dfa using equavalence minimization method 
def partition(dfa, alphabet, partitions):
    new_partitions = []
    for partition in partitions:
        if len(partition) == 1: 
            new_partitions.append(partition)
            continue
        new_partitions.append(OrderedSet([-1 if len(partition) == 0 else partition[0]]))

        for i in range(1, len(partition)):
            for j in range(len(new_partitions)):

                for alpha in alphabet:
                    dest1 = get_dest(dfa, partition[i], alpha)
                    dest2 = get_dest(dfa, new_partitions[j][0], alpha)
                    if find_partition(partitions, dest1) != find_partition(partitions, dest2):
                        break
                else:   # if it ends normally without hitting break
                    new_partitions[j].add(partition[i])
                    break
            else:   # if it ends normally without hitting break
                new_partitions.append(OrderedSet([partition[i]]))
    return new_partitions

# Minimize a given dfa
def minimize_dfa(dfa, accepting, alphabet):
    non_accepting = get_non_accepting_states(dfa, accepting)

    old_eq = [non_accepting, accepting] # 0 eq
    while True:
        new_eq = partition(dfa, alphabet, old_eq)
        if old_eq == new_eq: break 
        old_eq = new_eq
    
    new_accepting = OrderedSet()
    for item in old_eq:
        for item2 in item:
            if item2 in accepting:
                new_accepting.add(item[0])

    return (old_eq, new_accepting)
    
# interpret json file and return nfa transitions, starting state, and accepting state
def json_to_nfa(file):
    json_data = ''
    with open(file, 'r') as json_file:
        json_data = json.load(json_file)

    starting_state = json_data['startingState']
    json_data.pop('startingState')

    accepting_state = ''
    for key, val in json_data.items():
        if key == 'startingState':
            continue
        if val['isTerminatingState']:
            accepting_state = key
        json_data[key].pop('isTerminatingState')
    return (json_data, starting_state, accepting_state)

# write dfa to json file
def dfa_to_json(dfa, accepting, file): 
    json_data = {}
    json_data['startingState'] = 'S0'
    
    for item in dfa:
        key = list(item.keys())[0]
        json_data['PHI' if key in ['PHI', -1] else f'S{key}'] = {'isTerminatingState': key in accepting}

        for letter, dest in item[key].items():
            json_data['PHI' if key in ['PHI', -1] else f'S{key}'].update({letter: f'{dest}' if dest == 'PHI' else f'S{dest}'})

    with open(file, 'w') as json_file:
        json.dump(json_data, json_file, indent = 2)
    return json_data

# get all unique values of all transition inputs from nfa, in order to construct the alphabet
def detect_alphabet(nfa):
    alphabet = OrderedSet()
    for val in nfa.values():
        alphabet.update([char for char in val])
    if 'EPSILON' in alphabet:
        alphabet.remove('EPSILON')
    return alphabet

def get_modified_state(key, min_dfa):
    for item in min_dfa:
        if key in item: return item[0]
    return -1   # NOT FOUND

def minimized_to_table(dfa, min_dfa, accepting, alphabet):
    minimized = []
    for st in dfa:
        key = list(st.keys())[0]
        modified_key = get_modified_state(key, min_dfa)
        new_st = {}
        new_st[modified_key] = { alpha: 'PHI' if get_modified_state(st[key][alpha], min_dfa) == -1 else get_modified_state(st[key][alpha], min_dfa) for alpha in alphabet }
        minimized.append(new_st)

    # remove duplicate
    dup = []
    for i in range(len(minimized) - 1):
        for j in range(i + 1, len(minimized)):
            if list(minimized[i].keys())[0] == list(minimized[j].keys())[0]:
                if j not in dup:
                    dup.append(j)
    
    new_minimized = []
    for i in range(len(minimized)):
        if i in dup: continue
        new_minimized.append(minimized[i])


    return new_minimized

def draw(json_data):
    dfa_dot = gv.Digraph()
    
    dfa_dot.node(json_data['startingState'].removeprefix('S'), json_data['startingState'], style='filled', color='lightgrey')
    for key, val in json_data.items():
        if key == 'startingState': continue
        for alpha, dest in val.items():
            if alpha == 'isTerminatingState' and dest:
                dfa_dot.node(key.removeprefix('S'), key, shape='doublecircle', style='filled', color='lightgreen')
            elif alpha == 'isTerminatingState' and not dest:
                dfa_dot.node(key.removeprefix('S'), key, shape='circle')
            else:
                dfa_dot.edge(key.removeprefix('S'), dest.removeprefix('S'), label = alpha)




    dfa_dot.render('dfa', view=True)


# python filename.py convert input_file_name.json  output_file_name.json

# main function, entry point of the application
def main():
    if sys.argv[1] != 'convert':
        error('the word "convert" is missing')
        return

    NFA_JSON_FILE = sys.argv[2]
    DFA_JSON_FILE = sys.argv[3]


    nfa, start_state, accepting_state = json_to_nfa(NFA_JSON_FILE)
    print(nfa, start_state, accepting_state, sep='\n')

    alphabet = detect_alphabet(nfa)
    dfa, starting, accepting = nfa_to_dfa(nfa, alphabet, start_state, accepting_state)
    print(dfa, starting, accepting, sep='\n')

    minimized_dfa, new_accepting = minimize_dfa(dfa, accepting, alphabet)
    minimized_dfa = minimized_to_table(dfa, minimized_dfa, accepting, alphabet)
    print(minimized_dfa)
    json_data = dfa_to_json(minimized_dfa, new_accepting, DFA_JSON_FILE)
    # dfa_to_json(dfa, accepting, DFA_JSON_FILE)
    draw(json_data)


if __name__ == '__main__':
    main()
