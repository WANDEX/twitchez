#!/usr/bin/env python3
# coding=utf-8

from itertools import islice
import conf


class Grid:
    """Grid of boxes inside the Window."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width"))

    def __init__(self):
        """set key_list -> each key will have (X, Y) values on the Grid."""
        # FIXME: temporary hardcoded
        self.area_cols = 230
        self.area_rows = 50
        self.key_list = []
        # TODO: update value after pressing scroll key
        #       particularly: set it to total from capacity()
        self.key_start_index = 0

    def capacity(self, string="all"):
        """Count how many boxes fit in the area.
        returns value based on string: "all", "cols", "rows", "total".
        """
        cols = int(self.area_cols / self.w)
        rows = int(self.area_rows / self.h)
        total = cols * rows
        if "all" in string:
            return cols, rows, total
        elif "total" in string:
            return total
        elif "col" in string:
            return cols
        elif "row" in string:
            return rows
        else:
            raise ValueError(f"Unsupported argument string: '{string}'")

    def spacing(self, string, cols):  # TODO rows
        """Calculate even spacing between grid elements.
        returns spacing based on string: "cols", "rows".
        """
        if "col" in string:
            return int((self.area_cols - self.w * cols) / cols)
        elif "row" in string:
            return 1  # FIXME: temporary hardcoded
        else:
            raise ValueError(f"Unsupported argument string: '{string}'")

    def coordinates(self, initial_x=0, initial_y=0) -> dict:  # FIXME: x, y initial values temporary hardcoded
        """Return dict with: tuple(X, Y) values where each key_list element is the key."""
        cols, rows, total = self.capacity()
        total += self.key_start_index  # for scrolling
        spacing_cols = self.spacing("cols", cols)
        spacing_rows = self.spacing("rows", rows)
        x = initial_x
        y = initial_y
        current_col = 1
        coordinates = {}
        for key in islice(self.key_list, self.key_start_index, total):
            coordinates[key] = (x, y)
            if current_col < cols:
                current_col += 1
                x += spacing_cols + self.w
            else:
                current_col = 1
                x = initial_x
                y += spacing_rows + self.h
        return coordinates
