"""Defines all the maps and their functions."""
from resources import Constants
import pygame
import json


class Map:
    """An instance of Map is a blueprint for how the game map will look."""

    def __init__(self, width, height, boxes, start_positions, flag_position):
        """
        Initialize a map.

        Input:
        width, height: Size of the map.
        boxes: An array with the boxes type.
        start_positions: Start positions of tanks.
        flag_position: Flag position.
        """
        self.width = width
        self.height = height
        self.boxes = boxes
        self.start_positions = start_positions
        self.flag_position = flag_position

    def rect(self):
        """Return a Rect with the maps size in pixels."""
        return pygame.Rect(0, 0,
                           Constants.TILE_SIZE*self.width,
                           Constants.TILE_SIZE*self.height)

    def boxAt(self, x, y):
        """Return the type of the box at coordinates (x, y)."""
        return self.boxes[y][x]


def map_from_txt(file_path):
    """Take a file path to file describing map, and return instance of Map."""
    with open(file_path) as f:
        map_args = json.load(f)
        width, height, boxes, start_positions, flag_position = map_args
        return Map(width,
                   height,
                   boxes,
                   start_positions,
                   flag_position)


map0 = Map(9, 9,

           [[0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 2, 0, 2, 0, 1, 0],
            [0, 2, 0, 1, 0, 1, 0, 2, 0],
            [0, 0, 0, 1, 0, 1, 0, 0, 0],
            [1, 1, 0, 3, 0, 3, 0, 1, 1],
            [0, 0, 0, 1, 0, 1, 0, 0, 0],
            [0, 2, 0, 1, 0, 1, 0, 2, 0],
            [0, 1, 0, 2, 0, 2, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0]],

           [[0.5, 0.5, 0],
            [8.5, 0.5, 0],
            [0.5, 8.5, 180],
            [8.5, 8.5, 180]],

           [4.5, 4.5])

map1 = Map(15, 11,

           [[0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 3, 1, 1, 0, 0, 0, 1, 1, 3, 0, 1, 0],
            [0, 2, 0, 0, 3, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0],
            [2, 1, 0, 1, 1, 0, 1, 3, 1, 0, 1, 1, 0, 1, 2],
            [1, 1, 3, 0, 3, 2, 3, 0, 3, 2, 3, 0, 3, 1, 1],
            [2, 1, 0, 1, 1, 0, 1, 3, 1, 0, 1, 1, 0, 1, 2],
            [0, 2, 0, 0, 3, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0],
            [0, 1, 0, 3, 1, 1, 0, 0, 0, 1, 1, 3, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0]],

           [[0.5,  0.5,  0],
            [14.5, 0.5,  0],
            [0.5,  10.5, 180],
            [14.5, 10.5, 180],
            [7.5,  0.5,  0],
            [7.5,  10.5, 180]],

           [7.5, 5.5])

map2 = Map(10, 5,

           [[0, 2, 0, 2, 0, 0, 2, 0, 2, 0],
            [0, 3, 0, 1, 3, 3, 1, 0, 3, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 3, 0, 1, 3, 3, 1, 0, 3, 0],
            [0, 2, 0, 2, 0, 0, 2, 0, 2, 0]],

           [[0.5, 2.5, 270],
            [9.5, 2.5, 90]],

           [5, 2.5])
