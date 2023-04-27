"""Defines the enemy AI used in the game."""
import math
import pymunk
from pymunk import Vec2d
from collections import deque  # , defaultdict # Also unused.
from typing import Any, Callable, List
import gameobjects

# 3 degrees, a bit more than we can turn each tick.
MIN_ANGLE_DIF = math.radians(2)


def angle_between_vectors(vec1, vec2):
    """
    Return the angle between two vectors.

    Since Vec2d operates in a cartesian coordinate space, we have to convert
    the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """Return difference between angles, without multiples of 2pi."""
    return (angle1 - angle2) % (2 * math.pi)


class AI:
    """
    A simple AI.

    Finds the shortest path to the target using a breadth first search.
    Also capable of shooting other tanks and or woodboxes.
    """

    def __init__(self, tank, objects, tanks_list, space, current_map):
        """Initialize an instance of AI."""
        self.tank = tank
        self.objects = objects
        self.tanks_list = tanks_list
        self.space = space
        self.current_map = current_map
        self.flag = None
        self.MAX_X = current_map.width - 1
        self.MAX_Y = current_map.height - 1

        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()
        self.path = deque()

    def update_grid_pos(self):
        """
        Update the AI's position on the grid.

        This should only be called in the beginning, or at the end of a
        move_cycle.
        """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """
        Decide what to do.

        Moves to next state in the move cycle.
        """
        next(self.move_cycle)

    def maybe_shoot(self, gs):
        """
        Make a raycast query in front of the tank.

        If another tank or a wooden box is found, then shoot.
        """
        start = (self.tank.body.position
                 + Vec2d(0, 0.4).rotated(self.tank.body.angle))

        end = self.tank.body.position + (Vec2d(0, 1)
                                         .rotated(self.tank.body.angle)
                                         * (self.MAX_X**2))

        obj_looked_at = self.tank.space.segment_query_first(
            start,
            end,
            0,
            pymunk.ShapeFilter()
        )

        if obj_looked_at and obj_looked_at.shape.collision_type in {2, 3}:
            bullet = self.tank.shoot(gs)
            self.tank.guided_bullet = None
            # Increase speed for AI bullets.
            if bullet:
                bullet.body.velocity *= 1.3
            return bullet

    def get_angle(self, next_coord):
        """Get angle to go next."""
        diff = (self.grid_pos - next_coord + Vec2d(0.5, 0.5)).int_tuple
        # Up
        if diff == (0, 1):
            return math.radians(180)
        # Down
        elif diff == (0, -1):
            return 0
        # Left
        elif diff == (1, 0):
            return math.radians(90)
        # Right
        elif diff == (-1, 0):
            return math.radians(270)
        else:
            raise ValueError("Incorrect position.")

    def get_angle_difference(self, target_coord):
        """
        Return position that the tank should face to get to the target.

        Returns periodic difference between the tank angle and the angle of the
        difference vector between the tank position and the target position.
        """
        return periodic_difference_of_angles(
                self.tank.body.angle,
                angle_between_vectors(
                    self.tank.body.position,
                    target_coord)
                )

    def get_next_centered_coord(self, coord: Vec2d) -> Vec2d:
        """Return a centered vector on the next coordinate."""
        if not self.path or coord not in self.get_tile_neighbours(coord):
            self.path = self.find_shortest_path()

        return self.path.popleft() + Vec2d(0.5, 0.5)

    def move_cycle_gen(self):
        """
        Yield next step.

        A generator that iteratively goes through all the required steps to
        move to our goal.
        """
        while True:

            self.update_grid_pos()
            next_coord = self.get_next_centered_coord(self.grid_pos)
            yield

            # Adjust angle
            if abs(self.get_angle_difference(next_coord)) > math.pi/10:
                while (abs(angle_difference
                           := self.get_angle_difference(next_coord))
                       > MIN_ANGLE_DIF):

                    self.tank.stop_moving()

                    if (0 <= angle_difference <= math.pi):
                        self.tank.turn_left()
                    elif (math.pi <= angle_difference <= 2 * math.pi):
                        self.tank.turn_right()
                    else:
                        self.tank.turn_right()

                    yield

                self.tank.stop_turning()
                yield

            # Adjust position
            distance = self.tank.body.position.get_distance(next_coord)
            previous, current = distance, distance
            while previous >= current and current > 0.1:
                self.tank.accelerate()
                previous = current
                current = self.tank.body.position.get_distance(next_coord)

                # Check for respawn or stuck AI.
                if current > 2:
                    break
                yield

    def find_shortest_path(self):
        """
        Find the shortest path to the goal.

        A simple Breadth First Search using integer coordinates as our nodes.
        Edges are calculated as we go, using an external function.
        """
        goal = self.get_target_tile()

        def heuristic(v):
            distance = goal.get_dist_sqrd(v)

            if self.current_map.boxAt(v.x, v.y) == 3:
                return distance + 9000
            else:
                return distance

        if path := reconstruct(goal, A_star(
                goal,
                [],
                [(self.grid_pos, heuristic(self.grid_pos))],
                self.get_tile_neighbours,
                heuristic)):
            return deque(path)

        else:
            # Prevents pop from empty deque error.
            return deque([self.grid_pos])

    def get_target_tile(self):
        """
        Decide the position of the target.

        Returns position of the flag if we don't have it. If we do have the
        flag, return the position of our home base.
        """
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.get_flag()  # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """
        Set self.flag to the instance in the game and return it.

        This has to be called to get the flag, since we don't know
        where it is when the AI object is initialized.
        """
        if self.flag is None:
            # Find the flag in the game objects list.
            for obj in self.objects:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """
        Return a integer-rounded version of the current position.

        Convert and return the float position of our tank to an integer
        position.
        """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbours(self, coord_vec: Vec2d):
        """
        Return all bordering grid squares of the input coordinate.

        A bordering square is only considered accessible if it is grass or a
        wooden box.
        """
        coord = self.get_tile_of_position(coord_vec)

        left = coord - Vec2d(1, 0)
        right = coord + Vec2d(1, 0)
        up = coord - Vec2d(0, 1)
        down = coord + Vec2d(0, 1)

        return [i for i in [left, right, up, down]
                if 0 <= i.x <= self.MAX_X
                and 0 <= i.y <= self.MAX_Y
                and self.current_map.boxAt(i.x, i.y) in {0, 2, 3}]


def A_star(goal: tuple,
           visited: list,
           queue: list,
           nextfn: Callable[[Any], List[Any]],
           heuristic: Callable[[Any], Any]
           ) -> dict:
    """Search for shortest path to a vertex in a graph."""
    if not queue or queue[0] == goal:
        return {}
    else:
        next_vertices = [pos_tuple for v in nextfn(queue[0][0])
                         if (pos_tuple := (v, heuristic(v))) not in visited
                         and pos_tuple not in queue]

        return merge_dicts({v[0]: queue[0][0] for v in next_vertices},
                           A_star(goal,
                                  visited + queue[:1],
                                  sorted(queue[1:] + next_vertices,
                                         key=lambda x: x[1]),
                                  nextfn,
                                  heuristic
                                  ))


def reconstruct(goal: Any, traversal: dict) -> list:
    """Reconstruct the shortest to a goal path from a BFS traversal."""
    if goal not in traversal:
        return []
    else:
        return reconstruct(traversal[goal], traversal) + [goal]


def merge_dicts(d1: dict, d2: dict) -> dict:
    """Return the result of d1.update(d2) dictionaries without altering d1."""
    temp = d1.copy()
    temp.update(d2)
    return temp
