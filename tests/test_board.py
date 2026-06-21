import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from board import Board
from piece import Piece
from constants import GRID_WIDTH, GRID_HEIGHT, COLORS


class TestBoardInit(unittest.TestCase):
    def test_board_dimensions(self):
        board = Board()
        self.assertEqual(len(board.grid), GRID_HEIGHT)
        self.assertEqual(len(board.grid[0]), GRID_WIDTH)

    def test_board_initial_empty(self):
        board = Board()
        for row in board.grid:
            for cell in row:
                self.assertIsNone(cell)

    def test_board_reset(self):
        board = Board()
        board.grid[0][0] = (255, 0, 0)
        board.reset()
        for row in board.grid:
            for cell in row:
                self.assertIsNone(cell)


class TestBoardCollision(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.piece = Piece('O')
        self.piece.x = 3
        self.piece.y = 0

    def test_no_collision_in_middle(self):
        self.assertFalse(self.board.check_collision(self.piece, 0, 0))

    def test_collision_left_boundary(self):
        self.piece.x = 0
        self.assertTrue(self.board.check_collision(self.piece, -1, 0))
        self.assertFalse(self.board.check_collision(self.piece, 0, 0))

    def test_collision_right_boundary(self):
        self.piece.x = GRID_WIDTH - 2
        self.assertTrue(self.board.check_collision(self.piece, 1, 0))
        self.assertFalse(self.board.check_collision(self.piece, 0, 0))

    def test_collision_bottom_boundary(self):
        self.piece.y = GRID_HEIGHT - 2
        self.assertTrue(self.board.check_collision(self.piece, 0, 1))
        self.assertFalse(self.board.check_collision(self.piece, 0, 0))

    def test_no_collision_top_outside(self):
        self.piece.y = -1
        self.assertFalse(self.board.check_collision(self.piece, 0, 0))

    def test_collision_with_existing_block(self):
        self.board.grid[1][3] = (255, 0, 0)
        self.assertTrue(self.board.check_collision(self.piece, 0, 0))

    def test_no_collision_with_existing_block_elsewhere(self):
        self.board.grid[5][5] = (255, 0, 0)
        self.assertFalse(self.board.check_collision(self.piece, 0, 0))

    def test_I_piece_collision(self):
        piece = Piece('I')
        piece.x = -1
        piece.y = 0
        self.assertTrue(self.board.check_collision(piece, 0, 0))


class TestBoardLockPiece(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_lock_O_piece(self):
        piece = Piece('O')
        piece.x = 3
        piece.y = 18
        result = self.board.lock_piece(piece)
        self.assertTrue(result)
        self.assertEqual(self.board.grid[18][3], COLORS['O'])
        self.assertEqual(self.board.grid[18][4], COLORS['O'])
        self.assertEqual(self.board.grid[19][3], COLORS['O'])
        self.assertEqual(self.board.grid[19][4], COLORS['O'])

    def test_lock_piece_partially_outside_top(self):
        piece = Piece('O')
        piece.x = 3
        piece.y = -1
        result = self.board.lock_piece(piece)
        self.assertFalse(result)

    def test_lock_piece_fully_outside_top(self):
        piece = Piece('O')
        piece.x = 3
        piece.y = -2
        result = self.board.lock_piece(piece)
        self.assertFalse(result)

    def test_lock_I_piece(self):
        piece = Piece('I')
        piece.x = 3
        piece.y = 19
        result = self.board.lock_piece(piece)
        self.assertTrue(result)
        for c in range(4):
            self.assertEqual(self.board.grid[19][3 + c], COLORS['I'])


class TestBoardClearLines(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_no_lines_cleared(self):
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(score, 0)
        self.assertEqual(cleared, 0)

    def test_single_line_clear(self):
        for c in range(GRID_WIDTH):
            self.board.grid[19][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(score, 100)
        self.assertEqual(cleared, 1)
        for c in range(GRID_WIDTH):
            self.assertIsNone(self.board.grid[19][c])

    def test_double_line_clear(self):
        for c in range(GRID_WIDTH):
            self.board.grid[18][c] = (255, 0, 0)
            self.board.grid[19][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(score, 300)
        self.assertEqual(cleared, 2)

    def test_triple_line_clear(self):
        for c in range(GRID_WIDTH):
            self.board.grid[17][c] = (255, 0, 0)
            self.board.grid[18][c] = (255, 0, 0)
            self.board.grid[19][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(score, 500)
        self.assertEqual(cleared, 3)

    def test_tetris_line_clear(self):
        for c in range(GRID_WIDTH):
            for r in range(16, 20):
                self.board.grid[r][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(score, 800)
        self.assertEqual(cleared, 4)

    def test_line_clear_with_level_multiplier(self):
        for c in range(GRID_WIDTH):
            self.board.grid[19][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(3)
        self.assertEqual(score, 300)
        self.assertEqual(cleared, 1)

    def test_above_blocks_move_down(self):
        self.board.grid[18][0] = (0, 255, 0)
        for c in range(GRID_WIDTH):
            self.board.grid[19][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(cleared, 1)
        self.assertEqual(self.board.grid[19][0], (0, 255, 0))
        self.assertIsNone(self.board.grid[18][0])

    def test_non_consecutive_lines_clear(self):
        for c in range(GRID_WIDTH):
            self.board.grid[17][c] = (255, 0, 0)
            self.board.grid[19][c] = (255, 0, 0)
        self.board.grid[18][0] = (0, 255, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(cleared, 2)
        self.assertEqual(self.board.grid[19][0], (0, 255, 0))

    def test_partial_line_not_cleared(self):
        for c in range(GRID_WIDTH - 1):
            self.board.grid[19][c] = (255, 0, 0)
        score, cleared = self.board.clear_lines(1)
        self.assertEqual(score, 0)
        self.assertEqual(cleared, 0)
        self.assertEqual(self.board.grid[19][0], (255, 0, 0))


class TestBoardSpawnPosition(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_spawn_position_empty_board(self):
        piece = Piece('O')
        self.assertFalse(self.board.check_collision(piece, 0, 0))

    def test_spawn_position_with_blocks_below(self):
        for c in range(GRID_WIDTH):
            for r in range(10, GRID_HEIGHT):
                self.board.grid[r][c] = (255, 0, 0)
        piece = Piece('O')
        self.assertFalse(self.board.check_collision(piece, 0, 0))

    def test_spawn_position_with_blocks_at_top(self):
        self.board.grid[1][3] = (255, 0, 0)
        self.board.grid[1][4] = (255, 0, 0)
        self.board.grid[2][3] = (255, 0, 0)
        self.board.grid[2][4] = (255, 0, 0)
        piece = Piece('O')
        self.assertTrue(self.board.check_collision(piece, 0, 0))

    def test_spawn_position_I_piece(self):
        piece = Piece('I')
        self.assertFalse(self.board.check_collision(piece, 0, 0))


if __name__ == '__main__':
    unittest.main()
