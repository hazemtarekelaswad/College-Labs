import math
from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json
import numpy as np

from helpers.utils import NotImplemented

# This is a class for a generic Policy Iteration agent
class PolicyIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training
    policy: Dict[S, A]
    utilities: Dict[S, float] # The computed utilities
                                # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        # This initial policy will contain the first available action for each state,
        # except for terminal states where the policy should return None.
        self.policy = {
            state: (None if self.mdp.is_terminal(state) else self.mdp.get_actions(state)[0])
            for state in self.mdp.get_states()
        }
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor
    
    # Given the utilities for the current policy, compute the new policy
    def update_policy(self):
        # for every non terminal state, calculate the policy
        for state in self.mdp.get_states():
            if self.mdp.is_terminal(state): continue

            max_utility = -math.inf
            max_utility_index = 0
            actions = self.mdp.get_actions(state)

            # For every action availble by this state, calculate the utility and then maximize this utility,
            # update the policy of this state with the action that has the max utility calculated
            for index, action in enumerate(actions):
                # This summation is used for policy imrovement step
                utility = sum([probability * (self.discount_factor * self.utilities[possible_successor] + self.mdp.get_reward(state, action, possible_successor)) 
                            for possible_successor, probability in self.mdp.get_successor(state, action).items()])
                if utility > max_utility:
                    max_utility = utility
                    max_utility_index = index
            self.policy[state] = actions[max_utility_index]
    
    # Given the current policy, compute the utilities for this policy
    # Hint: you can use numpy to solve the linear equations. We recommend that you use numpy.linalg.lstsq
    def update_utilities(self):
        
        # Filter out all terminal states to update utilities for only non-terminal states
        states = [state for state in self.mdp.get_states() if not self.mdp.is_terminal(state)]

        # state-index mapping, used for coefficint matrix filling
        state_index = {state: index for index, state in enumerate(states)}
        statesCount = len(states)

        # Initialize 2 matrices, one for constants (free terms), and the other for coefficints of the utilities (unknowns)
        intercepts = np.zeros((statesCount, 1), dtype=np.float64)
        coefficints = np.zeros((statesCount, statesCount), dtype=np.float64)

        for index, state in enumerate(states):

            # Calculate the free terms by getting the summation of the successors rewards multiplied by its corresponding probability
            intercepts[index] = sum([probability * self.mdp.get_reward(state, self.policy[state], possible_successor) 
                                for possible_successor, probability in self.mdp.get_successor(state, self.policy[state]).items()])
            
            # Calculate the coefficints by filling each row according to the current state with the 
            # summation of negative probability * discount factor of the corresponding successor
            coefficints[index, index] = 1
            for possible_successor, probability in self.mdp.get_successor(state, self.policy[state]).items():
                if self.mdp.is_terminal(possible_successor): continue
                coefficints[index, state_index[possible_successor]] -= probability * self.discount_factor
        
        # Solve linear equations based on coefficint matrix and intercpts
        utilities = np.linalg.lstsq(coefficints, intercepts)
        
        # Refill the utilities with the new utility values obtained from bellman equations above
        j = 0
        for i in range(len(self.mdp.get_states())):
            if self.mdp.is_terminal(self.mdp.get_states()[i]): continue
            self.utilities[self.mdp.get_states()[i]] = utilities[0][j, 0]
            j += 1

    # Applies a single utility update followed by a single policy update
    # then returns True if the policy has converged and False otherwise
    def update(self) -> bool:
        # copy this policy to check its convergence
        policy = self.policy.copy()
        self.update_utilities()
        self.update_policy()
        
        # Check for convergence and return True if the whole updated policy is equal to the prev one
        for state in self.mdp.get_states():
            if self.policy[state] != policy[state]: return False
        return True

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None) -> int:
        iteration = 0
        while iterations is None or iteration < iterations:
            iteration += 1
            if self.update():
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
            policy = {
                self.mdp.format_state(state): (None if action is None else self.mdp.format_action(action)) 
                for state, action in self.policy.items()
            }
            json.dump({
                "utilities": utilities,
                "policy": policy
            }, f, indent=2, sort_keys=True)
    
    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in data['utilities'].items()}
            self.policy = {
                self.mdp.parse_state(state): (None if action is None else self.mdp.parse_action(action)) 
                for state, action in data['policy'].items()
            }
