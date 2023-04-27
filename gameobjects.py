"""Defines all object classes in the game."""
import pygame
import pymunk
import math
from pygame import mixer


def physics_to_display(x, gs):
    """Convert coordinates in the physics engine into display coordinates."""
    return x * gs.settings.TILE_SIZE


class GameObject:
    """
    Mostly handles visual aspects (pygame) of an object.

    Subclasses need to implement two functions:
    - screen_position    that will return the position of the object on the
      screen
    - screen_orientation that will return how much the object is rotated on the
      screen (in degrees).
    """

    def __init__(self, sprite):
        """Initiate an instance of GameObject."""
        self.sprite = sprite

    def update(self, gs):
        """
        Update the current state (after a tick) of the object.

        NOTE: Placeholder, supposed to be implemented in a subclass.
        """
        return

    def post_update(self):
        """
        Make updates that depend on other objects than itself.

        NOTE: Should be implemented in a subclass.
        """
        return

    def update_screen(self, screen, gs):
        """
        Update the visual part of the game.

        NOTE: Should NOT need to be changed by a subclass.
        """
        sprite = self.sprite

        # Get the position of the object (pygame coordinates)
        p = self.screen_position(gs)
        # Rotate the sprite using the rotation of the object
        sprite = pygame.transform.rotate(sprite, self.screen_orientation())

        # The position of the screen correspond to the center of the object,
        # but the function screen.blit expect to receive the top left corner
        # as argument, so we need to adjust the position p with an offset
        # which is the vector between the center of the sprite and the top left
        # corner of the sprite
        width, height = sprite.get_size()
        offset = pymunk.Vec2d(width, height) / 2
        p = p - offset
        screen.blit(sprite, p)  # Copy the sprite on the screen
        return screen


class GamePhysicsObject(GameObject):
    """
    Class for objects which interact with the physics engine.

    This class extends GameObject and it is used for objects which have a
    physical shape (such as tanks and boxes). This class handles the physical
    interaction of the objects.
    """

    def __init__(self, x, y, orientation, sprite, space, movable, gs):
        """
        Initialize an instance of GamePhysicsObject.

        Input:
        x, y: Starting coordinates.
        orientation: Orientation.
        sprite: Image representing the object.
        space: Physics engine object.
        movable: Whether the object is movable.
        """
        super().__init__(sprite)

        # Half dimensions of the object converted from screen coordinates to
        # physics coordinates.
        half_width = 0.5 * self.sprite.get_width() / gs.settings.TILE_SIZE
        half_height = 0.5 * self.sprite.get_height() / gs.settings.TILE_SIZE

        # Physical objects have a rectangular shape,
        # the points correspond to the corners of that shape.
        points = [[-half_width, -half_height],
                  [-half_width, half_height],
                  [half_width, half_height],
                  [half_width, -half_height]]

        self.points = points

        # Create a body (which is the physical representation of this game
        # object in the physics engine).
        if (movable):
            # Create a movable object with some mass and moments
            # (considering the game is a top view game, with no gravity,
            # the mass is set to the same value for all objects)."""
            mass = 10
            moment = pymunk.moment_for_poly(mass, points)
            self.body = pymunk.Body(mass, moment)
        else:
            # Create a non movable (static) object
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.body.position = x, y

        # orientation is provided in degress, but pymunk expects radians.
        self.body.angle = math.radians(orientation)

        # Create a polygon shape using the corner of the rectangle
        self.shape = pymunk.Poly(self.body, points)
        self.shape.parent = self

        # Set some value for friction and elasticity, which defines
        # interraction in case of a colision
        # self.shape.friction = 0.5
        # self.shape.elasticity = 0.1

        # Add the object to the physic engine
        space.add(self.body, self.shape)

    def screen_position(self, gs):
        """
        Return the screen coordinates of the physics object.

        Converts the body's position in the physics engine to screen
        coordinates.
        """
        return physics_to_display(self.body.position, gs)

    def screen_orientation(self):
        """Angles are reversed from the engine to the display."""
        return -math.degrees(self.body.angle)


