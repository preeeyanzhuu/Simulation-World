class Road:

    def __init__(self, road_id, cells):
        self.road_id = road_id
        self.cells = cells

    def get_occupied_cells(self):
        return self.cells

    def place_on_grid(self, grid):
        for row, col in self.cells:
            grid[row][col] = {"type": "road", "road_id": self.road_id}

    def to_dict(self):
        return {
            "road_id": self.road_id,
            "cells": self.cells,
        }

    def __repr__(self):
        return f"Road(road_id={self.road_id!r}, cells={self.cells})"
