# agent.py
import random

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