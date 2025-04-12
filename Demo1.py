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
    pygame.draw.rect(display, GRAY, pvp_rect)
    pygame.draw.rect(display, GRAY, pve_rect)
    pvp_text = font.render("Player vs Player", True, BLACK)
    pve_text = font.render("Player vs AI", True, BLACK)
    display.blit(title, (WIDTH // 4, HEIGHT // 4))
    display.blit(pvp_text, (WIDTH // 3, HEIGHT // 2 - 30))
    display.blit(pve_text, (WIDTH // 3, HEIGHT // 2 + 30))
    pygame.display.update()
    return pvp_rect, pve_rect


def menu():
    global is_pvp
    while True:
        pvp_rect, pve_rect = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_rect.collidepoint(event.pos):
                    is_pvp = True
                    return
                elif pve_rect.collidepoint(event.pos):
                    is_pvp = False
                    return


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


menu()
while True:
    draw_grid()
    check_game_over()
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
            CELL_SIZE = WIDTH // (GRID_SIZE - 1)
            display = pygame.display.set_mode((WIDTH, HEIGHT + MARGIN), pygame.RESIZABLE)
