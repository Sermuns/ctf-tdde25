"""Defines all common resources and constants used in the game."""
from dataclasses import dataclass
import pygame
import os


class Sprites:
    """Stores all sprites."""

    def __init__(self, screen, gs):
        """Load all sprites."""
        self.explosion_list = [pygame.transform.scale(_load_image(image),
                                                      (80, 80))
                               for image in ['regularExplosion00.png',
                                             'regularExplosion01.png',
                                             'regularExplosion02.png',
                                             'regularExplosion03.png',
                                             'regularExplosion04.png',
                                             'regularExplosion05.png',
                                             'regularExplosion06.png',
                                             'regularExplosion07.png']]

        self.grass = _load_image('grass.png')
        self.rockbox = _load_image('rockbox.png')
        self.metalbox = _load_image('metalbox.png')
        self.woodbox = _load_image('woodbox.png')
        self.woodbox_broken = _load_image('woodbox_broken.png')
        self.flag = _load_image('flag.png')
        self.bullet = pygame.transform.scale(
            pygame.transform.rotate(_load_image('bullet.png'), -90),
            (10, 10)
        )

        self.tanks = [_load_image(image)
                      for image in ['tank_orange.png',
                                    'tank_blue.png',
                                    'tank_white.png',
                                    'tank_yellow.png',
                                    'tank_red.png',
                                    'tank_gray.png']]

        self.tank_overlays = [_load_image(image)
                              for image in ['hp1_overlay.png',
                                            'hp2_overlay.png']]

        self.bases = [_load_image(image)
                      for image in ['base_orange.png',
                                    'base_blue.png',
                                    'base_white.png',
                                    'base_yellow.png',
                                    'base_red.png',
                                    'base_gray.png']]

        self.background = background(screen, self.grass, gs)


def background(screen, grass, gs):
    """Return a sprite of the background."""
    background = pygame.Surface(screen.get_size())
    # Copy the grass tile all over the level area.
    # The call to the function "blit" will copy the image
    # contained in "images.grass" into the "background"
    # image at the coordinates given as the second argument.
    [background.blit(grass,
                     (x*gs.settings.TILE_SIZE,
                      y*gs.settings.TILE_SIZE))
     for x in range(gs.current_map.width)
     for y in range(gs.current_map.height)]
    return background


def _load_image(file_name: str) -> pygame.surface.Surface:
    """Load an image from the data directory."""
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    file_path = os.path.join(main_dir, 'data', file_name)
    try:
        surface = pygame.image.load(file_path)
    except pygame.error:
        raise SystemExit(f'Could not load image "{file_path}"\
        {pygame.get_error()}')
    return surface.convert_alpha()


@dataclass
class Constants:
    """All in-game constants."""

    DRAW: bool = True
    USE_CLOCK: bool = True
    FRAMERATE: int = 60
    NPLAYERS: int = 1
    SOUND: bool = True
    TILE_SIZE: int = 40
