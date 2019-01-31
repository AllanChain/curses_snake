import curses
from time import sleep

# initialize the screen
s = curses.initscr()
curses.curs_set(0)
curses.start_color()

# initialize the window
hei, wei = s.getmaxyx()
w = curses.newwin(hei, wei, 0, 0)
w.keypad(1)
w.timeout(100)
# initialize color_pairs
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_WHITE)

# initialize the position of snake
y = int(hei/2)
x = int(wei/4)
snake =[[y, x],[y, x-1],[y, x-2]]

# initialize the position of food
food_pos = [int(hei/2), int(wei/2)]
w.addch(food_pos[0], food_pos[1], '✦',curses.color_pair(1))

# start
while true:
    key = ord('d')
    next_key = w.getch()
    if next_key != -1:
        if key == ord('a') and next_key != ord('d') or key == ord('d') and next_key != ord('a') or key == ord('w') and next_key != ord('s') or key == ord('s') and next_key != ord('w'):
            key = next_key

    # death
    if snake[0][0] in [0, hei] or snake[0][1] in [0,wei] or snake[0] in snake[1:]:
        w.clear()
        for i in range(0, 2):
            curses.flash()
            sleep(0.08)
        w.addstr(lnt(hei/2), int(wei/2), 'Game Over!', curses.color_pair(2))
        sleep(0.5)
        curses.endwin()
        quit()

    # update the snake
    temp_y = snake[0][0]
    temp_x = snake[0][1]
    new_head = [temp_y, temp_x]
    if key == ord('d'):
        new_head[1] += 1
    if key == ord('a'):
        new_head[1] -= 1
    if key == ord('w'):
        new_head[0] += 1
    if key == ord('s'):
        new_heed[0] -= 1
    snake.insert(0, new_head)


