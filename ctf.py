#!/usr/bin/env python3
"""Main game program."""

# -- Import libraries
import sys
from enum import Enum
import pygame
import handle_events
from pygame import mixer

# -- Import from the ctf framework.
import menus
import maps
from resources import Sprites
import resources
import gamestate

# -- Create a clock instance
clock = pygame.time.Clock()

# -- Initialize the display.
pygame.init()

# -- Set the caption of window
pygame.display.set_caption('Capture The Flag')

# -- Handle console-line options
selected_settings = resources.Constants()
selected_map = maps.map0
# custom maps
if "--map" in sys.argv:
    # Get file name from options
    file_path = sys.argv[sys.argv.index("--map") + 1]
    # Generate map from text file
    selected_map = maps.map_from_txt(file_path)
# multiplayer
if "--mp" in sys.argv:
    selected_settings.NPLAYERS = 2
# no clock
if "--noclock" in sys.argv:
    selected_settings.USE_CLOCK = False
if "--nosound" in sys.argv:
    selected_settings.SOUND = False

# Set display to (800, 800)
DEF_SCREEN_SIZE = (800, 800)
screen = menus.set_display(DEF_SCREEN_SIZE)

# -- Create a gamestate
gs = gamestate.GameState(screen,
                         current_map=selected_map,
                         settings=selected_settings)

# -- Keep track of scores
scores = {}

# Start without displaying scores overlay
scores_millis = -5000

# Set the background music.
#if gs.settings.SOUND:
    #background_sound = mixer.Sound('data\e1m1.flac')
    # Play the background music
    #background_sound.play(-1)

skip_update = 0

# Game and menu state class
Menu = Enum('Menu', ['OFF', 'HOMESCREEN', 'SETTINGS', 'GAME'])
draw = Menu.HOMESCREEN
old_draw = Menu.OFF

# --- Program loop
while draw != Menu.OFF:

    # - Handle state change
    if draw != old_draw:
        # This code only runs once, just as draw changes
        if draw == Menu.HOMESCREEN:
            sprites = Sprites(screen, gs)

            # Set background
            background = sprites.background

        elif draw == Menu.GAME:
            # Get current map size
            map_w, map_h = gs.current_map.rect().size
            w, h = screen.get_size()
            lesser_ratio = min(h/map_h, w/map_w)

            # Populate gamestate
            gs.generate_fresh(screen)

            # Add collision handlers
            gs.add_collision_handlers()

            # Initialise all player scores to zero
            scores = {tank.start_position: 0 for tank in gs.tanks}

            sprites = Sprites(screen, gs)

            # Set background
            background = sprites.background

    # - Keep track of state change
    old_draw = draw

    # Get event list
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.VIDEORESIZE:
            map_w, map_h = gs.current_map.rect().size
            w, h = event.w, event.h
            screen = menus.set_display((event.w, event.h))
            sprites = Sprites(screen, gs)
            background = sprites.background
            lesser_ratio = min(h/map_h, w/map_w)

    # --- Homescreen
    if draw == Menu.HOMESCREEN:
        draw = menus.home_screen(screen,
                                 clock,
                                 gs,
                                 events,
                                 Menu)

    # --- Settings screen
    elif draw == Menu.SETTINGS:
        draw, gs = menus.settings(screen,
                                  clock,
                                  gs,
                                  events,
                                  Menu,
                                  sprites)

    # --- Game
    elif draw == Menu.GAME:

        # Handle key input and return to HOMESCREEN if ESC is pressed
        if not handle_events.key_events(events, gs):
            draw = Menu.HOMESCREEN

        # Close program if window is quit
        if pygame.QUIT in [event.type for event in events]:
            draw = Menu.OFF

        # Update all physics
        gs.update_physics(skip_update)

        # Try to grab flag for every tank
        gs.tanks_try_grab_flag()

        # Check if any tanks have won
        for tank in gs.tanks:
            if tank.has_won():

                # Increase score for tank won
                scores[tank.start_position] += 1

                # Return to homescreen if any score is 5
                if scores[tank.start_position] == 5:
                    draw = Menu.HOMESCREEN

                # Generate fresh instances of everything
                gs.generate_fresh(screen)

                # Create new collision handlers
                gs.add_collision_handlers()

                # Remember millis when game was reset
                # (Start displaying scores overlay)
                scores_millis = pygame.time.get_ticks()

        # Make all bots decide + maybe_shoot
        gs.decide_all_bots()

        # Update display
        if gs.settings.DRAW:
            handle_events.update_display(screen,
                                         background,
                                         gs,
                                         clock,
                                         scores,
                                         lesser_ratio,
                                         scores_millis)
