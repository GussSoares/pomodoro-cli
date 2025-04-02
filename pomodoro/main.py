import argparse
import importlib.metadata
import sys

from pomodoro import Pomodoro


def init_args() -> argparse.Namespace:
    """
    Initialize arguments and return arg parser
    
    Attributes:
        -r,--restore (bool): restore previous pomodoro closed
        -m,--mute (bool): mute pomodoro alarms
        -c,--config (bool): configure times to your custom values
        -u,--update (bool): update your pomodoro app version
        -v,--version (bool): show current version
    
    Returns:
        parser (Namespace): a object with all arguments
    
    Example
    -------
    ``` python
    args = init_args()
    args.restore
    True
    ```
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--restore', action='store_true', help='restore previous pomodoro closed')
    parser.add_argument('-m', '--mute', action='store_true', help='mute pomodoro alarms')
    parser.add_argument('-c', '--config', action='store_true', help='configure times to your custom values')
    parser.add_argument('-u', '--update', action='store_true', help='update your pomodoro app version')
    parser.add_argument('-v', '--version', action='store_true', help='show current version')
    
    return parser.parse_args()


def version() -> None:
    """
    Print the current app version

    Example
    -------
    ``` sh
    pomodoro --version
    ✨ 1.0.0
    ```
    """
    print(f'✨ {importlib.metadata.version("pomodoro-app-cli")}')
    sys.exit()


def main():
    args = init_args()

    match True:
        case args.config:
            try:
                Pomodoro(no_interface=True).prompt_config()
            except KeyboardInterrupt:
                sys.exit()

        case args.version:
            Pomodoro.version(show=True)
            sys.exit()

        case args.update:
            Pomodoro.update()
            sys.exit()

        case _:
            pmdr = Pomodoro(restore=args.restore, mute=args.mute)
            try:
                pmdr.start()
            except KeyboardInterrupt:
                pmdr.save()
                sys.exit()


if __name__ == '__main__':
    main()
