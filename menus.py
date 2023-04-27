"""Handles all the menus in the game."""
import pygame
import gamestate
import maps
import resources


def home_screen(screen, clock, gs, events, Menu):
    """Display all home screen buttons. Return a draw enumerator."""
    # Get current display size
    s_width, s_height = screen.get_size()

    text_font = pygame.font.Font('data/Pixeltype.ttf', 50)

    msg_ctf_surf = text_font.render('Capture the Flag',
                                    False,
                                    'Black').convert_alpha()

    msg_ctf_rect = msg_ctf_surf.get_rect(midtop=(s_width / 2,
                                                 s_height / 16))

    msg_play_surf = text_font.render('Play',
                                     False,
                                     'Black').convert_alpha()

    msg_play_rect = msg_play_surf.get_rect(midtop=(s_width / 2,
                                                   s_height / 8))

    msg_settings_surf = text_font.render('Settings',
                                         False,
                                         'Black').convert_alpha()

    msg_settings_rect = msg_settings_surf.get_rect(midtop=(s_width / 2,
                                                           s_height * 3 / 16
                                                           ))

    msg_exit_surf = text_font.render('Exit',
                                     False,
                                     'Black').convert_alpha()

    msg_exit_rect = msg_exit_surf.get_rect(midtop=(s_width / 2,
                                                   s_height / 4
                                                   ))

    for event in events:

        # Handle quit events
        if event.type == pygame.QUIT:
            return Menu.OFF

        # Stop running if ESC is pressed
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return Menu.OFF
            elif event.key == pygame.K_g:
                return Menu.GAME
            elif event.key == pygame.K_s:
                return Menu.SETTINGS

        # Handle all button clicks on main menu
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Start game loop
            if msg_play_rect.collidepoint(event.pos):
                return Menu.GAME
            elif msg_settings_rect.collidepoint(event.pos):
                return Menu.SETTINGS
            elif msg_exit_rect.collidepoint(event.pos):
                return Menu.OFF

    screen.fill((94, 129, 162))  # Set blue blackground
    screen.blit(msg_ctf_surf, msg_ctf_rect)
    screen.blit(msg_play_surf, msg_play_rect)
    screen.blit(msg_settings_surf, msg_settings_rect)
    screen.blit(msg_exit_surf, msg_exit_rect)
    pygame.display.update()
    clock.tick(gs.settings.FRAMERATE)
    return Menu.HOMESCREEN


