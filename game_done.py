import pygame
import sys
import random
import copy
import time

# Khởi tạo các biến toàn cục
WIDTH, HEIGHT = 1500, 750
GRID_SIZE = 4
GRID_SIZE_MIN = 3
GRID_SIZE_MAX = 8
LINE_WIDTH = 5
DOT_RADIUS = 5
MARGIN = 50
start_time = 0
player1_name = "Player 1"
player2_name = "Player 2"
first_player = 1
CELL_SIZE = 0
offset_x = 0
offset_y = 0
player1_time = 30
player2_time = 30
last_turn_time = 0
is_pvp = False
current_player = 1

# Khởi tạo Pygame
pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)
pygame.display.set_caption("Dots and Boxes")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 200, 255)
PASTEL_GREEN = (150, 255, 150)
HOVER_COLOR = (255, 200, 100)
DARK_GREEN = (0, 150, 100)

# Font chữ
pygame.font.init()
title_font = pygame.font.Font(None, 80)
button_font = pygame.font.Font(None, 48)
label_font = pygame.font.Font(None, 40)

# Dữ liệu trò chơi
horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]

# Lớp Board để quản lý cấu trúc half-edge và trạng thái trò chơi
class Board:
    def __init__(self, grid_size, h_lines, v_lines, boxes):
        self.grid_size = grid_size
        self.h_lines = [row[:] for row in h_lines]
        self.v_lines = [row[:] for row in v_lines]
        self.boxes = [row[:] for row in boxes]
        self.total_half_edges = 2 * (grid_size * (grid_size - 1) + (grid_size - 1) * grid_size)
        self.edges = {}  # Lưu trạng thái cạnh: (type, row, col) -> player
        self.init_edges()

    def init_edges(self):
        # Khởi tạo các cạnh từ horizontal_lines và vertical_lines
        for row in range(self.grid_size):
            for col in range(self.grid_size - 1):
                if self.h_lines[row][col]:
                    self.edges[("h", row, col)] = self.h_lines[row][col]
        for row in range(self.grid_size - 1):
            for col in range(self.grid_size):
                if self.v_lines[row][col]:
                    self.edges[("v", row, col)] = self.v_lines[row][col]

    def copy(self):
        return Board(self.grid_size, self.h_lines, self.v_lines, self.boxes)

    def get_available_moves(self):
        moves = []
        for row in range(self.grid_size):
            for col in range(self.grid_size - 1):
                if not ("h", row, col) in self.edges:
                    moves.append(("h", row, col))
        for row in range(self.grid_size - 1):
            for col in range(self.grid_size):
                if not ("v", row, col) in self.edges:
                    moves.append(("v", row, col))
        return moves

    def make_move(self, move, player):
        move_type, row, col = move
        self.edges[move, row, col] = player
        if move_type == "h":
            self.h_lines[row][col] = player
        else:
            self.v_lines[row][col] = player
        return self.check_box_completion(player)

    def check_box_completion(self, player):
        completed = False
        for row in range(self.grid_size - 1):
            for col in range(self.grid_size - 1):
                if (self.h_lines[row][col] and self.h_lines[row + 1][col] and
                        self.v_lines[row][col] and self.v_lines[row][col + 1] and
                        self.boxes[row][col] == 0):
                    self.boxes[row][col] = player
                    completed = True
        return completed

    def evaluate(self):
        # Hàm đánh giá: số ô của AI - số ô của người chơi
        player1_score = sum(row.count(1) for row in self.boxes)
        player2_score = sum(row.count(2) for row in self.boxes)
        return player2_score - player1_score

    def is_game_over(self):
        return all(all(cell > 0 for cell in row) for row in self.boxes)

