"""Includes the class GameState which represents the state of the game."""
from gameobjects import Explosion
import objectcreation
from resources import Sprites
from ai import AI
from pygame import mixer


class GameState:
    """
    Describes an entire game state.

    This includes:
    - flag instance
    - list of all tanks
    - list of all game objects
    - pymunk space instance
    - settings instance
    - current map
    - list of all players
    - list of all ai bots

    Also has method for generating fresh instance, using objectcreation module.
    """

    def __init__(self,
                 screen,
                 flag=None,
                 tanks=None,
                 objects=None,
                 space=None,
                 settings=None,
                 current_map=None,
                 players=None,
                 ais=None):
        """Initialise an instance of gamestate."""
        self.settings = settings
        self.current_map = current_map
        self.flag = flag
        self.tanks = tanks
        self.objects = objects
        self.space = space
        self.players = players
        self.ais = ais
        self.sprites = Sprites(screen, self)

    def generate_fresh(self, screen):
        """Generate everything fresh, based on current_map and settings."""
        (self.flag,
         self.tanks,
         self.objects,
         self.space) = objectcreation.create_everything(self)

        self.players = self.tanks[:self.settings.NPLAYERS]
        self.ais = [AI(tank,
                       self.objects,
                       self.tanks,
                       self.space,
                       self.current_map)
                    for tank in self.tanks[self.settings.NPLAYERS:]]

        # Make AIs unfair buff.
        for ai in self.ais:
            ai.tank.POS_ACC *= 1.3
            ai.tank.ANG_ACC *= 1.3
            ai.tank.NORMAL_MAX_SPEED *= 1.5

        self.sprites = Sprites(screen, self)
        return self

    def decide_all_bots(self):
        """Run decide and maybe_shoot methods for all ai bots."""
        [ai.decide() for ai in self.ais]

        for ai in self.ais:
            if bullet := ai.maybe_shoot(self):
                self.objects.append(bullet)

    def tanks_try_grab_flag(self):
        """Try to grab flag for every tank in gamestate."""
        [tank.try_grab_flag(self.flag, self) for tank in self.tanks]

    def add_collision_handlers(self):
        """Add collision handlers to the gamestate."""
        if self.settings.SOUND:
            collision_sound_wall = mixer.Sound('data/collisionobject.flac')
            explosion_sound = mixer.Sound('data/explosion.wav')

        def _remove_object(obj):
            if obj in self.objects:
                self.objects.remove(obj)
                self.objects.append(Explosion(obj.body.position,
                                              self))
                if self.settings.SOUND:
                    explosion_sound.play()

            self.space.remove(obj.shape, obj.shape.body)
            return True

        def _collision_bullet_border_rockbox_metalbox(arb, space, data):
            bullet = arb.shapes[0].parent
            if self.settings.SOUND:
                collision_sound_wall.play()
            _remove_object(bullet)
            return True

        def _collision_bullet_woodbox(arb, space, data):
            bullet = arb.shapes[0].parent
            woodbox = arb.shapes[1].parent
            _remove_object(bullet)
            if woodbox.hp > 1:
                woodbox.sprite = self.sprites.woodbox_broken
                woodbox.hp -= 1
            else:
                _remove_object(woodbox)

            return True

        def _collision_bullet_tank(arb, space, data):
            bullet = arb.shapes[0].parent
            tank = arb.shapes[1].parent
            _remove_object(bullet)
            tank.take_damage(self.sprites)
            return True

        # Handles bullet - rockbox, border and metalbox collisions
        handler_rockbox = self.space.add_collision_handler(1, 0)
        handler_rockbox.pre_solve = _collision_bullet_border_rockbox_metalbox

        # Handles bullet - tank collision
        handler_tank = self.space.add_collision_handler(1, 3)
        handler_tank.pre_solve = _collision_bullet_tank

        # Handles bullet - woodbox collisions
        handler_woodbox = self.space.add_collision_handler(1, 2)
        handler_woodbox.pre_solve = _collision_bullet_woodbox

    def update_physics(self, skip_update):
        """
        Update all the physics of the game.

        Specifically the tanks speed by checking its acceleration,
        the collision of different objects,
        the position of tanks,
        and whether the player is close to the flag.
        Also update the display of the game and control the frame rate.
        """
        # -- Update physics
        if skip_update == 0:
            # Loop over all the game objects and update their speed in function
            # of their acceleration.
            [obj.update(self) for obj in self.objects]
            skip_update = 2
        else:
            skip_update -= 1

        # Check collisions and update the objects position
        self.space.step(1 / self.settings.FRAMERATE)

        # Update object that depends on an other object position
        # (for instance a flag)
        [obj.post_update() for obj in self.objects]
