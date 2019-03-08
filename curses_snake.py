import curses
from time import sleep
from random import randint


TIME_LIMIT = 100
def draw_block(pos, color=1):
    y, x = pos
    w.attron(curses.color_pair(color))
    w.addch(y, 2*x, ' ')
    w.addch(y, 2*x+1, ' ')
    w.attroff(curses.color_pair(color))

def draw_time(time):
    time = int(time / TIME_LIMIT * 40)
    for y in range(time):
        w.addch(y, 80, '#')
    for y in range(time,39):
        w.addch(y, 80, ' ')

def init():
    # initialize the screen
    s = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()

    # initialize the window
    global hei, wei, w
    curses.resize_term(40, 81)
    hei, wei = s.getmaxyx()
    w = curses.newwin(hei, wei, 0, 0)
    w.keypad(1)
    w.timeout(100)
    wei = wei//2
    # initialize color_pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # initialize the position of snake
    global snake
    y = int(hei/2)
    x = int(wei/4)
    snake = [[y, x], [y, x-1], [y, x-2]]

    # initialize the position of food
    global food_pos
    food_pos = [int(hei/2), int(wei/2)]
    draw_block(food_pos)
    # the initial direction
    global key
    key = ord('d')
    global keys
    keys = [ord('w'), ord('a'), ord('s'), ord('d')]


def death():
    for i in range(0, 4):
        curses.flash()
        sleep(0.08)
    w.clear()
    w.addstr(int(hei/2), int(wei), 'Game Over!', curses.color_pair(2))
    w.refresh()
    sleep(1.5)
    curses.endwin()
    quit()

# start


def main():
    global key
    global keys
    global food_pos
    global snake
    time = TIME_LIMIT
    while True:
        next_key = w.getch()
        time -= 1
        if time < 0:
            death()
        draw_time(time)
        if next_key in keys and (keys.index(key)-keys.index(next_key)) % 2 != 0:
            key = next_key
            w.addstr(1, 0, 'Current key= %s' % chr((key)))  # debug
        # pause and resume
        if next_key == ord('p') and key in keys:
            w.addstr(2, int(wei), "Pause")
            while True:
                a = w.getch()
                if a == ord('r'):
                    w.addstr(2, int(wei), "         ")
                    break
        # update the snake(turn)
        new_head = snake[0].copy()

        if key == ord('d'):
            new_head[1] += 1
        if key == ord('a'):
            new_head[1] -= 1
        if key == ord('w'):
            new_head[0] -= 1
        if key == ord('s'):
            new_head[0] += 1
        snake.insert(0, new_head)
        # death
        if snake[0][0] in (-1, hei) or snake[0][1] in (-1, wei) or snake[0] in snake[1:]:
            death()

        # eat
        w.addstr(3, 0, str(snake[0]))  # debug
        if snake[0] == food_pos:
            food_pos = None
            w.refresh()

        # remove the tail
        else:
            tail = snake.pop()
            draw_block(tail, 0)
        w.addstr(2, 0, "Length:%s" % (len(snake)))  # debug
        # spawn new food
        while food_pos is None:
            time = TIME_LIMIT
            new_food_pos = [randint(1, hei-1), randint(1, wei-1)]
            if new_food_pos not in snake:
                food_pos = new_food_pos
                w.addstr(0, 0, str(food_pos))  # debug
                w.refresh()
        draw_block(food_pos)

        # move
        draw_block(snake[0], 3)


if __name__ == '__main__':
    try:
        init()
        main()
    finally:
        curses.endwin()

