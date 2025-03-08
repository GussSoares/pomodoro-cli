import curses
import os
import sys
import time
import pathlib
import configparser
import subprocess

import pyfiglet

from pomodoro.constants import Constants, Messages


PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


class Pomodoro:
    def __init__(self, restore: bool = False, mute: bool = False):
        self.mute = mute
        self.pause = False
        self.rest = False
        self.minute = 0
        self.second = 0
        self.loop = 0
        self.window = curses.initscr()
        self.window.nodelay(True)

        self.config_file_path = os.path.join(PACKAGE_DIR, 'settings.ini')

        self.init_config_file()

        if restore:
            config = self.get_config()
            self.pause = eval(config['Settings']['pause'])
            self.rest = eval(config['Settings']['rest'])
            self.minute = eval(config['Settings']['minute'])
            self.second = eval(config['Settings']['second'])

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
        if self.pause:
            return Messages.PAUSE.value
        if self.rest:
            return Messages.REST.value
        return Messages.WORK.value

    def play_audio(self):
        process = subprocess.Popen(['aplay', f'{PACKAGE_DIR}/audio.wav'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(4)
        process.kill()

    def notify(self, message: str):
        subprocess.Popen(['notify-send', '-a', 'Pomodoro-app-cli', 'Pomodoro', message, '-i', 'terminal', '-t', '5000'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def init_config_file(self):
        if not pathlib.Path(self.config_file_path).exists():
            with open(self.config_file_path, 'w'):
                self.set_config()

    def get_config(self) -> dict:
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        return config

    def set_config(self) -> None:
        with open(self.config_file_path, 'w') as configfile:
            config = configparser.ConfigParser()
            config['Settings'] = {
                'pause': self.pause,
                'rest': self.rest,
                'minute': self.minute,
                'second': self.second,
                'loop': self.loop,
            }
            config.write(configfile)

    def save(self) -> None:
        self.set_config()

    def update_clock(self):
        long_rest = False
        
        if self.pause:
            return

        if self.second < 59:
            self.second += 1
        else:
            self.minute += 1
            self.second = 0


        if self.loop == 4:
            long_rest = True

        if self.minute == Constants.MINUTES_TO_WORK.value:
            self.minute = 0
            self.second = 0
            self.rest = True
            self.notify(Messages.REST.value)
            if not self.mute:
                self.play_audio()

        if self.rest and self.minute == Constants.MINUTES_TO_REST.value and not long_rest:
            self.minute = 0
            self.second = 0
            self.rest = False
            self.loop += 1
            self.notify(Messages.WORK.value)
            if not self.mute:
                self.play_audio()

        elif self.rest and self.minute == Constants.MINUTES_TO_LONG_REST.value and long_rest:
            self.minute = 0
            self.second = 0
            self.rest = False
            self.loop =  0
            long_rest = False
            self.notify(Messages.WORK.value)
            if not self.mute:
                self.play_audio()

    def get_center_xpos(self, text_length: int, max_x: int = None) -> int:
        return int(((max_x or self.max_x) // 2) - (text_length // 2) - (text_length % 2))

    def get_center_ypos(self, text_height: int, max_y: int = None) -> int:
        return int(((max_y or self.max_y) // 2) + (text_height // 2) - (text_height % 2))

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

            if k == ord('q'):
                self.save()
                sys.exit()
            if k == ord('p'):
                self.pause = not self.pause
                if self.pause:
                    self.notify(Messages.NOTIFY_PAUSE.value)
                else:
                    self.notify(Messages.NOTIFY_READY.value)

            self.window.clear()
            self.init_panel()

            number = str(pyfiglet.figlet_format(f'{str(self.minute).zfill(2)}:{str(self.second).zfill(2)}'))

            aux_y = self.get_center_ypos(len(number.split('\n')), self.max_y // 2)
            for line in number.split('\n'):
                self.window.addstr(aux_y, self.get_center_xpos(line.__len__()), line)
                aux_y += 1

            self.window.addstr(aux_y, self.get_center_xpos(self.info_message.__len__()), self.info_message)

            self.update_clock()

            self.window.refresh()
            time.sleep(1)

    def start(self):
        try:
            curses.wrapper(self.main)
        except curses.error:
            print('Very small resolution, exiting...')
            sys.exit()
