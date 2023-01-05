from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json

import math

from helpers.utils import NotImplemented

# This is a class for a generic Value Iteration agent
class ValueIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training 
    utilities: Dict[S, float] # The computed utilities
                                # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor
    
    # Given a state, compute its utility using the bellman equation
    # if the state is terminal, return 0
    def compute_bellman(self, state: S) -> float:
        if self.mdp.is_terminal(state): return 0

        # Using bellman equation provided in the document, 
        # for each action avalilble by the current state, the summation of bellman equation is calculated
        # to generate each utility for each action,
        # then the max utility is obtained and returned among all these action utilities
        max_utility = -math.inf
        for action in self.mdp.get_actions(state):
            utility = 0
            for possible_successor, probability in self.mdp.get_successor(state, action).items():
                utility += probability * (self.mdp.get_reward(state, action, possible_successor) + self.discount_factor * self.utilities[possible_successor])
            max_utility = max(max_utility, utility)
        return max_utility
            
    # Applies a single utility update
    # then returns True if the utilities has converged (the maximum utility change is less or equal the tolerance)
    # and False otherwise
    def update(self, tolerance: float = 0) -> bool:
        # To update bellman utility of each state is calculated and stored in bellman_utilities dict  
        bellman_utilities = {}
        for state in self.mdp.get_states():
            bellman_utilities[state] = self.compute_bellman(state)
        
        # Calculate the difference between bellman utility and current utility for each state,
        # then get the maximum difference
        max_change = max([abs(self.utilities[state] - bellman_utilities[state]) for state in self.mdp.get_states()])

        # Refill the utilities by the bellman_utilities
        for state in self.mdp.get_states():
            self.utilities[state] = bellman_utilities[state]

        # if convergence, return true
        return max_change <= tolerance
        

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None, tolerance: float = 0) -> int:
        iteration = 0
        while iterations is None or iteration < iterations:
            iteration += 1
            if self.update(tolerance):
                break
        return iteration
    
    # Given an environment and a state, return the best action as guided by the learned utilities and the MDP
    # If the state is terminal, return None
    def act(self, env: Environment[S, A], state: S) -> A:
        if self.mdp.is_terminal(state): return None
        
        max_utility = -math.inf
        max_utility_index = 0
        actions = self.mdp.get_actions(state)

        # For each action calculate the bellman utility as summation, based on the trained utilities of the successors.
        for index, action in enumerate(actions):  
            utility = 0 
            for possible_successor, probability in self.mdp.get_successor(state, action).items():  
                utility += probability * (self.mdp.get_reward(state, action, possible_successor) + self.discount_factor * self.utilities[possible_successor])           
            
            # Then get the action that has max utility and return it
            if utility > max_utility:
                max_utility = utility
                max_utility_index = index
        return actions[max_utility_index]
    
    # Save the utilities to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            utilities = {self.mdp.format_state(state): value for state, value in self.utilities.items()}
            json.dump(utilities, f, indent=2, sort_keys=True)
    
    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            utilities = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in utilities.items()}
