from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers import utils

from queue import PriorityQueue
# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # Frontier: queue of tuples, each tuple has a state and a list of actions that connects initial state to that state
    # Explored: is a set of states that are already explored
    frontier = [(initial_state, [])]
    explored = set()

    while True:
        # The goal doesn't exist only if the frontier gets emptied
        if len(frontier) == 0: return None

        # dequeue a state, check if it is goal to return it, or add it as explored
        state_actions = frontier.pop(0)
        if state_actions[0] in explored: continue
        explored.add(state_actions[0])
        if problem.is_goal(state_actions[0]): return state_actions[1]

        # Loop over each action to get successors, and for each successor state, 
        # either enqueue it into the frontier discard it if it is in explored set or in the frontier itself 
        for action in problem.get_actions(state_actions[0]):
            successor = problem.get_successor(state_actions[0], action)
            for state, _ in frontier:
                if successor == state: break
            else: 
                # To add a state into the frontier, first copy the state, actions pair 
                # then append the action that leads to this state into the list of actions
                # and finally append this new state actions pair intro thr frontier
                # So that, each entry in frontier is a pair of state and actions taken the leads to this state

                frontier.append((successor, state_actions[1] + [action]))
         

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:

    # Frontier: stack of tuples, each tuple has a state and a list of actions that connects initial state to that state
    # Explored: is a set of states that are already explored
    frontier = [(initial_state, [])]
    explored = set()

    while True:
        # The goal doesn't exist only if the frontier gets emptied
        if len(frontier) == 0: return None

        # pop a state from the stack, add it to explored set if it hasn't been already checked, 
        # then check if it is goal, return its path
        state_actions = frontier.pop()
        if state_actions[0] in explored: continue
        explored.add(state_actions[0])
        if problem.is_goal(state_actions[0]): return state_actions[1]

        # Loop over each action to get successors, and for each successor state, push it into the stack
        for action in problem.get_actions(state_actions[0]):
            successor = problem.get_successor(state_actions[0], action)
            # To add a state into the frontier, first copy the state, actions pair 
            # then append the action that leads to this state into the list of actions
            # and finally append this new state actions pair intro thr frontier, this done be concatentaion of actions.
            # So that, each entry in frontier is a pair of state and actions taken the leads to this state

            frontier.append((successor, state_actions[1] + [action]))
    
def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # Frontier: priority queue of tuples, each tuple has a cost, state and a list of actions that connects initial state to that state
    # The counter is just added to handle stability of the pri queue
    # Explored: is a set of states that are already explored
    frontier = PriorityQueue()
    counter = 0 # to handle stability of the priority queue
    frontier.put(((0, counter), initial_state, []))
    explored = set()

    while True:
        # The goal doesn't exist only if the frontier gets emptied
        if frontier.empty(): return None

        # dequeue a state from the queue, add it to explored set if it hasn't been already checked, 
        # then check if it is goal, return its path
        pri_state_actions = frontier.get()
        if pri_state_actions[1] in explored: continue
        explored.add(pri_state_actions[1])
        if problem.is_goal(pri_state_actions[1]): return pri_state_actions[2]

        # Loop over each action to get successors, and for each successor state, 
        # push it into the frontier
        for action in problem.get_actions(pri_state_actions[1]):
            successor = problem.get_successor(pri_state_actions[1], action)

            # To add a state into the frontier, first copy the state, actions 
            # then append the action that leads to this state into the list of actions
            # and append this new state actions pair intro thr frontier, this done be concatentaion of actions.
            # finally, sum the cost of the current action to the cumulative cost that leads to the current state and put that total
            # as a first entry to the pri queue
            # So that, each entry in frontier is a tuple of cumulative cost, state and actions taken the leads to this state

            cost = problem.get_cost(pri_state_actions[1], action)
            counter += 1
            frontier.put(((pri_state_actions[0][0] + cost, counter), successor, pri_state_actions[2] + [action]))

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    # Frontier: priority queue of tuples, each tuple has a (heuristic value + cumulative cost), cumulative cost, state and a list of actions that connects initial state to that state
    # The counter is just added to handle stability of the pri queue
    # Explored: is a set of states that are already explored
    frontier = PriorityQueue()
    counter = 0 # to handle stability of the priority queue
    frontier.put(((heuristic(problem, initial_state), counter, 0), initial_state, []))
    explored = set()

    while True:
        # The goal doesn't exist only if the frontier gets emptied
        if frontier.empty(): return None

        # dequeue a state from the queue, add it to explored set if it hasn't been already checked, 
        # then check if it is goal, return its path
        pri_state_actions = frontier.get()
        if pri_state_actions[1] in explored: continue
        explored.add(pri_state_actions[1])
        if problem.is_goal(pri_state_actions[1]): return pri_state_actions[2]

        # Loop over each action to get successors, and for each successor state, 
        # push it into the frontier
        for action in problem.get_actions(pri_state_actions[1]):
            successor = problem.get_successor(pri_state_actions[1], action)

            # To add a state into the frontier, first copy the f = g + h, g, state, actions 
            # then append the action that leads to this state into the list of actions
            # and append this new state actions pair intro thr frontier, this done be concatentaion of actions.
            # finally, sum the cum cost to the heuristic value (f) and put first then
            # get the sum of the cost of the current action to the cumulative cost that leads to the current state and put that total
            # as a second entry to the pri queue
            # So that, each entry in frontier is a tuple of cumulative cost, state and actions taken the leads to this state

            cum_cost = pri_state_actions[0][2] + problem.get_cost(pri_state_actions[1], action)
            heuristic_cost = heuristic(problem, successor)

            counter += 1
            frontier.put(((cum_cost + heuristic_cost, counter, cum_cost), successor, pri_state_actions[2] + [action]))

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    # Frontier: priority queue of tuples, each tuple has a heuristic value, state and a list of actions that connects initial state to that state
    # The counter is just added to handle stability of the pri queue
    # Explored: is a set of states that are already explored
    frontier = PriorityQueue()
    counter = 0 # to handle stability of the priority queue
    frontier.put(((heuristic(problem, initial_state), counter), initial_state, []))
    explored = set()

    while True:
        # The goal doesn't exist only if the frontier gets emptied
        if frontier.empty(): return None

        # dequeue a state from the queue, add it to explored set if it hasn't been already checked, 
        # then check if it is goal, return its path
        pri_state_actions = frontier.get()
        if pri_state_actions[1] in explored: continue
        explored.add(pri_state_actions[1])
        if problem.is_goal(pri_state_actions[1]): return pri_state_actions[2]

        # Loop over each action to get successors, and for each successor state, 
        # push it into the frontier
        for action in problem.get_actions(pri_state_actions[1]):
            successor = problem.get_successor(pri_state_actions[1], action)
            heuristic_cost = heuristic(problem, successor)

            # To add a state into the frontier, first copy the h, state, actions 
            # then append the action that leads to this state into the list of actions
            # and append this new state actions pair intro thr frontier, this done be concatentaion of actions.
            # finally, put heuristic value as a first entry.
            # So that, each entry in frontier is a tuple of cumulative cost, state and actions taken the leads to this state

            counter += 1
            frontier.put(((heuristic_cost, counter), successor, pri_state_actions[2] + [action]))