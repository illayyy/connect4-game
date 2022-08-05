import socket
import pygame
import sys
import math

PORT = 54321

# color constants
BLACK = (104, 92, 93)
WHITE = (243, 248, 241)
RED = (202, 81, 100)
BLUE = (37, 150, 190)
GREEN = (155, 208, 191)

# window constants
WINDOW_HEIGHT = 700
WINDOW_WIDTH = 700
ROW = 6
COL = 7

# game variables
board = [[0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0]]
status = [0, 0, 0, 0, 0, 0, 0]
CAN_PLAY = False


# checks which column has been clicked
def click_column(pos):
    x, y = pos
    column = math.floor(x / 100)
    return column


# checks if the selected column is valid to drop a piece into
def valid_column(column):
    if status[column] >= 6:
        return False
    return True


# drops a piece of a chosen color into a selected column, returns false if it wasn't able to (invalid column)
def make_a_move(column, color):
    if valid_column(column):
        board[5 - status[column]][column] = color
        status[column] += 1
        return True
    return False


# draws the game grid
def draw_grid():
    block_size = WINDOW_WIDTH / 7
    x, y = 0, 0
    for i in range(0, 6):
        y = block_size * i + 100
        for j in range(0, 7):
            x = block_size * j
            rect = pygame.Rect(x, y, block_size, block_size)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if board[i][j] == 1:
                pygame.draw.circle(screen, RED, (x + 0.5 * block_size, y + 0.5 * block_size), block_size * 0.48)
            elif board[i][j] == 2:
                pygame.draw.circle(screen, BLUE, (x + 0.5 * block_size, y + 0.5 * block_size), block_size * 0.48)


# checks if the current player has won
def did_win():
    count = 0
    # check row
    for i in range(ROW):
        count = 0
        for j in range(COL):
            if board[i][j] == my_color:
                count += 1
            else:
                count = 0
        if count >= 4:
            return True

    # check column
    for i in range(COL):
        count = 0
        for j in range(ROW):
            if board[j][i] == my_color:
                count += 1
            else:
                count = 0
        if count >= 4:
            return True

    # check positively sloped diagonals
    for c in range(COL - 3):
        for r in range(ROW - 3):
            if board[r][c] == my_color and board[r + 1][c + 1] == my_color and board[r + 2][c + 2] == my_color and \
                    board[r + 3][c + 3] == my_color:
                return True

    # check negatively sloped diagonals
    for c in range(COL - 3):
        for r in range(3, ROW):
            if board[r][c] == my_color and board[r - 1][c + 1] == my_color and board[r - 2][c + 2] == my_color \
                    and board[r - 3][c + 3] == my_color:
                return True
    return False


# returns the opposite color of the inputted one
def opposite_color(color):
    if color == 1:
        return 2
    return 1


# displays a text message onto the screen
def display_mes(str, color):
    myfont = pygame.font.SysFont('Calibri', 70)
    textsurface = myfont.render(str, True, color)
    text_rectangle = textsurface.get_rect()
    text_rectangle.center = (WINDOW_WIDTH / 2, 50)
    screen.blit(textsurface, text_rectangle)
    pygame.display.update()


def main():
    # socket stuff
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setblocking(False)
    my_socket.settimeout(60000)
    my_socket.connect(("127.0.0.1", PORT))
    my_socket.send("CONNECT".encode())
    print(my_socket.recv(1024).decode())

    # waits for a game to begin and assigns the player's color (assigned randomly by server)
    global my_color
    while True:
        msg = my_socket.recv(1024).decode()
        if msg == "red":
            my_color = 1
            break
        elif msg == "blue":
            my_color = 2
            break
    msg = my_socket.recv(1024).decode()

    # initiates pygame
    global clock, screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    icon = pygame.image.load("RED.png")
    pygame.display.set_icon(icon)
    pygame.display.set_caption("CLIENT 2")
    pygame.init()

    # game boolean values
    can_play = False
    inv = False
    running = True
    lost = False
    while running:
        clock.tick(60)  # fps
        screen.fill(WHITE)
        draw_grid()

        # checks for and displays the appropriate game message
        if can_play:
            if inv:
                display_mes("INVALID MOVE", BLACK)
            else:
                display_mes("YOUR TURN", BLACK)
        elif did_win():
            display_mes("YOU WON", GREEN)
        elif lost:
            display_mes("YOU LOST", RED)
        else:
            display_mes("OPPONENTS TURN", BLACK)

        # checks if it is currently the player's turn and allows him to make a move
        if msg == "play" or msg.isnumeric() and not can_play and not lost:
            can_play = True
            # if the player received a column number from the server (true for every turn except for the first one),
            # place an opponent piece into that column
            if msg.isnumeric():
                # if the received column number is larger than 10, the player has lost
                # victory message is sent by the opponent, and is : 10 + column number
                if int(msg) >= 10:
                    make_a_move(int(msg) - 10, opposite_color(my_color))
                    can_play = False
                    lost = True
                else:
                    make_a_move(int(msg), opposite_color(my_color))

        # if it is not the player's turn, check for messages from server
        else:
            my_socket.settimeout(0.001)
            try:
                msg = my_socket.recv(1024).decode()
            except socket.error:
                pass
            my_socket.settimeout(60000)

        # game events
        for event in pygame.event.get():
            # checks if user quit the window
            if event.type == pygame.QUIT:
                running = False
            # checks if the player clicked anywhere on the screen
            # if it is the players turn, he will be allowed to try to make a move
            if event.type == pygame.MOUSEBUTTONDOWN:
                if can_play:
                    pos = click_column(pygame.mouse.get_pos())  # finds the x, y coordinates the player clicked on
                    # if the attempted move is valid, it will be made and the turn will pass
                    if make_a_move(pos, my_color):
                        if did_win():
                            my_socket.send(str(pos + 10).encode())
                        else:
                            my_socket.send(str(pos).encode())
                        msg = my_socket.recv(1024).decode()
                        can_play = False
                        inv = False
                    # if the attempted move is invalid, it will not be made, the turn will not pass...
                    # ...and an invalid move message will appear on screen
                    else:
                        inv = True
        pygame.display.update()
    if not running:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
