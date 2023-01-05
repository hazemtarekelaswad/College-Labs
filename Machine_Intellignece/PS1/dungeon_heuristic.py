from dungeon import DungeonProblem, DungeonState
from mathutils import Direction, Point, euclidean_distance, manhattan_distance
from helpers import utils

# This heuristic returns the distance between the player and the exit as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: DungeonProblem, state: DungeonState):
    return euclidean_distance(state.player, problem.layout.exit)

#################################################################################################
# On my computer, running speed_test.py takes ~4 seconds
#################################################################################################

# Graph class is used to hold edges between coins and their distances
class Graph:
    # Constructor holds number of nodes (coins), and list of tuples 
    # that contains edges (2 points and the distance between them)
    def __init__(self, nodes_count):
        self.nodes_count = nodes_count
        self.graph = []

    # add edge to the graph list
    def add_edge(self, first_node, second_node, cost):
        self.graph.append((first_node, second_node, cost))

    # utility function that finds the root of a subtree that contain the passed node
    def find_root(self, roots, node_index):
        while roots[node_index] != node_index:
            node_index = roots[node_index]
        return node_index

    # utility function that merge two subtrees that each of which has its passed node
    def merge_roots(self, roots, tree_sizes, node1, node2):
        root1 = self.find_root(roots, node1)
        root2 = self.find_root(roots, node2)

        # Let root1 be the root2 or vice versa according to the less size
        if tree_sizes[root1] == tree_sizes[root2]:
            roots[root2] = root1
            tree_sizes[root1] += 1
        elif tree_sizes[root1] < tree_sizes[root2]:
            roots[root1] = root2
        else: roots[root2] = root1
       
    # Create minimum spanning tree using Krausal's algorithm and returns list of edges
    # selected as MST
    def to_mst(self):

        # Sort the graph edges based on their costs ascendigally
        self.graph = sorted(self.graph, key = lambda element: element[2])
        
        # Each node initially has a root of itself (as a subtree of one node)
        roots = list(range(self.nodes_count))
        tree_sizes = [0] * self.nodes_count

        # To hold the constructed MST 
        mst_edges = []
        node_index = 0
        edge_index = 0

        # For every edge sorted by cost, append it to the mst edges only if the two connected nodes
        # are in different subtrees and then merge these subtrees. 
        # But if they are in the same subtree, it means they are already added to the mst list
        while edge_index < self.nodes_count - 1:
            edge = self.graph[node_index]

            root1, root2 = (self.find_root(roots, edge[0]), self.find_root(roots, edge[1]))

            if root1 != root2:
                mst_edges.append(edge)
                self.merge_roots(roots, tree_sizes, root1, root2)
                edge_index += 1
           
            node_index += 1
        return mst_edges

# Take a point in the grid and return a list of its available moves, which are 
# the points in the four directions except ones that are not walkable 
def get_actions(problem: DungeonProblem, pos: Point):
    actions = []
    if pos + Direction.UP.to_vector() in problem.layout.walkable: actions.append(Direction.UP)
    if pos + Direction.RIGHT.to_vector() in problem.layout.walkable: actions.append(Direction.RIGHT)
    if pos + Direction.DOWN.to_vector() in problem.layout.walkable: actions.append(Direction.DOWN)
    if pos + Direction.LEFT.to_vector() in problem.layout.walkable: actions.append(Direction.LEFT)
    return actions

# Returns the path length as a distance between two given points by 
# statrting at point1 and goaling to point2 using breadth first search algorithm
def get_cost(problem: DungeonProblem, pos1: Point, pos2: Point):
    frontier = [(pos1, [])]
    explored = set()

    while True:
        if len(frontier) == 0: return None

        state_actions = frontier.pop(0)
        if state_actions[0] in explored: continue
        explored.add(state_actions[0])
        if state_actions[0] == pos2: return len(state_actions[1])

        for action in get_actions(problem, state_actions[0]):
            successor = action.to_vector() + state_actions[0]
            for state, _ in frontier:
                if successor == state: break
            else: 
                frontier.append((successor, state_actions[1] + [action]))

# Take a state (coins positions) and create a graph in which each coin is a node, and
# an edge, weighted as the distance (got from get_cost() function above), is created to connect each coin to all other coins
def to_graph(problem: DungeonProblem, state: DungeonState) -> Graph:
    # dictionary where coin position is a key and index is a value 
    # in order to add the index as graph node value instead of the position itself
    coin_indexes = { coin: index for index, coin in enumerate(state.remaining_coins) }
    graph = Graph(len(state.remaining_coins))

    # Loop over each coin and all other coins to calculate distances and add them to the graph
    for curr_coin in state.remaining_coins:
        for other_coin in state.remaining_coins:
            if curr_coin == other_coin: continue
            cost = problem.cache().get((curr_coin, other_coin), None) or problem.cache().get((other_coin, curr_coin), None)
            if not cost: 
                cost = get_cost(problem, curr_coin, other_coin)
                problem.cache()[(curr_coin, other_coin)] = cost
                problem.cache()[(other_coin, curr_coin)] = cost

            graph.add_edge(coin_indexes[curr_coin], coin_indexes[other_coin], cost)

    return graph


def strong_heuristic(problem: DungeonProblem, state: DungeonState) -> float:

    # If there is no coins in the grid, return the manhattan distance between player and exit positions
    if not state.remaining_coins: return manhattan_distance(state.player, problem.layout.exit)

    # Calculate the distance between each coin and the player position, 
    # then get the minimum distance among them. 
    # NOTE: distances are saved in the cache and used if they are previously computed, 
    # because get_cost() fucntion is computationally expensive

    distances = []
    for coin_pos in state.remaining_coins:
        if (coin_pos, state.player) in problem.cache():
            distances.append(problem.cache()[(coin_pos, state.player)])
            continue
        distance = get_cost(problem, coin_pos, state.player)
        problem.cache()[(coin_pos, state.player)] = distance
        problem.cache()[(state.player, coin_pos)] = distance
        distances.append(distance)

    player_coin_dist = min(distances)

    # Calculate the distance between each coin and the player exit position, 
    # then get the minimum distance among them. 

    # NOTE: distances are saved in the cache and used if they are previously computed, 
    # because get_cost() fucntion is computationally expensive

    distances = []
    for coin_pos in state.remaining_coins:
        if (coin_pos, problem.layout.exit) in problem.cache():
            distances.append(problem.cache()[(coin_pos, problem.layout.exit)])
            continue
        distance = get_cost(problem, coin_pos, problem.layout.exit)
        problem.cache()[(coin_pos, problem.layout.exit)] = distance
        problem.cache()[(problem.layout.exit, coin_pos)] = distance
        distances.append(distance)

    exit_coin_dist = min(distances)

    # Construct a graph from the current state given, get its MST, then add up all edge costs
    # and consider this sum as the estimated cost to traverse all coins in the grid
    # Finally, the heuristic value is the 
    # minimum player -> coin distance + minimum exit -> coin distance + MST cost 

    # NOTE: state is saved in cache and used if the MST cost of this state is already computed
    
    mst_cost = 0.0
    saved_state = problem.cache().get('state', None)
    if saved_state and state.remaining_coins == saved_state[0]:
        mst_cost = saved_state[1]
    else:
        mst_list = to_graph(problem, state).to_mst()
        mst_cost = sum([cost for _, _, cost in mst_list])

        problem.cache()['state'] = (state.remaining_coins, mst_cost)

    return player_coin_dist + mst_cost + exit_coin_dist





