"""All event handlers."""
import pygame
from pymunk import Vec2d


def key_events(events, gs):
    """
    Update the movement for the player tank based on what keys are pressed.

    Return false if an exit command is given.
    """
    for event in events:
        # Handle all key down events
        if event.type == pygame.KEYDOWN:

            # Stop running if ESC is pressed
            if event.key == pygame.K_ESCAPE:
                return False

            # Handle player 1 keypresses
            elif event.key == pygame.K_UP:
                gs.players[0].accelerate()

            elif event.key == pygame.K_DOWN:
                gs.players[0].decelerate()

            elif event.key == pygame.K_LEFT:
                gs.players[0].turn_left()

            elif event.key == pygame.K_RIGHT:
                gs.players[0].turn_right()

            elif event.key == pygame.K_SPACE and (
                    bullet := gs.players[0].shoot(gs)
            ):
                gs.objects.append(bullet)
                gs.players[0].guided_bullet = bullet

            elif event.key == pygame.K_u:
                gs.players[0]

            if gs.settings.NPLAYERS > 1:
                # Handle player 2 keypresses
                if event.key == pygame.K_w:
                    gs.players[1].accelerate()

                elif event.key == pygame.K_s:
                    gs.players[1].decelerate()

                elif event.key == pygame.K_a:
                    gs.players[1].turn_left()

                elif event.key == pygame.K_d:
                    gs.players[1].turn_right()

                elif event.key == pygame.K_b:
                    if bullet := gs.players[1].shoot(gs):
                        gs.objects.append(bullet)
                        gs.players[1].guided_bullet = bullet

        # Handle key up events
        elif event.type == pygame.KEYUP:

            # Handle player1 keyup
            if event.key in {pygame.K_UP, pygame.K_DOWN}:
                gs.players[0].stop_moving()

            elif event.key in {pygame.K_LEFT, pygame.K_RIGHT}:
                gs.players[0].stop_turning()

            elif event.key == pygame.K_SPACE:
                gs.players[0].guided_bullet = None

            if gs.settings.NPLAYERS > 1:
                # Handle player 2 keyup
                if event.key in {pygame.K_w, pygame.K_s}:
                    gs.players[1].stop_moving()

                elif event.key in {pygame.K_d, pygame.K_a}:
                    gs.players[1].stop_turning()

    # Return true if no quit events raised
    return True


def update_display(screen,
                   background,
                   gs,
                   clock,
                   scores,
                   lesser_ratio,
                   scores_millis):
    """
    Update the pygame display.

    Blit everything happening to a surface, then blit that surface to
    the pygame screen.

    Also blit score overlay to screen if any tank recently has won.
    """
    # Get screen size
    s_w, s_h = screen.get_size()

    # Get map size
    map_w, map_h = gs.current_map.rect().size

    # Create surface for blitting everything on
    temp_surf = pygame.Surface((map_w, map_h))

    # Display the background on the surface
    temp_surf.blit(background, (0, 0))

    # Update the display of the game objects on the surface
    [obj.update_screen(temp_surf, gs) for obj in gs.objects]

    # Display scores on map
    text_font = pygame.font.Font('data/Pixeltype.ttf',
                                 int(gs.settings.TILE_SIZE/2))

    [temp_surf.blit(text_font.render(f'{scores.get(key)}', False, "White"),
                    (gs.settings.TILE_SIZE *
                     (key + Vec2d(-0.4, -0.4))).int_tuple)
     for key in scores.keys()]

    # Blit black background
    screen.fill((0, 0, 0))

    # Blit score overlay (if necessary)
    curr_millis = pygame.time.get_ticks()
    millis_since_score = curr_millis - scores_millis
    if millis_since_score < 2000:
        score_surf = scores_overlay(gs.settings.TILE_SIZE,
                                    scores,
                                    (map_w, map_h))
        temp_surf.blit(score_surf, (0, 0))

    # Rescale temp_surf
    scaled = pygame.transform.scale(temp_surf, (int(map_w*lesser_ratio),
                                                int(map_h*lesser_ratio)))
    # Blit scaled surface to screen
    screen.blit(scaled, scaled.get_rect(center=(s_w / 2, s_h / 2)))

    # Update the screen
    pygame.display.flip()

    # Control the game framerate
    if gs.settings.USE_CLOCK:
        clock.tick(gs.settings.FRAMERATE)


def scores_overlay(tile_size, scores, map_size) -> pygame.Surface:
    """Return a surface displaying the game score."""

    # Create bigger font
    font = pygame.font.Font('data/Pixeltype.ttf', int(tile_size))

    # Create (transparent) surface with same dimensions as screen
    surf = pygame.Surface(map_size, pygame.SRCALPHA)

    # Blit transparent grey background
    surf.fill((20, 20, 20, 200))

    # For every score, blit on the surface
    for coord, score in scores.items():
        curr_surf = font.render(str(score),
                                False,
                                'Yellow')
        surf_coords = (coord*tile_size).int_tuple

        # Blit score in middle of base coordinate
        surf.blit(curr_surf, curr_surf.get_rect(center=surf_coords))

    return surf
