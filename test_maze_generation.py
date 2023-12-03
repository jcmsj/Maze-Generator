import unittest
from Cell import Cell
from maze import make_initial_maze, random_cell
from prim import prim
from random_dfs import random_dfs

def collect_isoleted_cells(maze: list[list[Cell]]):
    """Collects all the isolated cells in the maze"""
    return [cell for row in maze for cell in row if not cell.visited]
class MazeGeneration(unittest.TestCase):
    def test_prim_has_no_isolated_cells(self):
        # Run prim algorithm to get the output
        start,end, gen, maze, traversal = prim(make_initial_maze(30,20))
        maze:list[list[Cell]] = []
        # Simply consume the generator
        for _ in gen:
            pass
        # Check if there are any isolated cells in the output
        # Assert that there are no isolated cells in the output
        self.assertEqual(len(collect_isoleted_cells(maze)), 0, "There are isolated cells in the output")
    def test_random_dfs_has_no_isolated_cells(self):
        # Run prim algorithm to get the output
        _,_, gen,maze, _ = random_dfs(30,20)
        # Simply consume the generator
        for _ in gen:
            pass
        # Assert that there are no isolated cells in the output
        self.assertEqual(len(collect_isoleted_cells(maze)), 0, "There are isolated cells in the output")

if __name__ == '__main__':
    unittest.main()
