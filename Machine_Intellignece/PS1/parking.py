from typing import Any, Dict, Set, Tuple, List
from problem import Problem
from mathutils import Direction, Point
from helpers import utils

ParkingState = Tuple[Point]
# An action of the parking problem is a tuple containing an index 'i' and a direction 'd' where car 'i' should move in the direction 'd'.
ParkingAction = Tuple[int, Direction]

# This is the implementation of the parking problem
class ParkingProblem(Problem[ParkingState, ParkingAction]):
    passages: Set[Point]    # A set of points which indicate where a car can be (in other words, every position except walls).
    cars: Tuple[Point]      # A tuple of points where state[i] is the position of car 'i'. 
    slots: Dict[Point, int] # A dictionary which indicate the index of the parking slot (if it is 'i' then it is the lot of car 'i') for every position.
                            # if a position does not contain a parking slot, it will not be in this dictionary.
    width: int              # The width of the parking lot.
    height: int             # The height of the parking lot.

    # This function should return the initial state
    def get_initial_state(self) -> ParkingState:
        # The state is defined by the positions of each car in the grid  
        return self.cars
    
    # This function should return True if the given state is a goal. Otherwise, it should return False.
    def is_goal(self, state: ParkingState) -> bool:
        # The goal is defined when all cars are in the designated parking slots
        # So this loop checks if any of the cars is not in its designated slot, then it will return false
        for pos, car in self.slots.items():
            if state[car] != pos: return False
        return True


    
    # This function returns a list of all the possible actions that can be applied to the given state
    def get_actions(self, state: ParkingState) -> List[ParkingAction]:
        # Possible actions for each car is determined by two cases, if the position it wants to go to
        # (LEFT, UP, RIGHT, DOWN), is in passages and is not in state (to avoid collisions with other cars).
        # So, for each car, check for all four directions if they meet the cases or not to be considered as
        # available actions

        all_actions: List[ParkingAction] = []
        for index, car_pos in enumerate(state):
            if Point(car_pos.x - 1, car_pos.y) in self.passages and Point(car_pos.x - 1, car_pos.y) not in state:
                all_actions.append((index, Direction.LEFT))
            if Point(car_pos.x, car_pos.y - 1) in self.passages and Point(car_pos.x, car_pos.y - 1) not in state:
                all_actions.append((index, Direction.UP))
            if Point(car_pos.x + 1, car_pos.y) in self.passages and Point(car_pos.x + 1, car_pos.y) not in state:
                all_actions.append((index, Direction.RIGHT))
            if Point(car_pos.x, car_pos.y + 1) in self.passages and Point(car_pos.x, car_pos.y + 1) not in state:
                all_actions.append((index, Direction.DOWN))
        return all_actions
    
    
    # This function returns a new state which is the result of applying the given action to the given state
    def get_successor(self, state: ParkingState, action: ParkingAction) -> ParkingState:
        # Check the direction in the action passed and then, get the new car's position accordingly
        # the car itself is determined from action[0]

        change = None;
        if action[1] == Direction.LEFT:
            change = Point(state[action[0]].x - 1, state[action[0]].y)
        elif action[1] == Direction.UP:
            change = Point(state[action[0]].x, state[action[0]].y - 1)
        elif action[1] == Direction.RIGHT:
            change = Point(state[action[0]].x + 1, state[action[0]].y)
        else: # if DOWN
            change = Point(state[action[0]].x, state[action[0]].y + 1)
        
        # Create a new state that has all car position are the same but change only the car in action[0] 
        # to be the point determined above
        new_state = tuple(change if i == action[0] else car for i, car in enumerate(state))
        return new_state
    
    # This function returns the cost of applying the given action to the given state
    def get_cost(self, state: ParkingState, action: ParkingAction) -> float:
        # Check the direction in the action passed and then, get the new car's position accordingly
        # the car itself is determined from action[0]

        change = None;
        if action[1] == Direction.LEFT:
            change = Point(state[action[0]].x - 1, state[action[0]].y)
        elif action[1] == Direction.UP:
            change = Point(state[action[0]].x, state[action[0]].y - 1)
        elif action[1] == Direction.RIGHT:
            change = Point(state[action[0]].x + 1, state[action[0]].y)
        else: # if DOWN
            change = Point(state[action[0]].x, state[action[0]].y + 1)
        
        # The cost is 1 and add another 100 if the new position is one of the parking slots
        # and at the same time, not the parking slot of the mean car
        cost = 1.0
        if change in self.slots and self.slots[change] != action[0]:
            cost += 100.0
        return cost
       

     # Read a parking problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> 'ParkingProblem':
        passages =  set()
        cars, slots = {}, {}
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "#":
                    passages.add(Point(x, y))
                    if char == '.':
                        pass
                    elif char in "ABCDEFGHIJ":
                        cars[ord(char) - ord('A')] = Point(x, y)
                    elif char in "0123456789":
                        slots[int(char)] = Point(x, y)
        problem = ParkingProblem()
        problem.passages = passages
        problem.cars = tuple(cars[i] for i in range(len(cars)))
        problem.slots = {position:index for index, position in slots.items()}
        problem.width = width
        problem.height = height
        return problem

    # Read a parking problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'ParkingProblem':
        with open(path, 'r') as f:
            return ParkingProblem.from_text(f.read())
    