class Bullet(GamePhysicsObject):
    """Bullets in the game."""

    # Default bullet speed.
    MUZZLE_VELOCITY = pymunk.Vec2d(0, 5)

    def __init__(self, x, y, orientation, velocity, space, gs):
        """Initialise a bullet."""
        x1, y1 = pymunk.Vec2d(x, y) \
            + pymunk.Vec2d(0, 0.4).rotated(math.radians(orientation))  # Offset

        super().__init__(x1, y1,
                         orientation,
                         gs.sprites.bullet,
                         space,
                         True,
                         gs)

        # The constant velocity at which the bullet should be kept.
        # Muzzle velocity + Tank velocity.
        self.velocity = self.MUZZLE_VELOCITY.rotated(self.body.angle)\
            + velocity

        self.body.velocity = self.velocity

        # Add collision type to shape for collision handling.
        self.shape.collision_type = 1
        self.shape.parent = self

    def update(self, gs):
        """Keep velocity constant."""
        self.body.velocity = self.velocity

    def turn(self, direction):
        """Turn the bullet in the selected direction."""
        self.body.angle = direction
        self.velocity = self.MUZZLE_VELOCITY.rotated(self.body.angle)


def clamp(min_max, value):
    """
    Bound a value to a specific interval.

    Convenient helper function.
    """
    return min(max(-min_max, value), min_max)


