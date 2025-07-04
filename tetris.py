import pygame
import random
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
TITLE_GRAY = (180, 180, 180)  # Новый цвет для заголовка
COLORS = [
    (0, 240, 240),  # Cyan
    (0, 0, 240),    # Blue
    (240, 160, 0),  # Orange
    (240, 240, 0),  # Yellow
    (0, 240, 0),    # Green
    (160, 0, 240),  # Purple
    (240, 0, 0)     # Red
]

# Game settings
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PREVIEW_SIZE = 4

# Calculate window dimensions
GAME_WIDTH = BLOCK_SIZE * GRID_WIDTH
GAME_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
SIDEBAR_WIDTH = 200
WINDOW_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = GAME_HEIGHT

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1],      # J
     [0, 0, 1]],
    [[1, 1, 1],      # L
     [1, 0, 0]],
    [[1, 1],         # O
     [1, 1]],
    [[0, 1, 1],      # S
     [1, 1, 0]],
    [[1, 1, 1],      # T
     [0, 1, 0]],
    [[1, 1, 0],      # Z
     [0, 1, 1]]
]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Тетрис")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)  # Больший шрифт для заголовка
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # Initial speed in seconds

    def new_piece(self) -> dict:
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }

    def valid_move(self, piece: dict, x_offset: int = 0, y_offset: int = 0) -> bool:
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + x_offset
                    new_y = piece['y'] + y + y_offset
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def rotate_piece(self, piece: dict) -> None:
        old_shape = piece['shape']
        piece['shape'] = list(zip(*reversed(old_shape)))
        if not self.valid_move(piece):
            piece['shape'] = old_shape

    def lock_piece(self, piece: dict) -> None:
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece['y'] + y][piece['x'] + x] = piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def clear_lines(self) -> None:
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        num_lines = len(lines_to_clear)
        if num_lines:
            self.lines_cleared += num_lines
            self.score += [0, 100, 300, 500, 800][num_lines] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)

    def draw_grid(self) -> None:
        # Draw game area background
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, GAME_WIDTH, GAME_HEIGHT))
        
        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x] or BLACK
                pygame.draw.rect(self.screen, color,
                               (x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1,
                                BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        # Draw current piece
        if self.current_piece:
            for y, row in enumerate(self.current_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.current_piece['color'],
                                       ((self.current_piece['x'] + x) * BLOCK_SIZE + 1,
                                        (self.current_piece['y'] + y) * BLOCK_SIZE + 1,
                                        BLOCK_SIZE - 2, BLOCK_SIZE - 2))

    def draw_sidebar(self) -> None:
        sidebar_x = GAME_WIDTH + 10
        
        # Draw next piece preview
        preview_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(preview_text, (sidebar_x, 20))
        
        preview_offset_x = sidebar_x + (SIDEBAR_WIDTH - PREVIEW_SIZE * BLOCK_SIZE) // 2
        preview_offset_y = 60
        
        for y, row in enumerate(self.next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece['color'],
                                   (preview_offset_x + x * BLOCK_SIZE,
                                    preview_offset_y + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        # Draw score and level
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        self.screen.blit(score_text, (sidebar_x, 200))
        self.screen.blit(level_text, (sidebar_x, 240))
        self.screen.blit(lines_text, (sidebar_x, 280))

        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, WHITE)
            self.screen.blit(game_over_text, (sidebar_x, 350))
        elif self.paused:
            pause_text = self.font.render("Paused", True, WHITE)
            self.screen.blit(pause_text, (sidebar_x, 350))


    def run(self) -> None:
        running = True
        last_fall = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_fall) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.game_over and not self.paused and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, x_offset=-1):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, x_offset=1):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, y_offset=1):
                            self.current_piece['y'] += 1
                    elif event.key == pygame.K_UP:
                        self.rotate_piece(self.current_piece)
                    elif event.key == pygame.K_SPACE:
                        while self.valid_move(self.current_piece, y_offset=1):
                            self.current_piece['y'] += 1
                        self.lock_piece(self.current_piece)
                        last_fall = current_time
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                        last_fall = current_time

            if not self.game_over and not self.paused:
                if delta_time > self.fall_speed:
                    if self.valid_move(self.current_piece, y_offset=1):
                        self.current_piece['y'] += 1
                    else:
                        self.lock_piece(self.current_piece)
                    last_fall = current_time

            # Draw everything
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_sidebar()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    game = Tetris()
    game.run()