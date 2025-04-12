import pygame
import sys
import random

WIDTH, HEIGHT = 500, 500
GRID_SIZE = 4
CELL_SIZE = WIDTH // (GRID_SIZE - 1)
LINE_WIDTH = 5
DOT_RADIUS = 5
MARGIN = 50

pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)
pygame.display.set_caption("Dots and Boxes")
WHITE, BLACK, RED, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255)

horizontal_lines = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE)]
vertical_lines = [[0] * GRID_SIZE for _ in range(GRID_SIZE - 1)]
boxes = [[0] * (GRID_SIZE - 1) for _ in range(GRID_SIZE - 1)]
current_player = 1  # 1: Người chơi, 2: Máy
pygame.font.init()
font = pygame.font.Font(None, 36)

def draw_grid():
    display.fill(WHITE)
    score_text = font.render(f"Red: {calculate_scores()[0]} | Blue: {calculate_scores()[1]}", True, BLACK)
    display.blit(score_text, (WIDTH // 4, HEIGHT))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.circle(display, BLACK, (col * CELL_SIZE, row * CELL_SIZE), DOT_RADIUS)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            if horizontal_lines[row][col]:
                pygame.draw.line(display, RED if horizontal_lines[row][col] == 1 else BLUE,
                                 (col * CELL_SIZE, row * CELL_SIZE),
                                 ((col + 1) * CELL_SIZE, row * CELL_SIZE), LINE_WIDTH)
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            if vertical_lines[row][col]:
                pygame.draw.line(display, RED if vertical_lines[row][col] == 1 else BLUE,
                                 (col * CELL_SIZE, row * CELL_SIZE),
                                 (col * CELL_SIZE, (row + 1) * CELL_SIZE), LINE_WIDTH)
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            if boxes[row][col] > 0:
                pygame.draw.rect(display, RED if boxes[row][col] == 1 else BLUE,
                                 (col * CELL_SIZE + LINE_WIDTH, row * CELL_SIZE + LINE_WIDTH,
                                  CELL_SIZE - 2 * LINE_WIDTH, CELL_SIZE - 2 * LINE_WIDTH))
    pygame.display.update()

def check_click(pos):
    global current_player
    x, y = pos
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            if abs(y - row * CELL_SIZE) < 10 and col * CELL_SIZE < x < (col + 1) * CELL_SIZE:
                if horizontal_lines[row][col] == 0:
                    horizontal_lines[row][col] = current_player
                    if not check_box_completion():
                        current_player = 3 - current_player
                    return
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            if abs(x - col * CELL_SIZE) < 10 and row * CELL_SIZE < y < (row + 1) * CELL_SIZE:
                if vertical_lines[row][col] == 0:
                    vertical_lines[row][col] = current_player
                    if not check_box_completion():
                        current_player = 3 - current_player
                    return


def ai_move():
    global current_player
    best_move = None
    available_moves = []
    almost_completed_boxes = []

    # Quét các ô gần hoàn thành (chỉ còn thiếu 1 đường)
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            sides_filled = sum([horizontal_lines[row][col], horizontal_lines[row + 1][col],
                                vertical_lines[row][col], vertical_lines[row][col + 1]])
            if sides_filled == 3:
                # Nếu tìm thấy ô sắp hoàn thành, ưu tiên đi nước này
                if horizontal_lines[row][col] == 0:
                    almost_completed_boxes.append(("h", row, col))
                elif horizontal_lines[row + 1][col] == 0:
                    almost_completed_boxes.append(("h", row + 1, col))
                elif vertical_lines[row][col] == 0:
                    almost_completed_boxes.append(("v", row, col))
                elif vertical_lines[row][col + 1] == 0:
                    almost_completed_boxes.append(("v", row, col + 1))

    # Nếu có nước đi giúp AI ghi điểm, thực hiện ngay
    if almost_completed_boxes:
        move = random.choice(almost_completed_boxes)
    else:
        # Nếu không có ô sắp hoàn thành, tránh tạo điều kiện cho đối thủ
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

        # Nếu có nước đi an toàn, chọn ngẫu nhiên trong danh sách đó
        if available_moves:
            move = random.choice(available_moves)
        else:
            # Nếu không có nước đi an toàn, đành chọn đại
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

    # Thực hiện nước đi đã chọn
    if move:
        if move[0] == "h":
            horizontal_lines[move[1]][move[2]] = current_player
        else:
            vertical_lines[move[1]][move[2]] = current_player

        if not check_box_completion():
            current_player = 3 - current_player


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
    if all(all(cell > 0 for cell in row) for row in boxes):
        red_score, blue_score = calculate_scores()
        display.fill(WHITE)

        text1 = font.render("Game Over!", True, BLACK)
        text2 = font.render(f"Red: {red_score} - Blue: {blue_score}", True, BLACK)

        display.blit(text1, (WIDTH // 4, HEIGHT // 2 - 20))
        display.blit(text2, (WIDTH // 4, HEIGHT // 2 + 20))

        pygame.display.update()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

while True:
    draw_grid()
    check_game_over()
    if current_player == 2:
        ai_move()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and current_player == 1:
            check_click(event.pos)
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h - MARGIN
            CELL_SIZE = WIDTH // (GRID_SIZE - 1)
            display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)