class Tank(GamePhysicsObject):
    """
    The class for all tanks.

    Extends GamePhysicsObject and handles aspects which are specific to our
    tanks.
    """

    # Constant values for the tank, acessed like: Tank.ACCELERATION
    # You can add more constants here if needed later

    def __init__(self, x, y, orientation, sprite, space, gs):
        """Initialize an instance of a tank."""
        super().__init__(x, y, orientation, sprite, space, True, gs)

        self.POS_ACC = 0.2
        self.ANG_ACC = 0.2
        self.FRAMERATE = gs.settings.FRAMERATE
        self.NORMAL_MAX_SPEED = 2.0
        self.FLAG_MAX_SPEED = self.NORMAL_MAX_SPEED * 0.5
        self.TICKS_INVINCIBLE = 5 * gs.settings.FRAMERATE

        # Set tanks hp
        self.hp = 3
        self.defaultsprite = sprite.copy().convert_alpha()

        # Define variable used to apply motion to the tanks.

        # 1 forward, 0 for stand still, -1 for backwards.
        self.acceleration = 0

        # 1 clockwise, 0 for no rotation, -1 counter clockwise.
        self.rotation = 0

        # This variable is used to access the flag object, if the current tank
        # is carrying the flag.
        self.flag = None

        # Impose a maximum speed to the tank.self.body
        self.max_speed = self.NORMAL_MAX_SPEED

        # Starting angle of tank.
        self.start_angle = self.body.angle

        # Define the start position, which is also the position where the tank
        # has to return with the flag.
        self.start_position = pymunk.Vec2d(x, y)

        # Tank spawns ready to shoot bullet.
        self.cooldown_bullet = 0
        # Variable for guided bullets.
        self.guided_bullet = None

        self.space = space

        self.shape.collision_type = 3
        self.shape.parent = self

        # Respawn protection
        self.inv_ticks = self.TICKS_INVINCIBLE

        # Make blink
        self.sprite.set_alpha(math.sin(self.inv_ticks))

    def accelerate(self):
        """Make the tank move forward."""
        if self.guided_bullet:
            self.guided_bullet.turn(math.pi)
        self.acceleration = 1

    def decelerate(self):
        """Make the tank move backward."""
        if self.guided_bullet:
            self.guided_bullet.turn(0)
        self.acceleration = -1

    def _drop_flag(self):
        """Drop flag from tank."""
        if self.flag:
            self.flag.is_on_tank = False
            self.flag = None

    def take_damage(self, sprites):
        """Decrements health, and if zero, respawns tank."""
        if self.inv_ticks < 0:
            if self.hp > 1:
                self.hp -= 1
                ovl = sprites.tank_overlays[self.hp - 1]
                self.sprite.blit(ovl, ovl.get_rect())
            else:
                self.respawn()

    def respawn(self):
        """Respawn the tank at its starting location."""

        self.stop_moving()
        self.stop_turning()
        self._drop_flag()
        self.body.position = self.start_position
        self.body.angle = self.start_angle

        # Make hp full again
        self.hp = 3
        self.sprite = self.defaultsprite.copy().convert_alpha()

        # Respawn protection
        self.inv_ticks = self.TICKS_INVINCIBLE

        # Makes tanks transparent
        self.sprite.set_alpha(math.sin(self.inv_ticks))

    def stop_moving(self):
        """Make the tank stop moving."""
        self.acceleration = 0
        self.body.velocity = pymunk.Vec2d.zero()

    def stop_turning(self):
        """Make the tank stop turning."""
        self.rotation = 0
        self.body.angular_velocity = 0

    def turn_left(self):
        """Make the tank turn left (counter clock-wise)."""
        if self.guided_bullet:
            self.guided_bullet.turn(math.pi/2)
        self.rotation = -1

    def turn_right(self):
        """Make the tank turn right (clock-wise)."""
        if self.guided_bullet:
            self.guided_bullet.turn(3*math.pi/2)
        self.rotation = 1

    def update(self, gs):
        """
        Update the objects coordinates.

        Gets called at every tick of the game.
        """
        # Creates a vector in the direction we want accelerate / decelerate.
        acceleration_vector = pymunk.Vec2d(0,
                                           self.POS_ACC
                                           * self.acceleration
                                           ).rotated(self.body.angle)

        # Applies the vector to our velocity.
        self.body.velocity += acceleration_vector

        # Makes sure that we don't exceed our speed limit.
        velocity = clamp(self.max_speed, self.body.velocity.length)
        self.body.velocity = pymunk.Vec2d(velocity,
                                          0).rotated(self.body.velocity.angle)

        # Updates the rotation.
        self.body.angular_velocity += self.rotation * self.ANG_ACC
        self.body.angular_velocity = clamp(self.max_speed,
                                           self.body.angular_velocity)

    def post_update(self):
        """
        Update flag position or max speed.

        Update flag position if the tank has a flag or set max speed to normal
        if it does not.
        """
        # If the tank carries the flag, then update the positon of the flag
        if self.flag is not None:
            self.flag.x = self.body.position[0]
            self.flag.y = self.body.position[1]
            self.flag.orientation = -math.degrees(self.body.angle)

        # Else ensure that the tank has its normal max speed
        else:
            self.max_speed = self.NORMAL_MAX_SPEED

        # Counting down frames for cooldown of bullets
        self.cooldown_bullet -= 1

        if self.inv_ticks < 0:
            # Make opaque
            self.sprite.set_alpha(255)
        else:
            # Make pulsing effect
            self.sprite.set_alpha(64*math.sin(0.2*self.inv_ticks) + 128)

            # Decrement ticks for respawn protection
            self.inv_ticks -= 1

    def try_grab_flag(self, flag, gs):
        """
        Attempt to make the tank grab the flag.

        If the flag is not on another tank and it is close to the current tank,
        then the current tank will grab the flag.
        """
        # Check that the flag is not on other tank
        if (not flag.is_on_tank):
            # Check if the tank is close to the flag
            flag_pos = pymunk.Vec2d(flag.x, flag.y)
            if ((flag_pos - self.body.position).length < 0.5):
                # Grab the flag !
                if gs.settings.SOUND:
                    pickupflag_sound = mixer.Sound('data/pickupflag.wav')
                    pickupflag_sound.play()
                self.flag = flag
                flag.is_on_tank = True
                self.max_speed = self.FLAG_MAX_SPEED

    def has_won(self):
        """
        Check if the current tank has won.

        If it is has the flag and it is close to its start position, it has
        won.
        """

        return self.flag is not None and (self.start_position
                                          - self.body.position
                                          ).length < 0.2

    def shoot(self, gs):
        """Shoot (return) a bullet."""
        if self.cooldown_bullet < 1:
            # Set cooldown to framerate
            self.body.velocity -= Bullet.MUZZLE_VELOCITY.rotated(
                self.body.angle
            ) / 5
            self.cooldown_bullet = gs.settings.FRAMERATE

            # Sound for bullet
            if gs.settings.SOUND:
                bullet_sound_shoot = mixer.Sound('data/tankhit.wav')
                bullet_sound_shoot.play()

            # Return instance of bullet
            self.guided_bullet = Bullet(self.body.position[0],
                                        self.body.position[1],
                                        math.degrees(self.body.angle),
                                        self.body.velocity,
                                        self.space,
                                        gs
                                        )
            return self.guided_bullet


