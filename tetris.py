import pygame
import random

pygame.init()

GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 25
PLAY_AREA_X = 25
PLAY_AREA_Y = 25

SCREEN_WIDTH = PLAY_AREA_X * 2 + GRID_WIDTH * CELL_SIZE + 150
SCREEN_HEIGHT = PLAY_AREA_Y * 2 + GRID_HEIGHT * CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
DARK_GRAY = (20, 20, 20)

COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
}

SHAPES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]],
        [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0]],
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]],
    ],
    'O': [
        [[1, 1],
         [1, 1]],
        [[1, 1],
         [1, 1]],
        [[1, 1],
         [1, 1]],
        [[1, 1],
         [1, 1]],
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]],
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]],
        [[0, 0, 0],
         [0, 1, 1],
         [1, 1, 0]],
        [[1, 0, 0],
         [1, 1, 0],
         [0, 1, 0]],
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 0],
         [0, 1, 1]],
        [[0, 1, 0],
         [1, 1, 0],
         [1, 0, 0]],
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]],
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]],
    ],
}

SHAPE_TYPES = list(SHAPES.keys())

SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}


class Piece:
    def __init__(self, shape_type):
        self.type = shape_type
        self.color = COLORS[shape_type]
        self.rotation = 0
        self.shapes = SHAPES[shape_type]
        self.x = GRID_WIDTH // 2 - len(self.shapes[0]) // 2
        self.y = 0

    def get_shape(self):
        return self.shapes[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def unrotate(self):
        self.rotation = (self.rotation - 1) % 4


class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.spawn_piece()

    def spawn_piece(self):
        if self.next_piece is None:
            self.next_piece = Piece(random.choice(SHAPE_TYPES))
        self.current_piece = self.next_piece
        self.next_piece = Piece(random.choice(SHAPE_TYPES))
        if self.check_collision(self.current_piece, 0, 0):
            self.game_over = True

    def check_collision(self, piece, dx, dy):
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

    def move(self, dx, dy):
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        self.current_piece.rotate()
        if self.check_collision(self.current_piece, 0, 0):
            kicks = [-1, 1, -2, 2]
            kicked = False
            for kick in kicks:
                if not self.check_collision(self.current_piece, kick, 0):
                    self.current_piece.x += kick
                    kicked = True
                    break
            if not kicked:
                self.current_piece.unrotate()

    def hard_drop(self):
        drop_distance = 0
        while not self.check_collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
            drop_distance += 1
        self.score += drop_distance * 2
        self.lock_piece()

    def lock_piece(self):
        shape = self.current_piece.get_shape()
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + r
                    grid_x = self.current_piece.x + c
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece.color
        self.clear_lines()
        if not self.game_over:
            self.spawn_piece()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = GRID_HEIGHT - len(new_grid)
        for _ in range(cleared):
            new_grid.insert(0, [None for _ in range(GRID_WIDTH)])
        self.grid = new_grid
        if cleared > 0:
            self.score += SCORE_TABLE.get(cleared, 0) * self.level
            self.lines_cleared += cleared
            self.level = self.lines_cleared // 10 + 1

    def get_drop_speed(self):
        return max(50, 500 - (self.level - 1) * 50)


def draw_grid(surface, tetris):
    pygame.draw.rect(surface, GRAY, (
        PLAY_AREA_X - 2,
        PLAY_AREA_Y - 2,
        GRID_WIDTH * CELL_SIZE + 4,
        GRID_HEIGHT * CELL_SIZE + 4
    ), 2)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(
                PLAY_AREA_X + x * CELL_SIZE,
                PLAY_AREA_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(surface, DARK_GRAY, rect, 1)
            if tetris.grid[y][x] is not None:
                pygame.draw.rect(surface, tetris.grid[y][x], rect.inflate(-2, -2))


def draw_piece(surface, piece, offset_x=0, offset_y=0):
    shape = piece.get_shape()
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    PLAY_AREA_X + (piece.x + c) * CELL_SIZE + offset_x,
                    PLAY_AREA_Y + (piece.y + r) * CELL_SIZE + offset_y,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(surface, piece.color, rect.inflate(-2, -2))


def draw_ghost_piece(surface, tetris):
    ghost = tetris.current_piece
    ghost_y = ghost.y
    while not tetris.check_collision(ghost, 0, ghost_y - ghost.y + 1):
        if tetris.check_collision(ghost, 0, ghost_y - ghost.y + 1):
            break
    temp_y = ghost.y
    drop_distance = 0
    while not tetris.check_collision(ghost, 0, drop_distance + 1):
        drop_distance += 1

    shape = ghost.get_shape()
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    PLAY_AREA_X + (ghost.x + c) * CELL_SIZE,
                    PLAY_AREA_Y + (temp_y + r + drop_distance) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                s = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2))
                s.set_alpha(80)
                s.fill(ghost.color)
                surface.blit(s, (rect.x + 1, rect.y + 1))


