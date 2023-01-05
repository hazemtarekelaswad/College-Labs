from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

import math

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    is_terminal, terminal_vals = game.is_terminal(state)

    # Base cases:
    # if the current state is terminal state, return its tree value
    # if the maximum depth reaches 0, return its heuristic tree  value
    if is_terminal: return terminal_vals[0], None
    if max_depth == 0: return heuristic(game, state, 0), None
    
    # recursivly call the same function for every action avaliable for the current state 
    # and the save the returned values in a list of tuples, each tuple represents the tree value, and the action
    values_actions = [(minimax(game, game.get_successor(state, action), heuristic, max_depth - 1)[0], action) 
                        for action in game.get_actions(state)]

    # Eventually, get the max or min value-action pair according to the player's turn 
    
    return (max(values_actions, key = lambda k: k[0]) if game.get_turn(state) == 0 else min(values_actions, key = lambda k: k[0]))   
   

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1, alpha: int = -math.inf, beta: int = math.inf) -> Tuple[float, A]:
    is_terminal, terminal_vals = game.is_terminal(state)
    # Base cases:
    # if the current state is terminal state, return its tree value
    # if the maximum depth reaches 0, return its heuristic tree  value
    if is_terminal: return terminal_vals[0], None
    if max_depth == 0: return heuristic(game, state, 0), None
    
    # get successor states for each available action of the current state
    states_actions = [(game.get_successor(state, action), action) for action in game.get_actions(state)]

    # Based on the turn of max node or min node, you recursivly call the function for every
    # available action, then you minimize or maximize the value.
    if game.get_turn(state):
        min_value_action = (math.inf, None)
        for state, action in states_actions:
            value = alphabeta(game, state, heuristic, max_depth - 1, alpha, beta)[0]
            if value < min_value_action[0]: min_value_action = (value, action)

            # considering the two conditions of alpha and beta. they are used
            # to let alpha has the max value of max nodes and beta the min value of min nodes
            if min_value_action[0] <= alpha: return min_value_action
            if min_value_action[0] < beta: beta = min_value_action[0]
        return min_value_action

    max_value_action = (-math.inf, None)
    for state, action in states_actions:
        value = alphabeta(game, state, heuristic, max_depth - 1, alpha, beta)[0]
        if value > max_value_action[0]: max_value_action = (value, action)
        if max_value_action[0] >= beta: return max_value_action
        if max_value_action[0] > alpha: alpha = max_value_action[0]
    return max_value_action
        

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1, alpha: int = -math.inf, beta: int = math.inf) -> Tuple[float, A]:
    
    # Base cases:
    # if the current state is terminal state, return its tree value
    # if the maximum depth reaches 0, return its heuristic tree  value
    is_terminal, terminal_vals = game.is_terminal(state)

    if is_terminal: return terminal_vals[0], None
    if max_depth == 0: return heuristic(game, state, 0), None
    
    # This algorithm is exactly like alpha beta but it sorts the successor states from all available actions
    # descendingly based on the heuristic value of each of them. As the descending order of child nodes
    # will lead to more pruning and more optimization

    # Sort children descendingly based on the heuristic values
    heuristics_states_actions = sorted([(heuristic(game, game.get_successor(state, action), game.get_turn(state)), game.get_successor(state, action), action) 
                                        for action in game.get_actions(state)], key = lambda k: k[0], reverse = True)

    states_actions = [(state, action) for _, state, action in heuristics_states_actions]
    
    # Opponent
    if game.get_turn(state):

        min_value_action = (math.inf, None)
        for state, action in states_actions:
            value = alphabeta_with_move_ordering(game, state, heuristic, max_depth - 1, alpha, beta)[0]
            if value < min_value_action[0]: min_value_action = (value, action)
            if min_value_action[0] <= alpha: return min_value_action
            if min_value_action[0] < beta: beta = min_value_action[0]
        return min_value_action
            
    max_value_action = (-math.inf, None)
    for state, action in states_actions:
        value = alphabeta_with_move_ordering(game, state, heuristic, max_depth - 1, alpha, beta)[0]
        if value > max_value_action[0]: max_value_action = (value, action)
        if max_value_action[0] >= beta: return max_value_action
        if max_value_action[0] > alpha: alpha = max_value_action[0]
    return max_value_action

# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    # Base cases:
    # if the current state is terminal state, return its tree value
    # if the maximum depth reaches 0, return its heuristic tree  value
    is_terminal, terminal_vals = game.is_terminal(state)

    if is_terminal: return terminal_vals[0], None
    if max_depth == 0: return heuristic(game, state, 0), None

    # you get the all expectimax values of all successor states and then 
    # maximize the values if it is a max node, or average the values if it is not max node (chance node)
    values_actions = [(expectimax(game, game.get_successor(state, action), heuristic, max_depth - 1)[0], action) 
                        for action in game.get_actions(state)]

    return (max(values_actions, key = lambda k: k[0]) 
            if game.get_turn(state) == 0 
            else (sum(list(zip(*values_actions))[0]) / len(values_actions), None))