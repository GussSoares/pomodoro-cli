import argparse
import importlib.metadata
import sys

from pomodoro import Pomodoro


def init_args() -> argparse.Namespace:
    """Initialize arguments and return arg parser"""
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--restore', action='store_true', help='restore previous pomodoro closed')
    parser.add_argument('-m', '--mute', action='store_true', help='mute pomodoro alarms')
    parser.add_argument('-c', '--config', action='store_true', help='(coming soon) configure times to your custom values')
    parser.add_argument('-v', '--version', action='store_true', help='show current version')
    
    return parser.parse_args()


def version() -> None:
    """
    Print the current app version

    >>> pomodoro --version
    ✨ 1.0.0
    """
    print(f'✨ {importlib.metadata.version("pomodoro-app-cli")}')
    sys.exit()


def main():
    args = init_args()
    
    if args.version:
        version()

    pmdr = Pomodoro(restore=args.restore, mute=args.mute)
    try:
        pmdr.start()
    except KeyboardInterrupt:
        pmdr.save()
        sys.exit()


if __name__ == '__main__':
    main()
