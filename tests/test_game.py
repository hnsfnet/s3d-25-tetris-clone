import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
import unittest

mock_pygame = MagicMock()
mock_pygame.USEREVENT = 24
mock_pygame.QUIT = 256
mock_pygame.KEYDOWN = 768
mock_pygame.K_r = 114
mock_pygame.K_p = 112
mock_pygame.K_LEFT = 276
mock_pygame.K_RIGHT = 275
mock_pygame.K_DOWN = 274
mock_pygame.K_UP = 273
mock_pygame.K_SPACE = 32
mock_pygame.K_c = 99
mock_pygame.Rect = lambda *args: MagicMock()
mock_pygame.Surface = lambda *args, **kwargs: MagicMock()
mock_pygame.draw.rect = MagicMock()
mock_pygame.time.set_timer = MagicMock()

mock_font_module = MagicMock()
mock_font_module.Font.return_value.render.return_value = MagicMock(get_width=lambda: 100, get_height=lambda: 30)
mock_pygame.font = mock_font_module

with patch.dict('sys.modules', {'pygame': mock_pygame, 'pygame.font': mock_font_module}):
    from game import Game, GameState
    from constants import (
        GRID_WIDTH, GRID_HEIGHT, COLORS,
        FALL_EVENT_INTERVAL_BASE, FALL_EVENT_INTERVAL_MIN, FALL_EVENT_INTERVAL_DECREASE
    )
    from piece import Piece


class MockEvent:
    def __init__(self, event_type, key=None):
        self.type = event_type
        self.key = key


class TestGameState(unittest.TestCase):
    def test_game_state_values(self):
        self.assertEqual(GameState.MENU.value, 1)
        self.assertEqual(GameState.PLAYING.value, 2)
        self.assertEqual(GameState.PAUSED.value, 3)
        self.assertEqual(GameState.GAME_OVER.value, 4)


class TestGameInit(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def test_initial_state(self):
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)
        self.assertEqual(self.game.lines_cleared, 0)
        self.assertTrue(self.game.can_hold)
        self.assertIsNotNone(self.game.current_piece)
        self.assertIsNotNone(self.game.next_piece)

    def test_initial_speed(self):
        self.assertEqual(self.game.last_speed, FALL_EVENT_INTERVAL_BASE)
        mock_pygame.time.set_timer.assert_called()

    def test_timer_set_on_init(self):
        self.assertEqual(mock_pygame.time.set_timer.call_count, 1)


class TestGameScoring(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def _fill_rows(self, start_row, count):
        for r in range(start_row, start_row + count):
            for c in range(GRID_WIDTH):
                self.game.board.grid[r][c] = COLORS['T']

    def test_score_single_line(self):
        initial_score = self.game.score
        initial_lines = self.game.lines_cleared
        self._fill_rows(GRID_HEIGHT - 1, 1)
        add_score, cleared = self.game.board.clear_lines(self.game.level)
        self.assertEqual(add_score, 100)
        self.assertEqual(cleared, 1)
        self.assertEqual(self.game.lines_cleared, initial_lines)

    def test_score_double_line(self):
        self._fill_rows(GRID_HEIGHT - 2, 2)
        add_score, cleared = self.game.board.clear_lines(self.game.level)
        self.assertEqual(add_score, 300)
        self.assertEqual(cleared, 2)

    def test_score_triple_line(self):
        self._fill_rows(GRID_HEIGHT - 3, 3)
        add_score, cleared = self.game.board.clear_lines(self.game.level)
        self.assertEqual(add_score, 500)
        self.assertEqual(cleared, 3)

    def test_score_tetris(self):
        self._fill_rows(GRID_HEIGHT - 4, 4)
        add_score, cleared = self.game.board.clear_lines(self.game.level)
        self.assertEqual(add_score, 800)
        self.assertEqual(cleared, 4)

    def test_score_with_level_multiplier(self):
        self._fill_rows(GRID_HEIGHT - 1, 1)
        add_score, cleared = self.game.board.clear_lines(3)
        self.assertEqual(add_score, 300)

    def test_hard_drop_score(self):
        self.game.current_piece = Piece('O')
        self.game.current_piece.x = 0
        self.game.current_piece.y = 0
        initial_score = self.game.score
        self.game._hard_drop()
        expected_drop = GRID_HEIGHT - 2
        self.assertEqual(self.game.score - initial_score, expected_drop * 2)

    def test_soft_drop_score(self):
        initial_score = self.game.score
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_DOWN)
        self.game.handle_event(event)
        self.assertEqual(self.game.score - initial_score, 1)


