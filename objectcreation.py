"""Creates instances of game objects, populates list of game objects."""
import gameobjects
import pymunk


def create_everything(gs):
    """Create initial gameobjectslist, and pymunk space."""
    space = pymunk.Space()
    space.gravity = (0.0,  0.0)  # Can be used for wind later...
    space.damping = 0.1  # Adds friction to the ground for all objects.

    _create_border(space, gs.current_map)

    boxes = [gameobjects.get_box_with_type(x, y, box_type, space, gs)
             for x in range(gs.current_map.width)
             for y in range(gs.current_map.height)
             if (box_type := gs.current_map.boxAt(x, y)) != 0]

    bases = [gameobjects.GameVisibleObject(x, y, sprite)
             for ((x, y, _), sprite)
             in zip(gs.current_map.start_positions, gs.sprites.bases)]

    tanks = [gameobjects.Tank(x, y, orientation, sprite, space, gs)
             for ((x, y, orientation), sprite)
             in zip(gs.current_map.start_positions, gs.sprites.tanks)]

    flag = gameobjects.Flag(gs)

    return (flag, tanks, boxes + bases + tanks + [flag], space)


def _create_border(space, current_map):
    """Create borders and add them to space."""
    static_body = space.static_body
    space.add(*[
        pymunk.Segment(static_body, (0, 0), (0, current_map.height), 0),
        pymunk.Segment(static_body, (0, 0), (current_map.width, 0), 0),
        pymunk.Segment(static_body,
                       (current_map.width, current_map.height),
                       (current_map.width, 0), 0),
        pymunk.Segment(static_body,
                       (current_map.width, current_map.height),
                       (0, current_map.height), 0)
    ])