class Box(GamePhysicsObject):
    """This class extends the GamePhysicsObject to handle box objects."""

    def __init__(self, x, y,
                 sprite,
                 movable,
                 space,
                 gs,
                 collision_type=0,
                 hp=-1):
        """
        Initialize an instance of a box.

        Input:
        x, y: Starting position of the box.
        sprite: Sprite to represent the box.
        movable: Whether or not the box is movable.
        space: Physics object.
        collision_type : Determines how collisions should be handled (default=0)
        hp : Health points (default=-1, invincible)
        """
        super().__init__(x, y, 0, sprite, space, movable, gs)
        self.shape.collision_type = collision_type
        self.hp = hp
        self.shape.parent = self


def get_box_with_type(x, y, boxtype, space, gs):
    """
    Return a box of type 1-3.

    Type 1:
    A non-movable, non-destructible rockbox.

    Type 2:
    A movable, destructible woodbox.

    Type 3:
    A movable, non-destructible metalbox.
    """
    # Offsets the coordinate to the center of the tile.
    (x, y) = (x + 0.5, y + 0.5)

    if boxtype == 1:
        # Rockbox
        return Box(x, y, gs.sprites.rockbox, False, space, gs)

    elif boxtype == 2:
        # Woodbox (hp = 2)
        return Box(x, y, gs.sprites.woodbox, True, space, gs, 2, 2)

    elif boxtype == 3:
        # Metalbox
        return Box(x, y, gs.sprites.metalbox, True, space, gs)


class GameVisibleObject(GameObject):
    """
    Visible objects that do not interact with the physics engine.

    Used for bases and the flag.
    """

    def __init__(self, x, y, sprite):
        """
        Initialize a visible object.

        Input:
        x, y: Starting position of the object.
        sprite: Sprite to represent the object.
        """
        self.x = x
        self.y = y
        self.orientation = 0
        super().__init__(sprite)

    def screen_position(self, gs):
        """
        Return visual coordinates of the object.

        Transforms the physics coordinates to visual coordinates.
        """
        return physics_to_display(pymunk.Vec2d(self.x, self.y), gs)

    def screen_orientation(self):
        """Unknown Function. TODO."""
        return self.orientation


class Flag(GameVisibleObject):
    """This class extends GameVisibleObject for representing flags."""

    def __init__(self, gs):
        """Initialize a flag at coordinates x,y."""
        self.is_on_tank = False
        x, y = gs.current_map.flag_position
        super().__init__(x, y, gs.sprites.flag)


class Explosion(GameVisibleObject):
    """This class is used to represent explosions."""

    def __init__(self, position, gs):
        """Initialize an explosion."""
        self.LIFETIME = gs.settings.FRAMERATE//4
        self.timer = self.LIFETIME
        x, y = position
        super().__init__(x, y, gs.sprites.explosion_list[0])

    def update(self, gs):
        """Count down to self-deletion."""
        self.timer -= 1

        if self.timer < 1:
            gs.objects.remove(self)
        elif self.timer < 0.125 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[7]
        elif self.timer < 0.250 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[6]
        elif self.timer < 0.375 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[5]
        elif self.timer < 0.500 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[4]
        elif self.timer < 0.625 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[3]
        elif self.timer < 0.750 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[2]
        elif self.timer < 0.875 * self.LIFETIME:
            self.sprite = gs.sprites.explosion_list[1]
