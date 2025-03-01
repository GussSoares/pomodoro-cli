import sys

from pomodoro import Pomodoro


def main():
    try:
        pmdr = Pomodoro()
        pmdr.start()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    main()
