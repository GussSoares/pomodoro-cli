import curses
import sys
import time

import pyfiglet

from pomodoro.constants import Constants, Messages


class Pomodoro:
    def __init__(self):
        self.pause = False
        self.minute = 0
        self.second = 0
        self.window = curses.initscr()
        self.window.nodelay(True)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    @property
    def max_y(self):
        return self.window.getmaxyx()[0]

    @property
    def max_x(self):
        return self.window.getmaxyx()[1]

    @property
    def info_message(self):
        return Messages.PAUSE.value if self.pause else Messages.WORK.value

    def update_clock(self, pause: bool = False):
        if self.second < 59:
            self.second += 1
        else:
            self.minute += 1
            self.second = 0

        if self.second == Constants.MINUTES_TO_PAUSE.value or self.pause:
            self.minute = 0
            self.second = 0
            self.pause = not self.pause

    def get_center_xpos(self, text_length: int, max_x: int = None) -> int:
        return int(((max_x or self.max_x) // 2) - (text_length // 2) - (text_length % 2))

    def get_center_ypos(self, text_height: int, max_y: int = None) -> int:
        return int(((max_y or self.max_y) // 2) + (text_height // 2) + (text_height % 2))

    def write_work_message(self):
        self.window.addstr(
            self.get_center_ypos(1),
            self.get_center_xpos(Messages.WORK.value.__len__()),
            Messages.WORK.value,
            curses.A_BOLD | curses.pair_number(1)
        )
        self.window.refresh()

    def init_panel(self):
        self.window.border()
        self.window.addstr(
            0,
            self.get_center_xpos(Messages.WELCOME.value.__len__()),
            Messages.WELCOME.value,
            curses.A_BOLD | curses.color_pair(1)
        )

        # === statusbar ===
        self.window.attron(curses.color_pair(3))
        self.window.addstr(self.max_y - 1, 1, Messages.STATUSBAR.value)
        self.window.addstr(self.max_y - 1, len(Messages.STATUSBAR.value), " " * (self.max_x - len(Messages.STATUSBAR.value) - 1))
        self.window.attroff(curses.color_pair(3))

    def main(self, _):
        while True:
            k = self.window.getch()
            quick_pause = False

            if k == ord('q'):
                sys.exit()
            if k == ord('p'):
                quick_pause = not quick_pause

            self.window.clear()
            self.init_panel()

            number = str(pyfiglet.figlet_format(f'{str(self.minute).zfill(2)}:{str(self.second).zfill(2)}'))

            aux_y = self.get_center_ypos(len(number.split('\n')), self.max_y // 2)
            for line in number.split('\n'):
                self.window.addstr(aux_y, self.get_center_xpos(line.__len__()), line)
                aux_y += 1

            self.window.addstr(aux_y, self.get_center_xpos(self.info_message.__len__()), self.info_message)

            self.update_clock(pause=quick_pause)

            self.window.refresh()
            time.sleep(1)

    def start(self):
        try:
            curses.wrapper(self.main)
        except curses.error:
            print('Very small resolution, exiting...')
            sys.exit()
