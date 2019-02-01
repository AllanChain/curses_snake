import curses
from time import sleep
from random import randint

def init():
    # initialize the screen
    s = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()

    # initialize the window
    global hei, wei, w
    hei, wei = s.getmaxyx()
    w = curses.newwin(hei, wei, 0, 0)
    w.keypad(1)
    w.timeout(100)
    # initialize color_pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # initialize the position of snake
    global snake
    y = int(hei/2)
    x = int(wei/4)
    snake =[[y, x],[y, x-1],[y, x-2]]

    # initialize the position of food
    global food_pos
    food_pos = [int(hei/2), int(wei/2)]
    w.attron(curses.color_pair(1))
    w.addch(food_pos[0], food_pos[1], '✦')
    w.attroff(curses.color_pair(1))
    # the initial direction
    global key
    key = ord('d')
    global keys
    keys = {ord('a'), ord('d'), ord('w'), ord('s'), ord('r')}

def pause():
    global pre_key, key
    pre_key = key
    w.nodelay(0)
def resume():
    global pre_key
    key =pre_key
    w.nodelay(1)
def death():
    for i in range(0, 4):
        curses.flash()
        sleep(0.08)
    w.clear()
    w.addstr(int(hei/2), int(wei/2), 'Game Over!', curses.color_pair(2))
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
    while True:
        next_key = w.getch()
        if next_key != -1:
            if key == ord('a') and next_key in keys and next_key != ord('d') or key == ord('d') and next_key in keys and next_key != ord('a') or key == ord('w') and next_key in keys and next_key != ord('s') or key == ord('s') and next_key in keys and next_key != ord('w') or key == ord('p') and next_key == ord('r'):
                key = next_key
            # pause
            if next_key == ord('p') and key in keys:
                pause()
            if key == ord('r'): # resume
                resume()
        # death
        if snake[0][0] in [0, hei-1] or snake[0][1] in [0, wei-1] or snake[0] in snake[1:]:
           death() 
        # update the snake(turn)
        else:
            temp_y = snake[0][0]
            temp_x = snake[0][1]
            new_head = [temp_y, temp_x]

            if key == ord('d'):
                new_head[1] += 1
            if key == ord('a'):
                new_head[1] -= 1
            if key == ord('w'):
                new_head[0] -= 1
            if key == ord('s'):
                new_head[0] += 1
            snake.insert(0, new_head)
        
        # eat
        if snake[0] == food_pos:
            food_pos = None
            '''while food_pos is None:
                new_food_pos = (randint(1, hei-1),randint(1, wei-1))
                if new_food_pos not in snake:
                    food_pos = new_food_pos
            w.attron(curses.color_pair(1))
            w.addch(food_pos[0], food_pos[1],'✦')
            w.attroff(curses.color_pair(1))'''
        
        # remove the tail
        else:
            tail = snake.pop() 
            w.addch(tail[0], tail[1], ' ')
       
        # spawn new food
        while food_pos is None:
            new_food_pos = (randint(1, hei-1),randint(1, wei-1))
            if new_food_pos not in snake:
                food_pos = new_food_pos
                w.addstr(0, 0, str(food_pos)) # debug
                w.refresh()
        w.attron(curses.color_pair(1))
        w.addch(food_pos[0], food_pos[1],'✦')
        w.attroff(curses.color_pair(1))

        # move
        w.attron(curses.color_pair(3))
        w.addch(snake[0][0], snake[0][1], '@', curses.color_pair(3))
        w.attroff(curses.color_pair(3))

init()
main()