def settings(screen, clock, gs, events, Menu, sprites):
    """
    Display the settings screen.

    Return a draw and gamestate tuple.
    """
    # Get current display size
    s_width, s_height = screen.get_size()

    text_font = pygame.font.Font('data/Pixeltype.ttf', 50)

    msg_settings_surf = text_font.render('Settings',
                                         False,
                                         'Black').convert_alpha()
    msg_settings_rect = msg_settings_surf.get_rect(midtop=(s_width / 2,
                                                   s_height / 10))

    msg_players_surf = text_font.render('Players',
                                        False,
                                        'Black').convert_alpha()
    msg_players_rect = msg_players_surf.get_rect(midtop=(s_width / 2,
                                                 s_height*4 / 20))

    msg_p1_surf = text_font.render('1', False, 'Black').convert_alpha()
    msg_p1_rect = msg_p1_surf.get_rect(midtop=(s_width * 15/32, s_height / 4))

    msg_p2_surf = text_font.render('2', False, 'Black').convert_alpha()
    msg_p2_rect = msg_p2_surf.get_rect(midtop=(s_width * 17/32, s_height / 4))

    msg_maps_surf = text_font.render('Maps', False, 'Black').convert_alpha()
    msg_maps_rect = msg_maps_surf.get_rect(midtop=(s_width / 2,
                                                   s_height * 5/16))

    msg_map1_surf = text_font.render('Map 1', False, 'Black').convert_alpha()
    msg_map1_rect = msg_map1_surf.get_rect(midtop=(s_width * 1 / 4,
                                                   s_height * 3 / 8))

    msg_map2_surf = text_font.render('Map 2', False, 'Black').convert_alpha()
    msg_map2_rect = msg_map2_surf.get_rect(midtop=(s_width / 2,
                                           s_height * 3 / 8))

    msg_map3_surf = text_font.render('Map 3', False, 'Black').convert_alpha()
    msg_map3_rect = msg_map3_surf.get_rect(midtop=(s_width * 3 / 4,
                                                   s_height * 3 / 8))

    # Back message
    msg_back_surf = text_font.render('Back', False, 'Black').convert_alpha()
    msg_back_rect = msg_back_surf.get_rect(midtop=(s_width / 2,
                                                   s_height * 5/8))

    for event in events:
        new_draw = Menu.SETTINGS
        new_gs = gs

        if event.type == pygame.QUIT:
            new_draw = Menu.OFF

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                new_draw = Menu.HOMESCREEN

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Players
            if msg_p1_rect.collidepoint(event.pos):
                new_gs.settings.NPLAYERS = 1
            elif msg_p2_rect.collidepoint(event.pos):
                new_gs.settings.NPLAYERS = 2

            # Maps
            elif msg_map1_rect.collidepoint(event.pos):
                new_gs.current_map = maps.map0
            elif msg_map2_rect.collidepoint(event.pos):
                new_gs.current_map = maps.map1
            elif msg_map3_rect.collidepoint(event.pos):
                new_gs.current_map = maps.map2

            # Back
            elif msg_back_rect.collidepoint(event.pos):
                new_draw = Menu.HOMESCREEN

            return (new_draw, new_gs)

    screen.fill((94, 129, 162))

    map_lst = [maps.map0, maps.map1, maps.map2]

    # List of blank map previews.
    preview_lst = [draw_over(pygame.Surface(mapn.rect().size),
                             pygame.transform.scale(gs.sprites.background,
                                                    (mapn.rect().size[0] * 10,
                                                     mapn.rect().size[1] * 10)))
                   for mapn in map_lst]

    # List of simple gamestates for map previews.
    gs_lst = [gamestate.GameState(screen,
                                  current_map=mapn,
                                  settings=resources.Constants())
              .generate_fresh(preview)
              for mapn, preview in zip(map_lst, preview_lst)]

    # List of filled and scaled map previews.
    scaled_lst = [pygame.transform.scale(
        list(map(lambda obj: obj.update_screen(preview, gs), gs.objects))[-1],
        (100, 100))
                  for preview, gs in zip(preview_lst, gs_lst)]

    # List of map rects
    map_rects = [scaled_lst[0].get_rect(midtop=(s_width * 1 / 4,
                                               s_height * 7 / 16)), 
                 scaled_lst[1].get_rect(midtop=(s_width / 2,
                                               s_height * 7 / 16)),
                 scaled_lst[2].get_rect(midtop=(s_width * 3 / 4,
                                               s_height * 7 / 16))]

    # Blit every scaled map preview onto screen
    [screen.blit(scaled, rect) for scaled, rect in zip(scaled_lst, map_rects)]

    screen.blit(msg_settings_surf, msg_settings_rect)
    screen.blit(msg_players_surf, msg_players_rect)
    screen.blit(msg_p1_surf, msg_p1_rect)
    screen.blit(msg_p2_surf, msg_p2_rect)

    screen.blit(msg_maps_surf, msg_maps_rect)
    screen.blit(msg_map1_surf, msg_map1_rect)
    screen.blit(msg_map2_surf, msg_map2_rect)
    screen.blit(msg_map3_surf, msg_map3_rect)

    screen.blit(msg_maps_surf, msg_maps_rect)
    screen.blit(msg_back_surf, msg_back_rect)

    pygame.display.flip()
    clock.tick(gs.settings.FRAMERATE)

    return (Menu.SETTINGS, gs)


def set_display(size: tuple):
    """Set the display to a (resizable) screen with given width and height."""
    return pygame.display.set_mode(size, pygame.RESIZABLE)


def draw_over(surface1, surface2):
    """Return a new surface with surface1 drawn over surface2."""
    temp = surface1.copy()
    temp.blit(surface2, (0, 0))
    return temp
