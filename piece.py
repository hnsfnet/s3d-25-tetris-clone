from constants import COLORS, INITIAL_SHAPES, GRID_WIDTH


def rotate_matrix_cw(matrix):
    n = len(matrix)
    transposed = [[matrix[c][r] for c in range(n)] for r in range(n)]
    return [row[::-1] for row in transposed]


def rotate_matrix_ccw(matrix):
    n = len(matrix)
    transposed = [[matrix[c][r] for c in range(n)] for r in range(n)]
    return transposed[::-1]


class Piece:
    def __init__(self, shape_type):
        self.type = shape_type
        self.color = COLORS[shape_type]
        self._initial_shape = [row[:] for row in INITIAL_SHAPES[shape_type]]
        self._shape = [row[:] for row in self._initial_shape]
        self.rotation = 0
        size = len(self._initial_shape)
        self.x = GRID_WIDTH // 2 - size // 2
        self.y = 0

    def get_shape(self):
        return self._shape

    def rotate(self):
        self._shape = rotate_matrix_cw(self._shape)
        self.rotation = (self.rotation + 1) % 4

    def unrotate(self):
        self._shape = rotate_matrix_ccw(self._shape)
        self.rotation = (self.rotation - 1) % 4

    def get_bounding_box(self):
        shape = self._shape
        rows = [r for r, row in enumerate(shape) if any(cell for cell in row)]
        cols = [c for c in range(len(shape[0])) if any(row[c] for row in shape)]
        if not rows or not cols:
            return (0, 0, 0, 0)
        return (min(rows), max(rows), min(cols), max(cols))
