import pygame
import random
from enum import Enum

from constants import (
    SHAPE_TYPES, JLSTZ_WALL_KICKS, I_WALL_KICKS,
    FALL_EVENT_INTERVAL_BASE, FALL_EVENT_INTERVAL_MIN, FALL_EVENT_INTERVAL_DECREASE
)
from board import Board
from piece import Piece
from renderer import Renderer


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


class Game:
    def __init__(self, surface):
        self.renderer = Renderer(surface)
        self.board = Board()
        self.state = GameState.PLAYING
        self.current_piece = None
        self.next_piece = None
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_event = pygame.USEREVENT + 1
        self.last_speed = self._get_drop_speed()
        pygame.time.set_timer(self.fall_event, self.last_speed)
        self._spawn_piece()

    def reset(self):
        self.board.reset()
        self.current_piece = None
        self.next_piece = None
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.state = GameState.PLAYING
        self.last_speed = self._get_drop_speed()
        pygame.time.set_timer(self.fall_event, self.last_speed)
        self._spawn_piece()

    def _get_drop_speed(self):
        return max(FALL_EVENT_INTERVAL_MIN, FALL_EVENT_INTERVAL_BASE - (self.level - 1) * FALL_EVENT_INTERVAL_DECREASE)

    def _spawn_piece(self):
        if self.next_piece is None:
            self.next_piece = Piece(random.choice(SHAPE_TYPES))
        new_piece = self.next_piece
        if self.board.check_collision(new_piece, 0, 0):
            self.state = GameState.GAME_OVER
            return
        self.current_piece = new_piece
        self.next_piece = Piece(random.choice(SHAPE_TYPES))
        self.can_hold = True

    def _rotate_piece(self):
        piece = self.current_piece
        old_rot = piece.rotation
        piece.rotate()
        new_rot = piece.rotation

        if piece.type == 'I':
            kicks = I_WALL_KICKS.get((old_rot, new_rot), [(0, 0)])
        elif piece.type == 'O':
            kicks = [(0, 0)]
        else:
            kicks = JLSTZ_WALL_KICKS.get((old_rot, new_rot), [(0, 0)])

        kicked = False
        for dx, dy in kicks:
            if not self.board.check_collision(piece, dx, dy):
                piece.x += dx
                piece.y += dy
                kicked = True
                break
        if not kicked:
            piece.unrotate()

    def _hard_drop(self):
        drop_distance = 0
        while not self.board.check_collision(self.current_piece, 0, drop_distance + 1):
            drop_distance += 1
        self.current_piece.y += drop_distance
        self.score += drop_distance * 2
        self._lock_piece()

    def _lock_piece(self):
        if not self.board.lock_piece(self.current_piece):
            self.state = GameState.GAME_OVER
            return
        add_score, cleared = self.board.clear_lines(self.level)
        if cleared > 0:
            self.score += add_score
            self.lines_cleared += cleared
            self.level = self.lines_cleared // 10 + 1
            current_speed = self._get_drop_speed()
            if current_speed != self.last_speed:
                pygame.time.set_timer(self.fall_event, current_speed)
                self.last_speed = current_speed
        if self.state != GameState.GAME_OVER:
            self._spawn_piece()

    def _hold_piece(self):
        if not self.can_hold:
            return
        self.can_hold = False
        if self.held_piece is None:
            self.held_piece = Piece(self.current_piece.type)
            self._spawn_piece()
        else:
            temp_type = self.held_piece.type
            new_piece = Piece(temp_type)
            if self.board.check_collision(new_piece, 0, 0):
                self.state = GameState.GAME_OVER
                self.can_hold = True
                return
            self.held_piece = Piece(self.current_piece.type)
            self.current_piece = new_piece

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if self.state == GameState.GAME_OVER:
                if event.key == pygame.K_r:
                    self.reset()
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_p:
                    self.state = GameState.PLAYING
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_p:
                    self.state = GameState.PAUSED
                elif event.key == pygame.K_LEFT:
                    if not self.board.check_collision(self.current_piece, -1, 0):
                        self.current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if not self.board.check_collision(self.current_piece, 1, 0):
                        self.current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if not self.board.check_collision(self.current_piece, 0, 1):
                        self.current_piece.y += 1
                        self.score += 1
                elif event.key == pygame.K_UP:
                    self._rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self._hard_drop()
                elif event.key == pygame.K_c:
                    self._hold_piece()

        if event.type == self.fall_event and self.state == GameState.PLAYING:
            if self.board.check_collision(self.current_piece, 0, 1):
                self._lock_piece()
            else:
                self.current_piece.y += 1

        return True

    def render(self):
        self.renderer.clear()
        self.renderer.draw_grid(self.board)

        if self.state == GameState.PLAYING:
            self.renderer.draw_ghost_piece(self.current_piece, self.board)
            self.renderer.draw_piece(self.current_piece)

        self.renderer.draw_hold_piece(self.held_piece, self.can_hold)
        self.renderer.draw_next_piece(self.next_piece)
        self.renderer.draw_info(self.score, self.level, self.lines_cleared)

        if self.state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.score)
        elif self.state == GameState.PAUSED:
            self.renderer.draw_paused()
