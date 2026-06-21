import pygame
from constants import (
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, PLAY_AREA_X, PLAY_AREA_Y,
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY
)


class Renderer:
    def __init__(self, surface):
        self.surface = surface

    def clear(self):
        self.surface.fill(BLACK)

    def draw_grid(self, board):
        pygame.draw.rect(self.surface, GRAY, (
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
                pygame.draw.rect(self.surface, DARK_GRAY, rect, 1)
                if board.grid[y][x] is not None:
                    pygame.draw.rect(self.surface, board.grid[y][x], rect.inflate(-2, -2))

    def draw_piece(self, piece, offset_x=0, offset_y=0):
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
                    pygame.draw.rect(self.surface, piece.color, rect.inflate(-2, -2))

    def draw_ghost_piece(self, piece, board):
        drop_distance = 0
        while not board.check_collision(piece, 0, drop_distance + 1):
            drop_distance += 1

        shape = piece.get_shape()
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        PLAY_AREA_X + (piece.x + c) * CELL_SIZE,
                        PLAY_AREA_Y + (piece.y + r + drop_distance) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    s = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2))
                    s.set_alpha(80)
                    s.fill(piece.color)
                    self.surface.blit(s, (rect.x + 1, rect.y + 1))

    def _draw_preview_box(self, x, y, title, piece, can_use=True):
        font = pygame.font.Font(None, 24)
        text_color = WHITE if can_use else GRAY
        text = font.render(title, True, text_color)
        self.surface.blit(text, (x, y))

        box_size = 100
        box_rect = pygame.Rect(x, y + 30, box_size, box_size)
        border_color = GRAY if can_use else (30, 30, 30)
        pygame.draw.rect(self.surface, border_color, box_rect, 2)

        if piece is None:
            return

        shape = piece.get_shape()
        shape_h = len(shape)
        shape_w = len(shape[0])
        cell = 18
        offset_x = x + (box_size - shape_w * cell) // 2
        offset_y = y + 30 + (box_size - shape_h * cell) // 2

        for r, row in enumerate(shape):
            for c, cell_val in enumerate(row):
                if cell_val:
                    rect = pygame.Rect(
                        offset_x + c * cell,
                        offset_y + r * cell,
                        cell,
                        cell
                    )
                    if not can_use:
                        s = pygame.Surface((cell - 2, cell - 2))
                        s.set_alpha(60)
                        s.fill(piece.color)
                        self.surface.blit(s, (rect.x + 1, rect.y + 1))
                    else:
                        pygame.draw.rect(self.surface, piece.color, rect.inflate(-2, -2))

    def draw_hold_piece(self, piece, can_hold):
        info_x = PLAY_AREA_X + GRID_WIDTH * CELL_SIZE + 30
        info_y = PLAY_AREA_Y
        self._draw_preview_box(info_x, info_y, "HOLD", piece, can_hold)

    def draw_next_piece(self, piece):
        info_x = PLAY_AREA_X + GRID_WIDTH * CELL_SIZE + 30
        info_y = PLAY_AREA_Y + 150
        self._draw_preview_box(info_x, info_y, "NEXT", piece)

    def draw_info(self, score, level, lines_cleared):
        info_x = PLAY_AREA_X + GRID_WIDTH * CELL_SIZE + 30
        info_y = PLAY_AREA_Y + 300
        font = pygame.font.Font(None, 24)

        score_text = font.render(f"SCORE", True, WHITE)
        score_val = font.render(f"{score}", True, WHITE)
        self.surface.blit(score_text, (info_x, info_y))
        self.surface.blit(score_val, (info_x, info_y + 25))

        level_text = font.render(f"LEVEL", True, WHITE)
        level_val = font.render(f"{level}", True, WHITE)
        self.surface.blit(level_text, (info_x, info_y + 65))
        self.surface.blit(level_val, (info_x, info_y + 90))

        lines_text = font.render(f"LINES", True, WHITE)
        lines_val = font.render(f"{lines_cleared}", True, WHITE)
        self.surface.blit(lines_text, (info_x, info_y + 130))
        self.surface.blit(lines_val, (info_x, info_y + 155))

    def draw_game_over(self, score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.surface.blit(overlay, (0, 0))

        font_big = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)

        game_over_text = font_big.render("GAME OVER", True, (255, 80, 80))
        score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
        restart_text = font_small.render("Press R to Restart", True, WHITE)

        self.surface.blit(game_over_text, (
            SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
            SCREEN_HEIGHT // 2 - 80
        ))
        self.surface.blit(score_text, (
            SCREEN_WIDTH // 2 - score_text.get_width() // 2,
            SCREEN_HEIGHT // 2
        ))
        self.surface.blit(restart_text, (
            SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
            SCREEN_HEIGHT // 2 + 60
        ))

    def draw_paused(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.surface.blit(overlay, (0, 0))

        font_big = pygame.font.Font(None, 64)
        font_small = pygame.font.Font(None, 24)

        paused_text = font_big.render("PAUSED", True, WHITE)
        resume_text = font_small.render("Press P to Resume", True, WHITE)

        self.surface.blit(paused_text, (
            SCREEN_WIDTH // 2 - paused_text.get_width() // 2,
            SCREEN_HEIGHT // 2 - 40
        ))
        self.surface.blit(resume_text, (
            SCREEN_WIDTH // 2 - resume_text.get_width() // 2,
            SCREEN_HEIGHT // 2 + 40
        ))