# Hàm minimax với cắt tỉa alpha-beta
def minimax(board, depth, alpha, beta, maximizing_player, max_depth=4):
    if depth == max_depth or board.is_game_over():
        return board.evaluate(), None

    moves = board.get_available_moves()
    if not moves:
        return board.evaluate(), None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in moves:
            new_board = board.copy()
            completed = new_board.make_move(move, 2)  # AI là player 2
            if completed:
                eval_score, _ = minimax(new_board, depth, alpha, beta, True, max_depth)
            else:
                eval_score, _ = minimax(new_board, depth + 1, alpha, beta, False, max_depth)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in moves:
            new_board = board.copy()
            completed = new_board.make_move(move, 1)  # Người chơi là player 1
            if completed:
                eval_score, _ = minimax(new_board, depth, alpha, beta, False, max_depth)
            else:
                eval_score, _ = minimax(new_board, depth + 1, alpha, beta, True, max_depth)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

# Chiến lược tìm nước đi tốt nhất
def ai_move():
    global current_player, player1_time, player2_time, last_turn_time
    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000
    if current_player == 2:
        player2_time = max(0, player2_time - current_turn_sec)

    board = Board(GRID_SIZE, horizontal_lines, vertical_lines, boxes)

    # Ưu tiên nước đi hoàn thành ô
    almost_completed = []
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            sides_filled = sum([
                1 if ("h", row, col) in board.edges else 0,
                1 if ("h", row + 1, col) in board.edges else 0,
                1 if ("v", row, col) in board.edges else 0,
                1 if ("v", row, col + 1) in board.edges else 0
            ])
            if sides_filled == 3:
                if not ("h", row, col) in board.edges:
                    almost_completed.append(("h", row, col))
                elif not ("h", row + 1, col) in board.edges:
                    almost_completed.append(("h", row + 1, col))
                elif not ("v", row, col) in board.edges:
                    almost_completed.append(("v", row, col))
                elif not ("v", row, col + 1) in board.edges:
                    almost_completed.append(("v", row, col + 1))

    if almost_completed:
        move = random.choice(almost_completed)
    else:
        # Sử dụng minimax để tìm nước đi tốt nhất
        _, move = minimax(board, 0, float('-inf'), float('inf'), True)
        if not move:
            # Nếu không tìm được nước đi, chọn ngẫu nhiên
            available_moves = board.get_available_moves()
            move = random.choice(available_moves) if available_moves else None

    if move:
        move_type, row, col = move
        if move_type == "h":
            horizontal_lines[row][col] = current_player
        else:
            vertical_lines[row][col] = current_player
        if not check_box_completion():
            current_player = 3 - current_player
            last_turn_time = pygame.time.get_ticks()

def draw_gradient(surface, color1, color2, rect):
    x, y, w, h = rect
    color1 = pygame.Color(color1)
    color2 = pygame.Color(color2)
    for i in range(h):
        ratio = i / h
        r = int(color1.r + (color2.r - color1.r) * ratio)
        g = int(color1.g + (color2.g - color1.g) * ratio)
        b = int(color1.b + (color2.b - color1.b) * ratio)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))

