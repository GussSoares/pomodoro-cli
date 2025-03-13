from rich.console import Console
from InquirerPy import inquirer
from InquirerPy.validator import ValidationError, Validator


console = Console()

class ValidateMinute(Validator):
    def __init__(self, interval_start: int, interval_end: int):
        super().__init__()
        self.interval_start = interval_start
        self.interval_end = interval_end

    def validate(self, document):
        if not document.text.isnumeric():
            raise ValidationError(
                message='Must be a number',
                cursor_position=document.cursor_position
            )
        if not len(document.text):
            raise ValidationError(
                message='Required field',
                cursor_position=document.cursor_position
            )
        if not (self.interval_start <= int(document.text) <= self.interval_end):
            raise ValidationError(
                message=f'Must be between {self.interval_start} and {self.interval_end}',
                cursor_position=document.cursor_position
            )
        return True


class Config:

    @staticmethod
    def get_minutes(message: str, start: int, end: int, default: str = '25'):
        return inquirer.text(
            message=message,
            default=default,
            validate=ValidateMinute(interval_start=start, interval_end=end)
        ).execute()

    @staticmethod
    def confirm():
        return inquirer.confirm('Are you sure?').execute()

    def set_config(self, func, *args, **kwargs):
        console.rule('Pomodoro Customization')

        minutes_to_work = self.get_minutes(
            message='Type minutes to work: ',
            default='25',
            start=25,
            end=35
        )
        minutes_to_rest = self.get_minutes(
            message='Type minutes to rest: ',
            default='5',
            start=5,
            end=15
        )
        
        if self.confirm():
            with console.status('Please wait...'):
                func(minutes_to_work, minutes_to_rest)
            console.print('[green]Finished![/]')

    def update(self, func):
        with console.status('Updating. Please wait...'):
            func()
        console.print('[green]Finished![/]')