# agent.py
import random
from collections import deque
import heapq
import math

class SearchAgent:
    """Offline graph-search agent for navigating a static grid."""

    def __init__(self):
        self.reached = set()
        self.plan = []
        self.active_algo = 'BFS'

    def manhattan_distance(self, pos, goal) -> int:
        x1, y1 = pos
        x2, y2 = goal
        hn = abs(x1-x2) + abs(y2-y1)
        return hn

    def euclidean_distance(self, pos, goal) -> int:
        x1, y1 = pos
        x2, y2 = goal
        hn = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return hn

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        walls = set(walls)
        pq = []
        reached_states = set()

        if heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        start_h = heuristic(start_pos, goal_pos)
        heapq.heappush(pq, (start_h, 0, start_pos, []))

        while pq:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(pq)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            for action, next_pos in self._neighbors(current_pos, walls, grid_size):
                if next_pos not in reached_states:
                    new_g_cost = g_cost + 1
                    new_h_cost = heuristic(next_pos, goal_pos)
                    new_f_cost = new_g_cost + new_h_cost
                    heapq.heappush(
                        pq,
                        (new_f_cost, new_g_cost, next_pos, path_taken + [action]),
                    )

        return None


    def _neighbors(self, position, walls, grid_size):
        x, y = position
        width, height = grid_size

        possible_moves = [
            ("Up", (x, y + 1)),
            ("Right", (x + 1, y)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
        ]
        return [
            (action, coordinate)
            for action, coordinate in possible_moves
            if 0 <= coordinate[0] < width
            and 0 <= coordinate[1] < height
            and coordinate not in walls
        ]

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = set(walls)
        frontier = deque([(start_pos, [])])
        self.reached = {start_pos}

        while frontier:
            position, path = frontier.popleft()
            if position == goal_pos:
                return path

            for action, next_position in self._neighbors(position, walls, grid_size):
                if next_position not in self.reached:
                    self.reached.add(next_position)
                    frontier.append((next_position, path + [action]))

        return None


    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = set(walls)
        frontier = [(start_pos, [])]
        self.reached = {start_pos}

        while frontier:
            position, path = frontier.pop()
            if position == goal_pos:
                return path

            for action, next_position in reversed(self._neighbors(position, walls, grid_size)):
                if next_position not in self.reached:
                    self.reached.add(next_position)
                    frontier.append((next_position, path + [action]))

        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = set(walls)
        frontier = [(0, 0, start_pos, [])]
        self.reached = {start_pos}
        counter = 1

        while frontier:
            cost, _, position, path = heapq.heappop(frontier)
            if position == goal_pos:
                return path

            for action, next_position in self._neighbors(position, walls, grid_size):
                if next_position not in self.reached:
                    self.reached.add(next_position)
                    heapq.heappush(
                        frontier,
                        (cost + 1, counter, next_position, path + [action]),
                    )
                    counter += 1

        return None

    def sense_and_act(self, percept):
        if not self.plan:
            start_pos = tuple(percept['agent_pos'])
            food_positions = [tuple(food) for food in percept['all_food']]

            if not food_positions:
                return "Stay"

            closest_food = min(
                food_positions,
                key=lambda food: abs(food[0] - start_pos[0]) + abs(food[1] - start_pos[1]),
            )

            if self.active_algo == "BFS":
                self.plan = self.bfs_search(start_pos, closest_food, percept['walls'], percept['grid_size'])
            elif self.active_algo == "DFS":
                self.plan = self.dfs_search(start_pos, closest_food, percept['walls'], percept['grid_size'])
            elif self.active_algo == "AStar":
                self.plan = self.astar_search(
                    start_pos,
                    closest_food,
                    percept['walls'],
                    percept['grid_size'],
                )
            else:
                self.plan = self.ucs_search(start_pos, closest_food, percept['walls'], percept['grid_size'])

            if self.plan is None:
                self.plan = []

        return self.plan.pop(0) if self.plan else "Stay"

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict):
        if percept["food_here"]:
            return "Eat"
        if percept["wall_ahead"]:
            return "Left"
        else:
            return "Up"



class ModelBasedAgent:
    def __init__(self):
        self.visited_cells = set()
        self.last_action = None
        self.current_percept = None
        
        self.directions = ["Right", "Down", "Left", "Up"]
        self.face_direction = "Right"
        self.current_pos = (0, 0)
        
        self.visited_cells.add(self.current_pos)

    def sense_and_act(self, percept: dict) -> str:
        self.current_percept = percept
        
        if self.last_action == "turn_left":
            curr_idx = self.directions.index(self.face_direction)
            self.face_direction = self.directions[(curr_idx - 1) % 4]
            
        elif self.last_action == "turn_right":
            curr_idx = self.directions.index(self.face_direction)
            self.face_direction = self.directions[(curr_idx + 1) % 4]
            
        elif self.last_action == "move_forward":
            x, y = self.current_pos
            if self.face_direction == "Right":  self.current_pos = (x + 1, y)
            elif self.face_direction == "Down": self.current_pos = (x, y + 1)
            elif self.face_direction == "Left": self.current_pos = (x - 1, y)
            elif self.face_direction == "Up":   self.current_pos = (x, y - 1)
            
            self.visited_cells.add(self.current_pos)

        if percept.get("food_here"):
            action = "Eat"
            
        elif not percept.get("wall_ahead"):
            x, y = self.current_pos
            
            # Calculate where moving forward would take us
            if self.face_direction == "Right":  next_pos = (x + 1, y)
            elif self.face_direction == "Down": next_pos = (x, y + 1)
            elif self.face_direction == "Left": next_pos = (x - 1, y)
            elif self.face_direction == "Up":   next_pos = (x, y - 1)

            if next_pos not in self.visited_cells:
                action = "move_forward"
            else:
                action = "turn_right"
                
        else:
            action = "turn_right" if self.last_action == "turn_left" else "turn_left"

        self.last_action = action
        return action