class TestGameLevelProgression(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def _clear_lines(self, count):
        for c in range(GRID_WIDTH):
            for r in range(GRID_HEIGHT - count, GRID_HEIGHT):
                self.game.board.grid[r][c] = COLORS['T']
        add_score, cleared = self.game.board.clear_lines(self.game.level)
        self.game.score += add_score
        self.game.lines_cleared += cleared
        self.game.level = self.game.lines_cleared // 10 + 1

    def test_initial_level(self):
        self.assertEqual(self.game.level, 1)

    def test_level_up_at_10_lines(self):
        for _ in range(5):
            self._clear_lines(2)
        self.assertEqual(self.game.lines_cleared, 10)
        self.assertEqual(self.game.level, 2)

    def test_level_up_at_20_lines(self):
        for _ in range(10):
            self._clear_lines(2)
        self.assertEqual(self.game.lines_cleared, 20)
        self.assertEqual(self.game.level, 3)

    def test_level_up_with_tetris(self):
        for _ in range(3):
            self._clear_lines(4)
        self.assertEqual(self.game.lines_cleared, 12)
        self.assertEqual(self.game.level, 2)


class TestGameDropSpeed(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def test_get_drop_speed_level_1(self):
        self.game.level = 1
        self.assertEqual(self.game._get_drop_speed(), FALL_EVENT_INTERVAL_BASE)

    def test_get_drop_speed_level_2(self):
        self.game.level = 2
        expected = FALL_EVENT_INTERVAL_BASE - FALL_EVENT_INTERVAL_DECREASE
        self.assertEqual(self.game._get_drop_speed(), expected)

    def test_get_drop_speed_level_5(self):
        self.game.level = 5
        expected = FALL_EVENT_INTERVAL_BASE - 4 * FALL_EVENT_INTERVAL_DECREASE
        self.assertEqual(self.game._get_drop_speed(), expected)

    def test_get_drop_speed_minimum(self):
        self.game.level = 100
        self.assertEqual(self.game._get_drop_speed(), FALL_EVENT_INTERVAL_MIN)

    def test_speed_updates_on_level_up(self):
        initial_speed = self.game.last_speed
        mock_pygame.reset_mock()
        for c in range(GRID_WIDTH):
            for r in range(GRID_HEIGHT - 10, GRID_HEIGHT):
                self.game.board.grid[r][c] = COLORS['T']
        self.game.current_piece.y = -10
        self.game._lock_piece()
        self.assertNotEqual(self.game.last_speed, initial_speed)
        self.assertEqual(mock_pygame.time.set_timer.call_count, 1)


class TestGamePause(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def test_pause_from_playing(self):
        self.assertEqual(self.game.state, GameState.PLAYING)
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_p)
        self.game.handle_event(event)
        self.assertEqual(self.game.state, GameState.PAUSED)

    def test_resume_from_paused(self):
        self.game.state = GameState.PAUSED
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_p)
        self.game.handle_event(event)
        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_no_movement_when_paused(self):
        self.game.state = GameState.PAUSED
        initial_x = self.game.current_piece.x
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_LEFT)
        self.game.handle_event(event)
        self.assertEqual(self.game.current_piece.x, initial_x)

    def test_p_key_toggle(self):
        for _ in range(5):
            event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_p)
            self.game.handle_event(event)
        self.assertEqual(self.game.state, GameState.PLAYING)


class TestGameOver(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def test_game_over_on_spawn_collision(self):
        for c in range(GRID_WIDTH):
            self.game.board.grid[1][c] = COLORS['T']
        self.game._spawn_piece()
        self.assertEqual(self.game.state, GameState.GAME_OVER)

    def test_game_over_on_lock_outside_top(self):
        self.game.current_piece = Piece('O')
        self.game.current_piece.x = 0
        self.game.current_piece.y = -2
        self.game._lock_piece()
        self.assertEqual(self.game.state, GameState.GAME_OVER)

    def test_restart_after_game_over(self):
        self.game.state = GameState.GAME_OVER
        self.game.score = 1000
        self.game.level = 5
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_r)
        self.game.handle_event(event)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)

    def test_no_restart_when_not_game_over(self):
        initial_score = self.game.score
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_r)
        self.game.handle_event(event)
        self.assertEqual(self.game.score, initial_score)


class TestGameQuit(unittest.TestCase):
    def setUp(self):
        mock_pygame.reset_mock()
        self.mock_surface = MagicMock()
        self.game = Game(self.mock_surface)

    def test_quit_event_returns_false(self):
        event = MockEvent(mock_pygame.QUIT)
        result = self.game.handle_event(event)
        self.assertFalse(result)

    def test_other_events_return_true(self):
        event = MockEvent(mock_pygame.KEYDOWN, mock_pygame.K_LEFT)
        result = self.game.handle_event(event)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
