import curses
from time import sleep
from random import randint, random


class TimeBar:
    def __init__(self, limit, MAX, x, delay):
        self.LIMIT = 100
        self.unit = limit / MAX
        self.head = self.MAX = MAX
        self.x = x
        self.count = 0
        self.delay = delay
        w.timeout(delay)
        self.refill()

    def reduce(self):
        self.count += 1
        if self.count >= self.unit:
            self.count -= self.unit
            w.addch(self.head, self.x, ' ')
            self.head -= 1
            if self.head == -1:
                death()

    def refill(self):
        for y in range(self.MAX):
            w.addch(y, self.x, ' ', curses.color_pair(1))
        self.head = self.MAX
        self.delay = int(self.delay * 0.98)
        w.timeout(self.delay)


class Food:
    def __init__(self, pos, s=False):
        self.pos = pos
        w.addstr(0, 0, str(self.pos))  # debug
        w.refresh()
        self.draw()

    def draw(self):
        draw_block(self.pos)

    def tick(self):
        return True

    def consume(self):
        timer.refill()


class NormalFood(Food):
    pass


class TimeLimitFood(Food):
    def __init__(self, pos):
        self.time = int((2-random()**3)*40)
        self.blink = 1
        Food.__init__(self, pos)

    def draw(self):
        if self.blink:
            draw_block(self.pos)
        else:
            draw_block(self.pos, 0)
        self.blink = 1 - self.blink

    def tick(self):
        self.time -= 1
        if self.time == -1:
            self.blink = 0
            self.draw()
            return False
        self.draw()
        return True


class FoodMgr:
    DISTRIBUTION_SERIES = ((0.9, TimeLimitFood),)

    def __init__(self):
        self.foods = []
        self.produce()

    def update(self):
        head = snake[0]
        for food in self.foods:
            if not food.tick():
                self.foods.remove(food)
                continue
            if food.pos == head:
                food.consume()
                self.foods.remove(food)
                ratio = 1 - 0.2 * len(self.foods)
                flag = True
                break
        else:
            ratio = 0.05 - 0.02 * len(self.foods)
            flag = False
        if random() < ratio:
            self.produce()
        return flag

    def produce(self):
        excludes = snake + list(map(lambda f: f.pos, self.foods))
        def food_pos(): return (randint(1, hei-1), randint(1, wei-1))
        new_food_pos = food_pos()
        while new_food_pos in excludes:
            new_food_pos = food_pos()
        rand_point = random()
        stop_point = 0
        for ratio, food_factory in self.DISTRIBUTION_SERIES:
            stop_point += ratio
            if rand_point < stop_point:
                self.foods.append(food_factory(new_food_pos))
                break
        else:
            self.foods.append(NormalFood(new_food_pos))


def draw_block(pos, color=1):
    y, x = pos
    w.attron(curses.color_pair(color))
    w.addch(y, 2*x, ' ')
    w.addch(y, 2*x+1, ' ')
    w.attroff(curses.color_pair(color))


def init_curses():
    # initialize the screen
    s = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()
    # initialize the window
    global hei, wei, w
    curses.resize_term(40, 81)
    hei, wei = s.getmaxyx()
    wei = wei - 1 if wei % 2 == 0 else wei
    w = curses.newwin(hei, wei, 0, 0)
    w.keypad(1)
    wei = wei//2
    # initialize color_pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)


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
    key = ord('d')
    keys = [ord('w'), ord('a'), ord('s'), ord('d')]
    # initialize the position of snake
    global snake
    global timer
    y = int(hei/2)
    x = int(wei/4)
    snake = [(y, x), (y, x-1), (y, x-2)]
    timer = TimeBar(100, hei-2, 2*wei, 150)
    foods = FoodMgr()
    while True:
        next_key = w.getch()
        timer.reduce()
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
        new_head = list(snake[0])
        if key == ord('d'):
            new_head[1] += 1
        if key == ord('a'):
            new_head[1] -= 1
        if key == ord('w'):
            new_head[0] -= 1
        if key == ord('s'):
            new_head[0] += 1
        snake.insert(0, tuple(new_head))
        # death
        if snake[0][0] in (-1, hei) or snake[0][1] in (-1, wei) or snake[0] in snake[1:]:
            death()
        # eat
        w.addstr(3, 0, str(snake[0]))  # debug
        if not foods.update():
#        if snake[0] == food.pos:
#            food = Food()
#            timer.refill()
#            w.refresh()
        # remove the tail
#        else:
            tail = snake.pop()
            draw_block(tail, 0)
        w.addstr(2, 0, "Length:%s" % (len(snake)))  # debug
        # move
        draw_block(snake[0], 3)


if __name__ == '__main__':
    try:
        init_curses()
        main()
    finally:
        curses.endwin()
