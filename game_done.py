import pygame
import sys
import random

WIDTH, HEIGHT = 1500, 750  # Tăng kích thước cửa sổ nếu cần
GRID_SIZE = 4  # Giá trị mặc định
GRID_SIZE_MIN = 3  # Tối thiểu 3x3 chấm (2x2 ô vuông)
GRID_SIZE_MAX = 8  # Tối đa 8x8 chấm (7x7 ô vuông)
CELL_SIZE = WIDTH // (GRID_SIZE - 1)
LINE_WIDTH = 5
DOT_RADIUS = 5
MARGIN = 50
start_time = 0
player1_name = "Player 1"  # Tên mặc định cho người chơi 1
player2_name = "Player 2"  # Tên mặc định cho người chơi 2 hoặc AI
first_player = 1
CELL_SIZE = 0  # Sẽ được cập nhật trong draw_grid()
offset_x = 0
offset_y = 0
player1_time = 60  # Thời gian của người chơi 1 (60 giây)
player2_time = 60  # Thời gian của người chơi 2 (60 giây)
last_turn_time = 0  # Thời gian bắt đầu lượt hiện tại
pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)
pygame.display.set_caption("Dots and Boxes")
WHITE, BLACK, RED, BLUE, GRAY = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255), (200, 200, 200)

horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]
current_player = 1  # 1: Người chơi 1, 2: Người chơi 2 hoặc máy
is_pvp = False  # True nếu chơi PvP, False nếu chơi PvE

pygame.font.init()
font = pygame.font.Font(None, 36)