def show_how_to_play_screen():
    running = True
    while running:
        draw_gradient(display, LIGHT_BLUE, WHITE, (0, 0, WIDTH, HEIGHT + MARGIN))
        title = title_font.render("How to Play Dots and Boxes", True, BLACK)
        instructions = [
            "1. Two players take turns drawing a line connecting",
            "   two adjacent dots (horizontal or vertical).",
            "2. If a player completes the fourth side of a 1x1 box,",
            "   they score a point and take another turn.",
            "3. The game ends when all boxes are completed.",
            "4. The player with the higher score wins!",
            "",
            "Click anywhere to return to the main menu..."
        ]
        display.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        for i, line in enumerate(instructions):
            line_surface = label_font.render(line, True, BLACK)
            display.blit(line_surface, (WIDTH // 2 - line_surface.get_width() // 2, 150 + i * 45))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = False

def draw_menu():
    mouse_pos = pygame.mouse.get_pos()
    draw_gradient(display, LIGHT_BLUE, WHITE, (0, 0, WIDTH, HEIGHT + MARGIN))
    title = title_font.render("Dots and Boxes", True, BLACK)
    pvp_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 120, 400, 60)
    pve_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 30, 400, 60)
    how_to_play_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 60, 400, 60)

    pvp_color = HOVER_COLOR if pvp_rect.collidepoint(mouse_pos) else PASTEL_GREEN
    pve_color = HOVER_COLOR if pve_rect.collidepoint(mouse_pos) else PASTEL_GREEN
    how_to_play_color = HOVER_COLOR if how_to_play_rect.collidepoint(mouse_pos) else PASTEL_GREEN

    pygame.draw.rect(display, pvp_color, pvp_rect, border_radius=10)
    pygame.draw.rect(display, pve_color, pve_rect, border_radius=10)
    pygame.draw.rect(display, how_to_play_color, how_to_play_rect, border_radius=10)
    pygame.draw.rect(display, BLACK, pvp_rect, 2, border_radius=10)
    pygame.draw.rect(display, BLACK, pve_rect, 2, border_radius=10)
    pygame.draw.rect(display, BLACK, how_to_play_rect, 2, border_radius=10)

    pvp_text = button_font.render("Player vs Player", True, BLACK)
    pve_text = button_font.render("Player vs AI", True, BLACK)
    how_to_play_text = button_font.render("How to Play", True, BLACK)

    display.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    display.blit(pvp_text, (WIDTH // 2 - pvp_text.get_width() // 2, HEIGHT // 2 - 105))
    display.blit(pve_text, (WIDTH // 2 - pve_text.get_width() // 2, HEIGHT // 2 - 15))
    display.blit(how_to_play_text, (WIDTH // 2 - how_to_play_text.get_width() // 2, HEIGHT // 2 + 75))

    pygame.display.update()
    return pvp_rect, pve_rect, how_to_play_rect

def options_menu():
    global player1_name, player2_name, first_player, is_pvp, GRID_SIZE, horizontal_lines, vertical_lines, boxes
    input_active = None
    player1_input = player1_name
    player2_input = player2_name

    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_gradient(display, LIGHT_BLUE, WHITE, (0, 0, WIDTH, HEIGHT + MARGIN))
        title = title_font.render("Game Options", True, BLACK)

        player1_label = label_font.render("Player 1 Name:", True, BLACK)
        player1_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 200, 500, 50)
        player1_display = player1_input if player1_input.strip() != "" else "Player 1"
        player1_input_surface = button_font.render(player1_display, True, BLACK)
        player1_border_color = BLACK if input_active == 'player1' else DARK_GRAY
        pygame.draw.rect(display, WHITE, player1_rect, border_radius=10)
        pygame.draw.rect(display, player1_border_color, player1_rect, 3, border_radius=10)

        player2_label = label_font.render("Player 2/AI Name:", True, BLACK)
        player2_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 120, 500, 50)
        player2_display = player2_input if player2_input.strip() != "" else ("Player 2" if is_pvp else "AI")
        player2_input_surface = button_font.render(player2_display, True, BLACK)
        player2_border_color = BLACK if input_active == 'player2' else DARK_GRAY
        pygame.draw.rect(display, WHITE, player2_rect, border_radius=10)
        pygame.draw.rect(display, player2_border_color, player2_rect, 3, border_radius=10)

        first_player_label = label_font.render("First Move:", True, BLACK)
        player1_move_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 40, 240, 60)
        player2_move_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 - 40, 240, 60)
        player1_move_color = BLUE if first_player == 1 else PASTEL_GREEN
        player2_move_color = BLUE if first_player == 2 else PASTEL_GREEN
        if player1_move_rect.collidepoint(mouse_pos):
            player1_move_color = HOVER_COLOR
        if player2_move_rect.collidepoint(mouse_pos):
            player2_move_color = HOVER_COLOR
        pygame.draw.rect(display, DARK_GRAY, (player1_move_rect.x + 3, player1_move_rect.y + 3, 240, 60), border_radius=10)
        pygame.draw.rect(display, DARK_GRAY, (player2_move_rect.x + 3, player2_move_rect.y + 3, 240, 60), border_radius=10)
        pygame.draw.rect(display, player1_move_color, player1_move_rect, border_radius=10)
        pygame.draw.rect(display, player2_move_color, player2_move_rect, border_radius=10)
        pygame.draw.rect(display, BLACK, player1_move_rect, 2, border_radius=10)
        pygame.draw.rect(display, BLACK, player2_move_rect, 2, border_radius=10)
        player1_move_text = button_font.render(player1_input if player1_input.strip() != "" else "Player 1", True, BLACK)
        player2_move_text = button_font.render(player2_input if player2_input.strip() != "" else ("Player 2" if is_pvp else "AI"), True, BLACK)

        grid_size_label = label_font.render("Grid Size:", True, BLACK)
        decrease_grid_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 + 50, 60, 60)
        grid_display_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 50, 240, 60)
        increase_grid_rect = pygame.Rect(WIDTH // 2 + 190, HEIGHT // 2 + 50, 60, 60)
        decrease_color = PASTEL_GREEN if not decrease_grid_rect.collidepoint(mouse_pos) else HOVER_COLOR
        increase_color = PASTEL_GREEN if not increase_grid_rect.collidepoint(mouse_pos) else HOVER_COLOR
        pygame.draw.rect(display, DARK_GRAY, (decrease_grid_rect.x + 3, decrease_grid_rect.y + 3, 60, 60), border_radius=10)
        pygame.draw.rect(display, DARK_GRAY, (increase_grid_rect.x + 3, increase_grid_rect.y + 3, 60, 60), border_radius=10)
        pygame.draw.rect(display, decrease_color, decrease_grid_rect, border_radius=10)
        pygame.draw.rect(display, WHITE, grid_display_rect, border_radius=10)
        pygame.draw.rect(display, increase_color, increase_grid_rect, border_radius=10)
        pygame.draw.rect(display, BLACK, decrease_grid_rect, 2, border_radius=10)
        pygame.draw.rect(display, BLACK, grid_display_rect, 3, border_radius=10)
        pygame.draw.rect(display, BLACK, increase_grid_rect, 2, border_radius=10)
        decrease_text = button_font.render("-", True, BLACK)
        grid_size_text = button_font.render(str(GRID_SIZE), True, BLACK)
        increase_text = button_font.render("+", True, BLACK)

        back_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 + 140, 240, 60)
        back_color = PASTEL_GREEN if not back_rect.collidepoint(mouse_pos) else HOVER_COLOR
        pygame.draw.rect(display, DARK_GRAY, (back_rect.x + 3, back_rect.y + 3, 240, 60), border_radius=10)
        pygame.draw.rect(display, back_color, back_rect, border_radius=10)
        pygame.draw.rect(display, BLACK, back_rect, 2, border_radius=10)
        back_text = button_font.render("Back", True, BLACK)

        play_game_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 140, 240, 60)
        play_game_color = DARK_GREEN if not play_game_rect.collidepoint(mouse_pos) else HOVER_COLOR
        pygame.draw.rect(display, DARK_GRAY, (play_game_rect.x + 3, play_game_rect.y + 3, 240, 60), border_radius=10)
        pygame.draw.rect(display, play_game_color, play_game_rect, border_radius=10)
        pygame.draw.rect(display, BLACK, play_game_rect, 2, border_radius=10)
        play_game_text = button_font.render("Play Game", True, WHITE)

        display.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4 - 150))
        display.blit(player1_label, (WIDTH // 2 - 250, HEIGHT // 2 - 240))
        display.blit(player1_input_surface, (WIDTH // 2 - 240, HEIGHT // 2 - 190))
        display.blit(player2_label, (WIDTH // 2 - 250, HEIGHT // 2 - 145))
        display.blit(player2_input_surface, (WIDTH // 2 - 240, HEIGHT // 2 - 110))
        display.blit(first_player_label, (WIDTH // 2 - 250, HEIGHT // 2 - 70))
        display.blit(player1_move_text, (WIDTH // 2 - 240 + (240 - player1_move_text.get_width()) // 2, HEIGHT // 2 - 25))
        display.blit(player2_move_text, (WIDTH // 2 + 20 + (240 - player2_move_text.get_width()) // 2, HEIGHT // 2 - 25))
        display.blit(grid_size_label, (WIDTH // 2 - 250, HEIGHT // 2 + 20))
        display.blit(decrease_text, (decrease_grid_rect.x + 20, decrease_grid_rect.y + 10))
        display.blit(grid_size_text, (grid_display_rect.x + (240 - grid_size_text.get_width()) // 2, grid_display_rect.y + 10))
        display.blit(increase_text, (increase_grid_rect.x + 20, increase_grid_rect.y + 10))
        display.blit(back_text, (WIDTH // 2 - 240 + (240 - back_text.get_width()) // 2, HEIGHT // 2 + 155))
        display.blit(play_game_text, (WIDTH // 2 + 20 + (240 - play_game_text.get_width()) // 2, HEIGHT // 2 + 155))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if player1_rect.collidepoint(event.pos):
                    input_active = 'player1'
                elif player2_rect.collidepoint(event.pos):
                    input_active = 'player2'
                elif player1_move_rect.collidepoint(event.pos):
                    first_player = 1
                elif player2_move_rect.collidepoint(event.pos):
                    first_player = 2
                elif decrease_grid_rect.collidepoint(event.pos):
                    if GRID_SIZE > GRID_SIZE_MIN:
                        GRID_SIZE -= 1
                        horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
                        vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
                        boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]
                elif increase_grid_rect.collidepoint(event.pos):
                    if GRID_SIZE < GRID_SIZE_MAX:
                        GRID_SIZE += 1
                        horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
                        vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
                        boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]
                elif back_rect.collidepoint(event.pos):
                    menu()
                    return
                elif play_game_rect.collidepoint(event.pos):
                    player1_name = player1_input if player1_input.strip() != "" else "Player 1"
                    player2_name = player2_input if player2_input.strip() != "" else ("Player 2" if is_pvp else "AI")
                    return
                else:
                    input_active = None
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = None
                elif event.key == pygame.K_BACKSPACE:
                    if input_active == 'player1':
                        player1_input = player1_input[:-1]
                    elif input_active == 'player2':
                        player2_input = player2_input[:-1]
                elif event.unicode.isprintable() and len(player1_input if input_active == 'player1' else player2_input) < 15:
                    if input_active == 'player1':
                        player1_input += event.unicode
                    elif input_active == 'player2':
                        player2_input += event.unicode

def menu():
    global is_pvp, current_player
    while True:
        pvp_rect, pve_rect, how_to_play_rect = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_rect.collidepoint(event.pos):
                    is_pvp = True
                    options_menu()
                    current_player = first_player
                    return
                elif pve_rect.collidepoint(event.pos):
                    is_pvp = False
                    options_menu()
                    current_player = first_player
                    return
                elif how_to_play_rect.collidepoint(event.pos):
                    show_how_to_play_screen()

def draw_grid():
    global start_time, CELL_SIZE, offset_x, offset_y, player1_time, player2_time, last_turn_time
    mouse_pos = pygame.mouse.get_pos()
    display.fill(WHITE)
    HEADER_HEIGHT = 60

    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000
    if current_player == 1:
        player1_time = max(0, 30 - current_turn_sec)
    else:
        player2_time = max(0, 30 - current_turn_sec)

    player1_time_text = label_font.render(f"{player1_name} Time: {int(player1_time)}s", True, RED if current_player == 1 else BLACK)
    player2_time_text = label_font.render(f"{player2_name} Time: {int(player2_time)}s", True, BLUE if current_player == 2 else BLACK)

    red_score, blue_score = calculate_scores()
    player1_text = label_font.render(f"{player1_name}: {red_score}", True, RED)
    player2_text = label_font.render(f"{player2_name}: {blue_score}", True, BLUE)
    separator_text = label_font.render(" | ", True, BLACK)

    return_menu_rect = pygame.Rect(WIDTH - 260, HEIGHT - 70, 240, 50)
    return_menu_color = (100, 180, 255) if not return_menu_rect.collidepoint(mouse_pos) else (255, 220, 100)
    pygame.draw.rect(display, GRAY, (0, 0, WIDTH, HEADER_HEIGHT))
    pygame.draw.rect(display, DARK_GRAY, (return_menu_rect.x + 3, return_menu_rect.y + 3, 240, 50), border_radius=15)
    draw_gradient(display, return_menu_color, (50, 130, 200) if return_menu_color == (100, 180, 255) else (220, 180, 60), return_menu_rect)
    pygame.draw.rect(display, BLACK, return_menu_rect, 2, border_radius=15)
    try:
        return_menu_font = pygame.font.Font("Roboto.ttf", 28)
    except:
        return_menu_font = pygame.font.Font(None, 28)
    return_menu_text = return_menu_font.render("Return to Menu", True, WHITE)
    return_menu_text_x = WIDTH - 260 + (240 - return_menu_text.get_width()) // 2
    return_menu_text_y = HEIGHT - 70 + (50 - return_menu_text.get_height()) // 2

    player1_width = player1_text.get_width()
    player2_width = player2_text.get_width()
    separator_width = separator_text.get_width()
    player1_time_width = player1_time_text.get_width()
    player2_time_width = player2_time_text.get_width()

    total_score_width = player1_width + separator_width + player2_width
    score_x = (WIDTH - total_score_width) // 2
    text_y = (HEADER_HEIGHT - player1_text.get_height()) // 2

    player1_time_x = 20
    player2_time_x = WIDTH - player2_time_width - 20

    display.blit(player1_text, (score_x, text_y))
    display.blit(separator_text, (score_x + player1_width, text_y))
    display.blit(player2_text, (score_x + player1_width + separator_width, text_y))
    display.blit(player1_time_text, (player1_time_x, text_y))
    display.blit(player2_time_text, (player2_time_x, text_y))
    display.blit(return_menu_text, (return_menu_text_x, return_menu_text_y))

    grid_width = WIDTH - 40
    grid_height = HEIGHT - HEADER_HEIGHT - 40
    cell_size_x = grid_width // (GRID_SIZE - 1)
    cell_size_y = grid_height // (GRID_SIZE - 1)
    CELL_SIZE = min(cell_size_x, cell_size_y)

    grid_total_width = CELL_SIZE * (GRID_SIZE - 1)
    grid_total_height = CELL_SIZE * (GRID_SIZE - 1)
    offset_x = (WIDTH - grid_total_width) // 2
    offset_y = HEADER_HEIGHT + (HEIGHT - HEADER_HEIGHT - grid_total_height) // 2

    mouse_x, mouse_y = pygame.mouse.get_pos()
    adjusted_mouse_x = mouse_x - offset_x
    adjusted_mouse_y = mouse_y - offset_y

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.circle(display, BLACK, (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE), DOT_RADIUS)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            line_y = row * CELL_SIZE
            if horizontal_lines[row][col] == 0:
                if abs(adjusted_mouse_y - line_y) < 10 and col * CELL_SIZE < adjusted_mouse_x < (col + 1) * CELL_SIZE:
                    pygame.draw.line(display, DARK_GRAY, (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     (offset_x + (col + 1) * CELL_SIZE, offset_y + row * CELL_SIZE), LINE_WIDTH)

    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            line_x = col * CELL_SIZE
            if vertical_lines[row][col] == 0:
                if abs(adjusted_mouse_x - line_x) < 10 and row * CELL_SIZE < adjusted_mouse_y < (row + 1) * CELL_SIZE:
                    pygame.draw.line(display, DARK_GRAY, (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     (offset_x + col * CELL_SIZE, offset_y + (row + 1) * CELL_SIZE), LINE_WIDTH)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            if horizontal_lines[row][col]:
                pygame.draw.line(display, RED if horizontal_lines[row][col] == 1 else BLUE,
                                 (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                 (offset_x + (col + 1) * CELL_SIZE, offset_y + row * CELL_SIZE), LINE_WIDTH)

    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            if vertical_lines[row][col]:
                pygame.draw.line(display, RED if vertical_lines[row][col] == 1 else BLUE,
                                 (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                 (offset_x + col * CELL_SIZE, offset_y + (row + 1) * CELL_SIZE), LINE_WIDTH)

    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            if boxes[row][col] > 0:
                pygame.draw.rect(display, RED if boxes[row][col] == 1 else BLUE,
                                 (offset_x + col * CELL_SIZE + LINE_WIDTH,
                                  offset_y + row * CELL_SIZE + LINE_WIDTH,
                                  CELL_SIZE - 2 * LINE_WIDTH, CELL_SIZE - 2 * LINE_WIDTH))

    pygame.display.update()
    return return_menu_rect

def check_click(pos):
    global current_player, CELL_SIZE, offset_x, offset_y, player1_time, player2_time, last_turn_time
    x, y = pos
    adjusted_x = x - offset_x
    adjusted_y = y - offset_y

    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000

    if current_player == 1:
        player1_time = max(0, player1_time - current_turn_sec)
    else:
        player2_time = max(0, player2_time - current_turn_sec)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            line_y = row * CELL_SIZE
            if abs(adjusted_y - line_y) < 10 and col * CELL_SIZE < adjusted_x < (col + 1) * CELL_SIZE:
                if horizontal_lines[row][col] == 0:
                    horizontal_lines[row][col] = current_player
                    if not check_box_completion():
                        current_player = 3 - current_player
                        last_turn_time = pygame.time.get_ticks()
                    return

    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            line_x = col * CELL_SIZE
            if abs(adjusted_x - line_x) < 10 and row * CELL_SIZE < adjusted_y < (row + 1) * CELL_SIZE:
                if vertical_lines[row][col] == 0:
                    vertical_lines[row][col] = current_player
                    if not check_box_completion():
                        current_player = 3 - current_player
                        last_turn_time = pygame.time.get_ticks()
                    return

def check_box_completion():
    completed = False
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            if (horizontal_lines[row][col] and horizontal_lines[row + 1][col] and
                    vertical_lines[row][col] and vertical_lines[row][col + 1] and boxes[row][col] == 0):
                boxes[row][col] = current_player
                completed = True
    return completed

def calculate_scores():
    red_score = sum(row.count(1) for row in boxes)
    blue_score = sum(row.count(2) for row in boxes)
    return red_score, blue_score


def check_game_over():
    global player1_time, player2_time
    if player1_time <= 0 or player2_time <= 0 or all(all(cell > 0 for cell in row) for row in boxes):
        # Tính điểm
        red_score, blue_score = calculate_scores()

        # Xác định người chiến thắng
        if player1_time <= 0:
            winner_text = f"{player2_name} Wins!"
            winner_color = BLUE
        elif player2_time <= 0:
            winner_text = f"{player1_name} Wins!"
            winner_color = RED
        else:
            if red_score > blue_score:
                winner_text = f"{player1_name} Wins!"
                winner_color = RED
            elif blue_score > red_score:
                winner_text = f"{player2_name} Wins!"
                winner_color = BLUE
            else:
                winner_text = "It's a Tie!"
                winner_color = DARK_GRAY

        # Vẽ nền
        draw_gradient(display, LIGHT_BLUE, WHITE, (0, 0, WIDTH, HEIGHT + MARGIN))

        # Vẽ khung kết quả
        result_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 150, 600, 300)
        pygame.draw.rect(display, WHITE, result_rect, border_radius=15)
        pygame.draw.rect(display, BLACK, result_rect, 3, border_radius=15)

        # Tiêu đề
        game_over_text = title_font.render("Game Over", True, BLACK)
        display.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 120))

        # Kết quả
        winner_surface = button_font.render(winner_text, True, winner_color)
        display.blit(winner_surface, (WIDTH // 2 - winner_surface.get_width() // 2, HEIGHT // 2 - 60))

        # Hiển thị điểm số - CHỈ TÔ MÀU ĐIỂM
        score_font = pygame.font.Font(None, 50)

        # Player 1 score (luôn màu đỏ)
        p1_text = score_font.render(f"{player1_name}: ", True, BLACK)
        p1_score = score_font.render(f"{red_score}", True, RED)

        # Dấu gạch ngang
        separator = score_font.render(" - ", True, BLACK)

        # Player 2 score (luôn màu xanh)
        p2_text = score_font.render(f"{player2_name}: ", True, BLACK)
        p2_score = score_font.render(f"{blue_score}", True, BLUE)

        # Tính toán vị trí để căn giữa
        total_width = (p1_text.get_width() + p1_score.get_width() +
                       separator.get_width() +
                       p2_text.get_width() + p2_score.get_width())
        start_x = WIDTH // 2 - total_width // 2

        # Vẽ điểm số với màu nổi bật
        display.blit(p1_text, (start_x, HEIGHT // 2))
        display.blit(p1_score, (start_x + p1_text.get_width(), HEIGHT // 2))
        sep_x = start_x + p1_text.get_width() + p1_score.get_width()
        display.blit(separator, (sep_x, HEIGHT // 2))
        p2_x = sep_x + separator.get_width()
        display.blit(p2_text, (p2_x, HEIGHT // 2))
        display.blit(p2_score, (p2_x + p2_text.get_width(), HEIGHT // 2))

        # Nút chơi lại
        replay_btn = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 70, 180, 50)
        pygame.draw.rect(display, PASTEL_GREEN, replay_btn, border_radius=10)
        pygame.draw.rect(display, BLACK, replay_btn, 2, border_radius=10)
        replay_text = button_font.render("Play Again", True, BLACK)
        display.blit(replay_text, (replay_btn.x + 90 - replay_text.get_width() // 2,
                                   replay_btn.y + 25 - replay_text.get_height() // 2))

        # Nút về menu
        menu_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 70, 180, 50)
        pygame.draw.rect(display, LIGHT_BLUE, menu_btn, border_radius=10)
        pygame.draw.rect(display, BLACK, menu_btn, 2, border_radius=10)
        menu_text = button_font.render("Main Menu", True, BLACK)
        display.blit(menu_text, (menu_btn.x + 90 - menu_text.get_width() // 2,
                                 menu_btn.y + 25 - menu_text.get_height() // 2))

        pygame.display.update()

        # Xử lý sự kiện
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if replay_btn.collidepoint(event.pos):
                        reset_game()
                        waiting = False
                        return
                    elif menu_btn.collidepoint(event.pos):
                        menu()
                        waiting = False
                        return

def reset_game():
    global horizontal_lines, vertical_lines, boxes, current_player, start_time, player1_time, player2_time, last_turn_time
    horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
    vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
    boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]
    start_time = 0
    player1_time = 30
    player2_time = 30
    last_turn_time = pygame.time.get_ticks()
    current_player = first_player
    menu()

menu()
last_turn_time = pygame.time.get_ticks()
while True:
    return_menu_rect = draw_grid()
    check_game_over()

    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000

    if current_player == 1:
        player1_time = max(0, 30 - current_turn_sec)
        if player1_time <= 0:
            current_player = 2
            last_turn_time = pygame.time.get_ticks()
    else:
        player2_time = max(0, 30 - current_turn_sec)
        if player2_time <= 0:
            current_player = 1
            last_turn_time = pygame.time.get_ticks()

    if not is_pvp and current_player == 2:
        ai_move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if return_menu_rect.collidepoint(event.pos):
                reset_game()
            else:
                check_click(event.pos)
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h - MARGIN
            display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)