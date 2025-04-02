from enum import Enum


class Constants(Enum):
    """Enum to list all constant values relacted with times

    Attributes:
        MINUTES_TO_WORK (int): repr the time to work
        MINUTES_TO_REST (int): repr the time to rest after work time
        MINUTES_TO_LONG_REST (int): repr the long time to rest after one full pomodoro cycle
    """
    MINUTES_TO_WORK = 25
    MINUTES_TO_REST = 5
    MINUTES_TO_LONG_REST = 15


class Messages(Enum):
    """Enum to list all messages used in all the pomodoro app

    Attributes:
        WELCOME (str): Welcome to Pomodoro CLI 
        REST (str): Do a pause now!
        PAUSE (str): PAUSED!
        NOTIFY_PAUSE (str): ⏰ Your pomodoro is paused!
        NOTIFY_READY (str): ✨ Your pomodoro is ready!
        WORK (str): Back to work now!
        STATUSBAR (str): Press 'q' or 'ctrl + c' to exit | Press 'p' to pause
    """
    WELCOME = " Welcome to Pomodoro CLI "
    REST = "Do a pause now!"
    PAUSE = "PAUSED!"
    NOTIFY_PAUSE = "⏰ Your pomodoro is paused!"
    NOTIFY_READY = "✨ Your pomodoro is ready!"
    WORK = "Back to work now!"
    STATUSBAR = "Press 'q' or 'ctrl + c' to exit | Press 'p' to pause"