def draw_menu():
    display.fill(WHITE)
    title = font.render("Dots and Boxes", True, BLACK)
    pvp_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 - 40, WIDTH // 2, 50)
    pve_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 20, WIDTH // 2, 50)
    options_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 80, WIDTH // 2, 50)  # Nút Options mới
    pygame.draw.rect(display, GRAY, pvp_rect)
    pygame.draw.rect(display, GRAY, pve_rect)
    pygame.draw.rect(display, GRAY, options_rect)
    pvp_text = font.render("Player vs Player", True, BLACK)
    pve_text = font.render("Player vs AI", True, BLACK)
    options_text = font.render("Options", True, BLACK)
    display.blit(title, (WIDTH // 4, HEIGHT // 4))
    display.blit(pvp_text, (WIDTH // 3, HEIGHT // 2 - 30))
    display.blit(pve_text, (WIDTH // 3, HEIGHT // 2 + 30))
    display.blit(options_text, (WIDTH // 3, HEIGHT // 2 + 90))
    pygame.display.update()
    return pvp_rect, pve_rect, options_rect  # Trả về thêm options_rect

def options_menu():
    global player1_name, player2_name, first_player, is_pvp, GRID_SIZE, horizontal_lines, vertical_lines, boxes
    input_active = None
    player1_input = player1_name
    player2_input = player2_name

    while True:
        display.fill(WHITE)
        title = font.render("Options", True, BLACK)

        # Nhãn và ô nhập tên người chơi 1
        player1_label = font.render("Player 1 Name:", True, BLACK)
        player1_rect = pygame.Rect(WIDTH // 4 + 150, HEIGHT // 2 - 100, WIDTH // 2 - 150, 40)
        player1_input_surface = font.render(player1_input, True, BLACK)
        pygame.draw.rect(display, GRAY if input_active != 'player1' else BLACK, player1_rect, 2)

        # Nhãn và ô nhập tên người chơi 2 hoặc AI
        player2_label = font.render("Player 2/AI Name:", True, BLACK)
        player2_rect = pygame.Rect(WIDTH // 4 + 150, HEIGHT // 2 - 40, WIDTH // 2 - 150, 40)
        player2_input_surface = font.render(player2_input, True, BLACK)
        pygame.draw.rect(display, GRAY if input_active != 'player2' else BLACK, player2_rect, 2)

        # Nhãn và nút chọn người đi trước
        first_player_label = font.render("First Move:", True, BLACK)
        human_rect = pygame.Rect(WIDTH // 4 + 150, HEIGHT // 2 + 20, 100, 40)
        ai_rect = pygame.Rect(WIDTH // 4 + 260, HEIGHT // 2 + 20, 140, 40)
        pygame.draw.rect(display, BLUE if first_player == 1 else GRAY, human_rect)
        pygame.draw.rect(display, BLUE if first_player == 2 else GRAY, ai_rect)
        human_text = font.render("Human", True, BLACK)
        ai_text = font.render("AI/Player 2", True, BLACK)

        # Nhãn và nút chỉnh kích thước lưới (Grid Size)
        grid_size_label = font.render("Grid Size:", True, BLACK)
        decrease_grid_rect = pygame.Rect(WIDTH // 4 + 150, HEIGHT // 2 + 80, 40, 40)  # Nút "-"
        grid_display_rect = pygame.Rect(WIDTH // 4 + 200, HEIGHT // 2 + 80, 40, 40)   # Hiển thị số
        increase_grid_rect = pygame.Rect(WIDTH // 4 + 250, HEIGHT // 2 + 80, 40, 40)  # Nút "+"

        pygame.draw.rect(display, GRAY, decrease_grid_rect)
        pygame.draw.rect(display, WHITE, grid_display_rect)
        pygame.draw.rect(display, GRAY, increase_grid_rect)

        decrease_text = font.render("-", True, BLACK)
        grid_size_text = font.render(str(GRID_SIZE), True, BLACK)
        increase_text = font.render("+", True, BLACK)

        # Nút Back
        back_rect = pygame.Rect(WIDTH // 4 + 150, HEIGHT // 2 + 140, WIDTH // 4, 40)
        pygame.draw.rect(display, GRAY, back_rect)
        back_text = font.render("Back", True, BLACK)

        # Vẽ các thành phần lên màn hình
        display.blit(title, (WIDTH // 4, HEIGHT // 4))
        display.blit(player1_label, (WIDTH // 4 - 100, HEIGHT // 2 - 90))
        display.blit(player1_input_surface, (WIDTH // 4 + 160, HEIGHT // 2 - 90))
        display.blit(player2_label, (WIDTH // 4 - 100, HEIGHT // 2 - 30))
        display.blit(player2_input_surface, (WIDTH // 4 + 160, HEIGHT // 2 - 30))
        display.blit(first_player_label, (WIDTH // 4 - 100, HEIGHT // 2 + 30))
        display.blit(human_text, (WIDTH // 4 + 160, HEIGHT // 2 + 25))
        display.blit(ai_text, (WIDTH // 4 + 270, HEIGHT // 2 + 25))
        display.blit(grid_size_label, (WIDTH // 4 - 100, HEIGHT // 2 + 90))
        display.blit(decrease_text, (decrease_grid_rect.x + 12, decrease_grid_rect.y + 5))
        display.blit(grid_size_text, (grid_display_rect.x + 12, grid_display_rect.y + 5))
        display.blit(increase_text, (increase_grid_rect.x + 12, increase_grid_rect.y + 5))
        display.blit(back_text, (WIDTH // 4 + 180, HEIGHT // 2 + 145))

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
                elif human_rect.collidepoint(event.pos):
                    first_player = 1
                elif ai_rect.collidepoint(event.pos):
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
        pvp_rect, pve_rect, options_rect = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_rect.collidepoint(event.pos):
                    is_pvp = True
                    current_player = first_player  # Áp dụng người đi trước
                    return
                elif pve_rect.collidepoint(event.pos):
                    is_pvp = False
                    current_player = first_player  # Áp dụng người đi trước
                    return
                elif options_rect.collidepoint(event.pos):
                    options_menu()


def draw_grid():
    global start_time, CELL_SIZE, offset_x, offset_y, player1_time, player2_time, last_turn_time
    display.fill(WHITE)

    # Dành không gian phía trên để hiển thị thông tin (thanh header)
    HEADER_HEIGHT = 60

    # Tính thời gian đã chơi (thời gian tổng của trò chơi)
    if start_time == 0:
        start_time = pygame.time.get_ticks()
    elapsed_ms = pygame.time.get_ticks() - start_time
    elapsed_sec = elapsed_ms // 1000
    minutes = elapsed_sec // 60
    seconds = elapsed_sec % 60
    time_text = font.render(f"Total: {minutes:02d}:{seconds:02d}", True, BLACK)

    # Tính thời gian đã trôi qua trong lượt hiện tại
    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000

    # Chỉ giảm thời gian của người chơi hiện tại
    if current_player == 1:
        player1_time = max(0, 60 - current_turn_sec)
    else:
        player2_time = max(0, 60 - current_turn_sec)

    # Hiển thị thời gian của từng người chơi
    player1_time_text = font.render(f"{player1_name} Time: {int(player1_time)}s", True, RED if current_player == 1 else BLACK)
    player2_time_text = font.render(f"{player2_name} Time: {int(player2_time)}s", True, BLUE if current_player == 2 else BLACK)

    # Tính điểm số và hiển thị tên người chơi
    red_score, blue_score = calculate_scores()
    player1_text = font.render(f"{player1_name}: {red_score}", True, RED)
    player2_text = font.render(f"{player2_name}: {blue_score}", True, BLUE)
    separator_text = font.render(" | ", True, BLACK)

    # Vẽ thanh header (nền màu xám nhạt)
    pygame.draw.rect(display, GRAY, (0, 0, WIDTH, HEADER_HEIGHT))

    # Căn chỉnh văn bản trong thanh header
    player1_width = player1_text.get_width()
    player2_width = player2_text.get_width()
    separator_width = separator_text.get_width()
    time_width = time_text.get_width()
    player1_time_width = player1_time_text.get_width()
    player2_time_width = player2_time_text.get_width()

    total_score_width = player1_width + separator_width + player2_width
    score_x = (WIDTH - total_score_width) // 2
    text_y = (HEADER_HEIGHT - player1_text.get_height()) // 2

    player1_time_x = 20
    player2_time_x = WIDTH - player2_time_width - time_width - 40
    time_x = WIDTH - time_width - 20

    display.blit(player1_text, (score_x, text_y))
    display.blit(separator_text, (score_x + player1_width, text_y))
    display.blit(player2_text, (score_x + player1_width + separator_width, text_y))
    display.blit(time_text, (time_x, text_y))
    display.blit(player1_time_text, (player1_time_x, text_y))
    display.blit(player2_time_text, (player2_time_x, text_y))

    # Tính toán kích thước grid để fit với phần còn lại của cửa sổ
    grid_width = WIDTH - 40  # Khoảng cách lề 20 pixel mỗi bên
    grid_height = HEIGHT - HEADER_HEIGHT - 40  # Khoảng cách lề 20 pixel dưới cùng
    cell_size_x = grid_width // (GRID_SIZE - 1)
    cell_size_y = grid_height // (GRID_SIZE - 1)
    CELL_SIZE = min(cell_size_x, cell_size_y)

    # Tính toán vị trí bắt đầu của grid để căn giữa
    grid_total_width = CELL_SIZE * (GRID_SIZE - 1)
    grid_total_height = CELL_SIZE * (GRID_SIZE - 1)
    offset_x = (WIDTH - grid_total_width) // 2  # Căn giữa theo chiều ngang
    offset_y = HEADER_HEIGHT + (HEIGHT - HEADER_HEIGHT - grid_total_height) // 2  # Căn giữa theo chiều dọc, tính từ dưới thanh header

    # Lấy vị trí chuột để làm nổi bật đường
    mouse_x, mouse_y = pygame.mouse.get_pos()
    adjusted_mouse_x = mouse_x - offset_x
    adjusted_mouse_y = mouse_y - offset_y

    # Vẽ các chấm (dots)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.circle(display, BLACK,
                               (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                               DOT_RADIUS)

    # Highlight các đường ngang chưa được vẽ khi chuột di qua
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            line_y = row * CELL_SIZE
            if horizontal_lines[row][col] == 0:  # Chỉ highlight nếu đường chưa được vẽ
                if abs(adjusted_mouse_y - line_y) < 10 and col * CELL_SIZE < adjusted_mouse_x < (col + 1) * CELL_SIZE:
                    pygame.draw.line(display, (150, 150, 150),  # Màu xám nhạt
                                     (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     (offset_x + (col + 1) * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     LINE_WIDTH)

    # Highlight các đường dọc chưa được vẽ khi chuột di qua
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            line_x = col * CELL_SIZE
            if vertical_lines[row][col] == 0:  # Chỉ highlight nếu đường chưa được vẽ
                if abs(adjusted_mouse_x - line_x) < 10 and row * CELL_SIZE < adjusted_mouse_y < (row + 1) * CELL_SIZE:
                    pygame.draw.line(display, (150, 150, 150),  # Màu xám nhạt
                                     (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     (offset_x + col * CELL_SIZE, offset_y + (row + 1) * CELL_SIZE),
                                     LINE_WIDTH)

    # Vẽ các đường ngang (horizontal lines) đã được vẽ
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            if horizontal_lines[row][col]:
                pygame.draw.line(display, RED if horizontal_lines[row][col] == 1 else BLUE,
                                 (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                 (offset_x + (col + 1) * CELL_SIZE, offset_y + row * CELL_SIZE),
                                 LINE_WIDTH)

    # Vẽ các đường dọc (vertical lines) đã được vẽ
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            if vertical_lines[row][col]:
                pygame.draw.line(display, RED if vertical_lines[row][col] == 1 else BLUE,
                                 (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                 (offset_x + col * CELL_SIZE, offset_y + (row + 1) * CELL_SIZE),
                                 LINE_WIDTH)

    # Vẽ các ô (boxes)
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            if boxes[row][col] > 0:
                pygame.draw.rect(display, RED if boxes[row][col] == 1 else BLUE,
                                 (offset_x + col * CELL_SIZE + LINE_WIDTH,
                                  offset_y + row * CELL_SIZE + LINE_WIDTH,
                                  CELL_SIZE - 2 * LINE_WIDTH, CELL_SIZE - 2 * LINE_WIDTH))

    pygame.display.update()
def check_click(pos):
    global current_player, CELL_SIZE, offset_x, offset_y, player1_time, player2_time, last_turn_time
    x, y = pos
    # Điều chỉnh tọa độ click bằng cách trừ offset
    adjusted_x = x - offset_x
    adjusted_y = y - offset_y

    # Tính thời gian đã sử dụng trong lượt hiện tại
    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000

    # Cập nhật thời gian của người chơi hiện tại
    if current_player == 1:
        player1_time = max(0, player1_time - current_turn_sec)
    else:
        player2_time = max(0, player2_time - current_turn_sec)

    # Kiểm tra click trên các đường ngang
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            line_y = row * CELL_SIZE
            if abs(adjusted_y - line_y) < 10 and col * CELL_SIZE < adjusted_x < (col + 1) * CELL_SIZE:
                if horizontal_lines[row][col] == 0:
                    horizontal_lines[row][col] = current_player
                    if not check_box_completion():
                        current_player = 3 - current_player
                        last_turn_time = pygame.time.get_ticks()  # Cập nhật thời gian bắt đầu lượt mới
                    return

    # Kiểm tra click trên các đường dọc
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            line_x = col * CELL_SIZE
            if abs(adjusted_x - line_x) < 10 and row * CELL_SIZE < adjusted_y < (row + 1) * CELL_SIZE:
                if vertical_lines[row][col] == 0:
                    vertical_lines[row][col] = current_player
                    if not check_box_completion():
                        current_player = 3 - current_player
                        last_turn_time = pygame.time.get_ticks()  # Cập nhật thời gian bắt đầu lượt mới
                    return

def ai_move():
    global current_player, player1_time, player2_time, last_turn_time
    best_move = None
    available_moves = []
    almost_completed_boxes = []

    # Tính thời gian đã sử dụng trong lượt hiện tại
    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000

    # Cập nhật thời gian của AI (người chơi 2)
    if current_player == 2:
        player2_time = max(0, player2_time - current_turn_sec)

    # Quét các ô gần hoàn thành (chỉ còn thiếu 1 đường)
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            sides_filled = sum([horizontal_lines[row][col], horizontal_lines[row + 1][col],
                                vertical_lines[row][col], vertical_lines[row][col + 1]])
            if sides_filled == 3:
                if horizontal_lines[row][col] == 0:
                    almost_completed_boxes.append(("h", row, col))
                elif horizontal_lines[row + 1][col] == 0:
                    almost_completed_boxes.append(("h", row + 1, col))
                elif vertical_lines[row][col] == 0:
                    almost_completed_boxes.append(("v", row, col))
                elif vertical_lines[row][col + 1] == 0:
                    almost_completed_boxes.append(("v", row, col + 1))

    if almost_completed_boxes:
        move = random.choice(almost_completed_boxes)
    else:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 1):
                if horizontal_lines[row][col] == 0:
                    if not will_give_advantage("h", row, col):
                        available_moves.append(("h", row, col))

        for row in range(GRID_SIZE - 1):
            for col in range(GRID_SIZE):
                if vertical_lines[row][col] == 0:
                    if not will_give_advantage("v", row, col):
                        available_moves.append(("v", row, col))

        if available_moves:
            move = random.choice(available_moves)
        else:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE - 1):
                    if horizontal_lines[row][col] == 0:
                        best_move = ("h", row, col)
                        break
                if best_move:
                    break

            for row in range(GRID_SIZE - 1):
                for col in range(GRID_SIZE):
                    if vertical_lines[row][col] == 0:
                        best_move = ("v", row, col)
                        break
                if best_move:
                    break

            move = best_move

    if move:
        if move[0] == "h":
            horizontal_lines[move[1]][move[2]] = current_player
        else:
            vertical_lines[move[1]][move[2]] = current_player

        if not check_box_completion():
            current_player = 3 - current_player
            last_turn_time = pygame.time.get_ticks()  # Cập nhật thời gian bắt đầu lượt mới
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
    # Kiểm tra nếu một trong hai người chơi hết thời gian
    if player1_time <= 0:
        red_score, blue_score = calculate_scores()
        display.fill(WHITE)
        text1 = font.render("Game Over!", True, BLACK)
        text2 = font.render(f"{player1_name} ran out of time!", True, BLACK)
        text3 = font.render(f"Final Score: {player1_name}: {red_score} - {player2_name}: {blue_score}", True, BLACK)
        new_game_btn = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 60, WIDTH // 2, 40)
        quit_btn = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 110, WIDTH // 2, 40)

        pygame.draw.rect(display, GRAY, new_game_btn)
        pygame.draw.rect(display, GRAY, quit_btn)

        new_game_text = font.render("New Game", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)

        display.blit(text1, (WIDTH // 4, HEIGHT // 2 - 40))
        display.blit(text2, (WIDTH // 4, HEIGHT // 2))
        display.blit(text3, (WIDTH // 4, HEIGHT // 2 + 20))
        display.blit(new_game_text, (WIDTH // 3, HEIGHT // 2 + 65))
        display.blit(quit_text, (WIDTH // 3 + 10, HEIGHT // 2 + 115))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_btn.collidepoint(event.pos):
                        reset_game()
                        return
                    elif quit_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
        return

    if player2_time <= 0:
        red_score, blue_score = calculate_scores()
        display.fill(WHITE)
        text1 = font.render("Game Over!", True, BLACK)
        text2 = font.render(f"{player2_name} ran out of time!", True, BLACK)
        text3 = font.render(f"Final Score: {player1_name}: {red_score} - {player2_name}: {blue_score}", True, BLACK)
        new_game_btn = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 60, WIDTH // 2, 40)
        quit_btn = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 110, WIDTH // 2, 40)

        pygame.draw.rect(display, GRAY, new_game_btn)
        pygame.draw.rect(display, GRAY, quit_btn)

        new_game_text = font.render("New Game", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)

        display.blit(text1, (WIDTH // 4, HEIGHT // 2 - 40))
        display.blit(text2, (WIDTH // 4, HEIGHT // 2))
        display.blit(text3, (WIDTH // 4, HEIGHT // 2 + 20))
        display.blit(new_game_text, (WIDTH // 3, HEIGHT // 2 + 65))
        display.blit(quit_text, (WIDTH // 3 + 10, HEIGHT // 2 + 115))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_btn.collidepoint(event.pos):
                        reset_game()
                        return
                    elif quit_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
        return

    # Kiểm tra nếu tất cả ô đã được hoàn thành
    if all(all(cell > 0 for cell in row) for row in boxes):
        red_score, blue_score = calculate_scores()
        display.fill(WHITE)

        text1 = font.render("Game Over!", True, BLACK)
        text2 = font.render(f"{player1_name}: {red_score} - {player2_name}: {blue_score}", True, BLACK)
        new_game_btn = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 60, WIDTH // 2, 40)
        quit_btn = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 110, WIDTH // 2, 40)

        pygame.draw.rect(display, GRAY, new_game_btn)
        pygame.draw.rect(display, GRAY, quit_btn)

        new_game_text = font.render("New Game", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)

        display.blit(text1, (WIDTH // 4, HEIGHT // 2 - 40))
        display.blit(text2, (WIDTH // 4, HEIGHT // 2))
        display.blit(new_game_text, (WIDTH // 3, HEIGHT // 2 + 65))
        display.blit(quit_text, (WIDTH // 3 + 10, HEIGHT // 2 + 115))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_btn.collidepoint(event.pos):
                        reset_game()
                        return
                    elif quit_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

def reset_game():
    global horizontal_lines, vertical_lines, boxes, current_player, start_time, player1_time, player2_time, last_turn_time
    horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
    vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
    boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]
    start_time = 0
    player1_time = 60  # Đặt lại thời gian
    player2_time = 60
    last_turn_time = pygame.time.get_ticks()  # Khởi tạo thời gian lượt
    current_player = first_player
    menu()

def will_give_advantage(line_type, row, col):
    """Kiểm tra xem nước đi này có mở đường cho đối thủ ghi điểm không"""
    temp_lines = horizontal_lines if line_type == "h" else vertical_lines
    temp_lines[row][col] = current_player  # Giả lập nước đi

    # Kiểm tra xem có ô nào sắp hoàn thành không
    for r in range(GRID_SIZE - 1):
        for c in range(GRID_SIZE - 1):
            sides_filled = sum([horizontal_lines[r][c], horizontal_lines[r + 1][c],
                                vertical_lines[r][c], vertical_lines[r][c + 1]])
            if sides_filled == 3 and boxes[r][c] == 0:
                temp_lines[row][col] = 0  # Hoàn tác
                return True  # Tránh nước đi này

    temp_lines[row][col] = 0  # Hoàn tác
    return False


menu()
start_time = pygame.time.get_ticks()
last_turn_time = pygame.time.get_ticks()
while True:
    draw_grid()
    check_game_over()

    # Kiểm tra thời gian của người chơi hiện tại
    current_turn_ms = pygame.time.get_ticks() - last_turn_time
    current_turn_sec = current_turn_ms // 1000

    if current_player == 1:
        player1_time = max(0, 60 - current_turn_sec)
        if player1_time <= 0:
            current_player = 2
            last_turn_time = pygame.time.get_ticks()
    else:
        player2_time = max(0, 60 - current_turn_sec)
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
            check_click(event.pos)
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h - MARGIN
            display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)