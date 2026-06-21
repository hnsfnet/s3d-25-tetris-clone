from constants import GRID_WIDTH, GRID_HEIGHT, SCORE_TABLE


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def reset(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def check_collision(self, piece, dx=0, dy=0):
        shape = piece.get_shape()
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    new_x = piece.x + c + dx
                    new_y = piece.y + r + dy
                    if new_x < 0 or new_x >= GRID_WIDTH:
                        return True
                    if new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return True
        return False

    def lock_piece(self, piece):
        shape = piece.get_shape()
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    grid_y = piece.y + r
                    grid_x = piece.x + c
                    if grid_y < 0:
                        return False
                    self.grid[grid_y][grid_x] = piece.color
        return True

    def clear_lines(self, level):
        cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                for move_y in range(y, 0, -1):
                    self.grid[move_y] = list(self.grid[move_y - 1])
                self.grid[0] = [None for _ in range(GRID_WIDTH)]
                cleared += 1
            else:
                y -= 1
        if cleared > 0:
            return SCORE_TABLE.get(cleared, 0) * level, cleared
        return 0, 0
