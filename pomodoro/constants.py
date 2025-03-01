from enum import Enum


class Constants(Enum):
    MINUTES_TO_PAUSE = 25


class Messages(Enum):
    WELCOME = " Welcome to Pomodoro CLI "
    PAUSE = "Do a pause now!"
    WORK = "Back to work now!"
    STATUSBAR = "Press 'q' or 'ctrl + c' to exit | STATUS BAR"
