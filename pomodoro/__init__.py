import curses
import os
import sys
import time
import pathlib
import importlib
import configparser
import subprocess
from typing import Dict

import pyfiglet

from pomodoro.constants import Constants, Messages
from pomodoro.config import Config


PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(PACKAGE_DIR, 'settings.ini')


class Pomodoro:
    def __init__(self, restore: bool = False, mute: bool = False, no_interface: bool = False):
        self.mute = mute
        self.pause = False
        self.rest = False
        self.minute = 0
        self.second = 0
        self.loop = 0
        self.init_config_file()
        self.config = self.get_config()

        if restore:
            self.pause = eval(self.config['Settings']['pause'])
            self.rest = eval(self.config['Settings']['rest'])
            self.minute = eval(self.config['Settings']['minute'])
            self.second = eval(self.config['Settings']['second'])

        if no_interface:
            return

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
    def minutes_to_work(self):
        return self.config['CustomTime']['work_time']

    @property
    def minutes_to_rest(self):
        return self.config['CustomTime']['rest_time']

    @property
    def info_message(self):
        if self.pause:
            return Messages.PAUSE.value
        if self.rest:
            return Messages.REST.value
        return Messages.WORK.value

    @staticmethod
    def version(show: bool = False) -> str:
        version = importlib.metadata.version("pomodoro-app-cli")
        if show:
            print(f'✨ {version}')
        return version

    @staticmethod
    def update() -> None:
        Config().update(lambda: subprocess.check_output(['pip', 'install', '--upgrade', 'pomodoro-app-cli', '--break-system-packages']))
        Pomodoro.version(show=True)
        # subprocess.Popen(['pip', 'install', '--upgrade', 'pomodoro-app-cli', '--break-system-packages'])
        sys.exit()

    def play_audio(self):
        subprocess.Popen(['aplay', f'{PACKAGE_DIR}/audio.wav', '--duration', '2'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def notify(self, message: str):
        subprocess.Popen(['notify-send', '-a', 'Pomodoro-app-cli', 'Pomodoro', message, '-i', 'terminal', '-t', '5000'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def init_config_file(self):
        if not pathlib.Path(SETTINGS_PATH).exists():
            config = configparser.ConfigParser()
            config['CustomTime'] = {
                'work_time': Constants.MINUTES_TO_WORK.value,
                'rest_time': Constants.MINUTES_TO_REST.value
            }
            config['Settings'] = {
                'pause': self.pause,
                'rest': self.rest,
                'minute': self.minute,
                'second': self.second,
                'loop': self.loop,
            }
            with open(SETTINGS_PATH, 'w') as configfile:
                config.write(configfile)

    def prompt_config(self):
        Config().set_config(self.set_custom_time)

    @staticmethod
    def get_config() -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(SETTINGS_PATH)
        return config

    def set_config(self, config: Dict[str, dict]) -> None:
        _config = self.get_config()

        for section, conf in config.items():
            if not _config.has_section(section):
                _config.add_section(section)

            for k, v in conf.items():
                _config.set(section, k, str(v))

        with open(SETTINGS_PATH, 'w') as configfile:
            _config.write(configfile)

    def set_custom_time(self, work_time: int = None, rest_time: int = None) -> None:
        SECTION = 'CustomTime'
        config = self.get_config()

        if not config.has_section(SECTION):
            config.add_section(SECTION)

        if work_time is not None:
            config.set(SECTION, 'work_time', work_time)
        if rest_time is not None:
            config.set(SECTION, 'rest_time', rest_time)

        with open(SETTINGS_PATH, 'w') as configfile:
            config.write(configfile)

    def save(self) -> None:
        self.set_config(config={
            'Settings': {
                'pause': self.pause,
                'rest': self.rest,
                'minute': self.minute,
                'second': self.second,
                'loop': self.loop,
            }
        })

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

        if self.minute == self.minutes_to_work:
            self.minute = 0
            self.second = 0
            self.rest = True
            self.notify(Messages.REST.value)
            if not self.mute:
                self.play_audio()

        if self.rest and self.minute == self.minutes_to_rest and not long_rest:
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

        self.window.attron(curses.color_pair(3) | curses.A_BOLD)
        self.window.addstr(self.max_y - 4, 0, f' * Work time: {self.minutes_to_work} minutes ')
        self.window.addstr(self.max_y - 3, 0, f' * Rest time: {self.minutes_to_rest} minutes ')

        # === statusbar ===
        self.window.addstr(self.max_y - 1, 1, Messages.STATUSBAR.value)
        self.window.addstr(self.max_y - 1, len(Messages.STATUSBAR.value) + 1, " " * (self.max_x - len(Messages.STATUSBAR.value) - 2))
        self.window.attroff(curses.color_pair(3))

    def main(self, _):
        self.play_audio()
        try:
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

                self.window.erase()
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
        except Exception:
            curses.endwin()

    def start(self):
        try:
            curses.wrapper(self.main)
        except curses.error:
            print('Very small resolution, exiting...')
        finally:
            self.save()
            sys.exit()
