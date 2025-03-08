from enum import Enum


class Constants(Enum):
    MINUTES_TO_WORK = 25
    MINUTES_TO_REST = 5
    MINUTES_TO_LONG_REST = 15


class Messages(Enum):
    WELCOME = " Welcome to Pomodoro CLI "
    REST = "Do a pause now!"
    PAUSE = "PAUSED!"
    WORK = "Back to work now!"
    STATUSBAR = "Press 'q' or 'ctrl + c' to exit | STATUS BAR"