def draw_next_piece(surface, piece):
    info_x = PLAY_AREA_X + GRID_WIDTH * CELL_SIZE + 30
    info_y = PLAY_AREA_Y
    font = pygame.font.Font(None, 24)
    text = font.render("NEXT", True, WHITE)
    surface.blit(text, (info_x, info_y))

    box_size = 120
    box_rect = pygame.Rect(info_x, info_y + 30, box_size, box_size)
    pygame.draw.rect(surface, GRAY, box_rect, 2)

    shape = piece.get_shape()
    shape_h = len(shape)
    shape_w = len(shape[0])
    cell = 20
    offset_x = info_x + (box_size - shape_w * cell) // 2
    offset_y = info_y + 30 + (box_size - shape_h * cell) // 2

    for r, row in enumerate(shape):
        for c, cell_val in enumerate(row):
            if cell_val:
                rect = pygame.Rect(
                    offset_x + c * cell,
                    offset_y + r * cell,
                    cell,
                    cell
                )
                pygame.draw.rect(surface, piece.color, rect.inflate(-2, -2))


def draw_info(surface, tetris):
    info_x = PLAY_AREA_X + GRID_WIDTH * CELL_SIZE + 30
    info_y = PLAY_AREA_Y + 170
    font = pygame.font.Font(None, 24)

    score_text = font.render(f"SCORE", True, WHITE)
    score_val = font.render(f"{tetris.score}", True, WHITE)
    surface.blit(score_text, (info_x, info_y))
    surface.blit(score_val, (info_x, info_y + 25))

    level_text = font.render(f"LEVEL", True, WHITE)
    level_val = font.render(f"{tetris.level}", True, WHITE)
    surface.blit(level_text, (info_x, info_y + 65))
    surface.blit(level_val, (info_x, info_y + 90))

    lines_text = font.render(f"LINES", True, WHITE)
    lines_val = font.render(f"{tetris.lines_cleared}", True, WHITE)
    surface.blit(lines_text, (info_x, info_y + 130))
    surface.blit(lines_val, (info_x, info_y + 155))


def draw_game_over(surface, score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    font_big = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

    game_over_text = font_big.render("GAME OVER", True, (255, 80, 80))
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    restart_text = font_small.render("Press R to Restart", True, WHITE)

    surface.blit(game_over_text, (
        SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
        SCREEN_HEIGHT // 2 - 80
    ))
    surface.blit(score_text, (
        SCREEN_WIDTH // 2 - score_text.get_width() // 2,
        SCREEN_HEIGHT // 2
    ))
    surface.blit(restart_text, (
        SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
        SCREEN_HEIGHT // 2 + 60
    ))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    tetris = Tetris()
    fall_event = pygame.USEREVENT + 1
    pygame.time.set_timer(fall_event, tetris.get_drop_speed())

    last_speed = tetris.get_drop_speed()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if tetris.game_over:
                    if event.key == pygame.K_r:
                        tetris = Tetris()
                        pygame.time.set_timer(fall_event, tetris.get_drop_speed())
                        last_speed = tetris.get_drop_speed()
                else:
                    if event.key == pygame.K_LEFT:
                        tetris.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        tetris.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        if tetris.move(0, 1):
                            tetris.score += 1
                    elif event.key == pygame.K_UP:
                        tetris.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        tetris.hard_drop()

            if event.type == fall_event and not tetris.game_over:
                if not tetris.move(0, 1):
                    tetris.lock_piece()

                current_speed = tetris.get_drop_speed()
                if current_speed != last_speed:
                    pygame.time.set_timer(fall_event, current_speed)
                    last_speed = current_speed

        screen.fill(BLACK)
        draw_grid(screen, tetris)

        if not tetris.game_over:
            draw_ghost_piece(screen, tetris)
            draw_piece(screen, tetris.current_piece)

        draw_next_piece(screen, tetris.next_piece)
        draw_info(screen, tetris)

        if tetris.game_over:
            draw_game_over(screen, tetris.score)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
