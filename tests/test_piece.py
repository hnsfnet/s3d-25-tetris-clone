import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from piece import Piece, rotate_matrix_cw, rotate_matrix_ccw
from constants import INITIAL_SHAPES, COLORS, GRID_WIDTH


class TestRotationMatrix(unittest.TestCase):
    def test_rotate_cw_3x3(self):
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]
        expected = [
            [7, 4, 1],
            [8, 5, 2],
            [9, 6, 3],
        ]
        self.assertEqual(rotate_matrix_cw(matrix), expected)

    def test_rotate_ccw_3x3(self):
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]
        expected = [
            [3, 6, 9],
            [2, 5, 8],
            [1, 4, 7],
        ]
        self.assertEqual(rotate_matrix_ccw(matrix), expected)

    def test_rotate_cw_4x4(self):
        matrix = [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        expected = [
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0],
        ]
        self.assertEqual(rotate_matrix_cw(matrix), expected)

    def test_rotate_full_cycle(self):
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]
        m = matrix
        for _ in range(4):
            m = rotate_matrix_cw(m)
        self.assertEqual(m, matrix)

    def test_rotate_cw_ccw_inverse(self):
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]
        m = rotate_matrix_cw(matrix)
        m = rotate_matrix_ccw(m)
        self.assertEqual(m, matrix)


class TestPieceInitialShape(unittest.TestCase):
    def test_I_initial_shape(self):
        piece = Piece('I')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['I'])
        self.assertEqual(piece.type, 'I')
        self.assertEqual(piece.color, COLORS['I'])
        self.assertEqual(piece.rotation, 0)

    def test_O_initial_shape(self):
        piece = Piece('O')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['O'])
        self.assertEqual(piece.type, 'O')

    def test_T_initial_shape(self):
        piece = Piece('T')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['T'])

    def test_S_initial_shape(self):
        piece = Piece('S')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['S'])

    def test_Z_initial_shape(self):
        piece = Piece('Z')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['Z'])

    def test_J_initial_shape(self):
        piece = Piece('J')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['J'])

    def test_L_initial_shape(self):
        piece = Piece('L')
        self.assertEqual(piece.get_shape(), INITIAL_SHAPES['L'])

    def test_initial_position(self):
        piece = Piece('O')
        self.assertEqual(piece.y, 0)
        self.assertEqual(piece.x, GRID_WIDTH // 2 - 1)

        piece_I = Piece('I')
        self.assertEqual(piece_I.y, 0)
        self.assertEqual(piece_I.x, GRID_WIDTH // 2 - 2)


class TestPieceRotation(unittest.TestCase):
    def test_O_rotation_symmetry(self):
        piece = Piece('O')
        initial = piece.get_shape()
        for _ in range(4):
            piece.rotate()
            self.assertEqual(piece.get_shape(), initial)
        self.assertEqual(piece.rotation, 0)

    def test_I_rotation_full_cycle(self):
        piece = Piece('I')
        initial = piece.get_shape()
        piece.rotate()
        self.assertNotEqual(piece.get_shape(), initial)
        piece.rotate()
        piece.rotate()
        piece.rotate()
        self.assertEqual(piece.get_shape(), initial)
        self.assertEqual(piece.rotation, 0)

    def test_T_rotation(self):
        piece = Piece('T')
        piece.rotate()
        expected = [
            [0, 1, 0],
            [0, 1, 1],
            [0, 1, 0],
        ]
        self.assertEqual(piece.get_shape(), expected)

    def test_unrotate(self):
        piece = Piece('T')
        initial = piece.get_shape()
        piece.rotate()
        self.assertNotEqual(piece.get_shape(), initial)
        piece.unrotate()
        self.assertEqual(piece.get_shape(), initial)
        self.assertEqual(piece.rotation, 0)

    def test_rotation_state_counter(self):
        piece = Piece('T')
        self.assertEqual(piece.rotation, 0)
        piece.rotate()
        self.assertEqual(piece.rotation, 1)
        piece.rotate()
        self.assertEqual(piece.rotation, 2)
        piece.rotate()
        self.assertEqual(piece.rotation, 3)
        piece.rotate()
        self.assertEqual(piece.rotation, 0)


class TestPieceBoundingBox(unittest.TestCase):
    def test_I_bounding_box_initial(self):
        piece = Piece('I')
        min_r, max_r, min_c, max_c = piece.get_bounding_box()
        self.assertEqual(min_r, 1)
        self.assertEqual(max_r, 1)
        self.assertEqual(min_c, 0)
        self.assertEqual(max_c, 3)

    def test_I_bounding_box_rotated(self):
        piece = Piece('I')
        piece.rotate()
        min_r, max_r, min_c, max_c = piece.get_bounding_box()
        self.assertEqual(min_r, 0)
        self.assertEqual(max_r, 3)
        self.assertEqual(min_c, 2)
        self.assertEqual(max_c, 2)

    def test_O_bounding_box(self):
        piece = Piece('O')
        min_r, max_r, min_c, max_c = piece.get_bounding_box()
        self.assertEqual(min_r, 0)
        self.assertEqual(max_r, 1)
        self.assertEqual(min_c, 0)
        self.assertEqual(max_c, 1)

    def test_T_bounding_box(self):
        piece = Piece('T')
        min_r, max_r, min_c, max_c = piece.get_bounding_box()
        self.assertEqual(min_r, 0)
        self.assertEqual(max_r, 1)
        self.assertEqual(min_c, 0)
        self.assertEqual(max_c, 2)


if __name__ == '__main__':
    unittest.main()
