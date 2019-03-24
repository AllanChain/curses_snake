import curses
from time import sleep
from random import randint, random
from sys import platform


class TimeBar:
    def __init__(self, limit, MAX, y, delay):
        self.LIMIT = 100
        self._pause = False
        self.unit = limit / MAX
        self.head = self.MAX = MAX
        self.y = y
        self.count = 0
        self.delay = delay
        w.timeout(delay)
        self.refill()

    def reduce(self):
        if self._pause:
            return
        self.count += 1
        if self.count >= self.unit:
            self.count -= self.unit
            w.addstr(self.y, self.head, '<', curses.color_pair(2))
            self.head -= 1
            if self.head == -1:
                death()

    def refill(self):
        self._pause = False
        w.addstr(self.y, 0, ' ' * self.MAX, curses.color_pair(1))
        self.head = self.MAX
        self.delay = int(self.delay * 0.98)
        w.timeout(self.delay)

    def pause(self):
        self._pause = True

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


class PassFood(Food):
    def draw(self):
        draw_block(self.pos, 5)

    def consume(self):
        pass


class TimeLimitFood(Food):
    def __init__(self, pos):
        self.time = int((2-random()**3)*40)
        self.count = 0
        self.INTERVAL = 3
        self.blink = 1
        Food.__init__(self, pos)

    def draw(self):
        if self.blink:
            draw_block(self.pos)
        else:
            draw_block(self.pos, 0)

    def wipe(self):
        draw_block(self.pos, 0)

    def tick(self):
        self.count += 1
        if self.count > self.INTERVAL:
            self.count = 0
            self.blink = 1 - self.blink
        self.time -= 1
        if self.time == -1:
            self.wipe()
            return False
        self.draw()
        return True


class PauseFood(TimeLimitFood):
    def draw(self):
        if self.blink:
            draw_block(self.pos, 4)
        else:
            draw_block(self.pos, 0)

    def consume(self):
        timer.pause()

class BonusFood(TimeLimitFood):
    def draw(self):
        if self.blink:
            draw_block(self.pos, 5)
        else:
            draw_block(self.pos, 4)

    def consume(self):
        global SNOW_FIELD
        SNOW_FIELD = True
        if self.blink:
            for i in range(10):
                foods.produce()
        else:
            SNOW_FIELD = True

class FoodMgr:
    DISTRIBUTION_SERIES = ((0.2, TimeLimitFood),
                          (0.05, PauseFood),
                           (0.2, PassFood),
                           (0.5, BonusFood))

    def __init__(self):
        self.foods = []
        self.produce()

    def update(self, head):
        for food in self.foods:
            if not food.tick():
                self.foods.remove(food)
                continue
            if food.pos == head:
                food.consume()
                self.foods.remove(food)
                ratio = 1 - 0.2 * len(self.foods) + 0.02 * snake.length()
                flag = True
                break
        else:
            ratio = 0.05 - 0.02 * len(self.foods) + 0.002 * snake.length()
            flag = False
        if random() < ratio:
            self.produce()
        return flag

    def produce(self):
        excludes = snake.body() + list(map(lambda f: f.pos, self.foods))
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
            self.foods.append(Food(new_food_pos))


class Snake:
    def __init__(self):
        y = int(hei/2)
        x = int(wei/4)
        self._snake = [(y, x), (y, x-1), (y, x-2)]
        self.key = ord('d')
        self.keys = [ord('w'), ord('a'), ord('s'), ord('d')]
        self.SNOW_FIELD = False

    def body(self):
        return self._snake

    def length(self):
        return len(self._snake)

    def go(self, next_key):
        if next_key in self.keys and (self.keys.index(self.key)-self.keys.index(next_key)) % 2 != 0:
            self.key = next_key
            w.addstr(1, 0, 'Current key= %s' % chr(self.key))  # debug
        new_head = list(self._snake[0])
        if self.key == ord('d'):
            new_head[1] += 1
        if self.key == ord('a'):
            new_head[1] -= 1
        if self.key == ord('w'):
            new_head[0] -= 1
        if self.key == ord('s'):
            new_head[0] += 1
        self._snake.insert(0, tuple(new_head))

    def test_death(self):
        return self._snake[0][0] in (-1, hei) or self._snake[0][1] in (-1, wei) or self._snake[0] in self._snake[1:]

    def bite(self):
        w.addstr(3, 0, str(self._snake[0]))  # debug
        if not foods.update(self._snake[0]):
            draw_block(self._snake.pop(), 0)
        w.addstr(2, 0, "Length:%s" %len(self._snake))  # debug

    def move(self):
        if not self.SNOW_FIELD:
            draw_block(self._snake[0], 3)

def draw_block(pos, color=1, style='  '):
    y, x = pos
    w.addstr(y, 2*x, style, curses.color_pair(color))


def init_curses():
    # initialize the screen
    s = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()
    # initialize the window
    global hei, wei, w
    if platform == 'win32':
        curses.resize_term(40, 80)
    hei, wei = s.getmaxyx()
    wei = wei if wei % 2 == 0 else wei-1
    w = curses.newwin(hei, wei, 0, 0)
    w.keypad(1)
    wei = wei//2
    hei -= 1
    # initialize color_pairs
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_MAGENTA)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_YELLOW)


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
    # initialize the position of snake
    global snake
    global timer, foods, SNOW_FIELD
    snake = Snake()
    timer = TimeBar(100, wei * 2 - 2, hei, 150)
    foods = FoodMgr()
    while True:
        next_key = w.getch()
        timer.reduce()
        snake.go(next_key)
        # pause and resume
        if next_key == ord('p') and snake.key in keys:
            w.addstr(2, int(wei), "Pause")
            while True:
                a = w.getch()
                if a == ord('r'):
                    w.addstr(2, int(wei), "         ")
                    break
        # death
        if snake.test_death():
            death()
        snake.bite()
        snake.move()


if __name__ == '__main__':
    try:
        init_curses()
        main()
    finally:
        curses.endwin()
