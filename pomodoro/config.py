from rich.console import Console
from InquirerPy import inquirer
from InquirerPy.validator import ValidationError, Validator


console = Console()

class ValidateMinute(Validator):
    """
    ValidateMinute created to validate minutes in interval passed by user
    
    Attributes:
        interval_start (int): initial value
        interval_end (int): end value
    
    Methods:
        validate() -> bool: return `True` for valid input
    """
    def __init__(self, interval_start: int, interval_end: int):
        super().__init__()
        self.interval_start = interval_start
        self.interval_end = interval_end

    def validate(self, document):
        """
        Validate input passed by user
        
        Attributes:
            document (Document): implicit attribute that contains input and position cursor
        
        Returns:
            validation (bool): return `True` if valid input
        
        Raises:
            ValidationError: Must be a number
            ValidationError: Required field
            ValidationError: Must between min and max
        """
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
    """
    Config class for CLI
    
    Methods:
        get_minutes() -> str: Execute a inquirer promp to receive minutes with validations 
        config() -> bool: Confirm if you are sure of your answers
        set_config() -> None: Show a pretty prompt for user pass minutes to work, minutes to rest and confirm it
    """

    @staticmethod
    def get_minutes(message: str, start: int, end: int, default: str = '25'):
        """
        Execute a inquirer promp to receive minutes with validations
        
        Attributes:
            message (str): a message to show in prompt
            start (int): the min value to validate like a interval
            start (int): the max value to validate like a interval
            default (str): the default value if user no pass nothing
        
        Returns:
            minutes (str): the value prompted by user
        """
        return inquirer.text(
            message=message,
            default=default,
            validate=ValidateMinute(interval_start=start, interval_end=end)
        ).execute()

    @staticmethod
    def confirm():
        """
        Confirm if you are sure of your answers
        
        Returns:
            confirm (bool): True if user confirm and False if user abort
        """
        return inquirer.confirm('Are you sure?').execute()

    def set_config(self, func, *args, **kwargs):
        """
        Show a pretty prompt for user pass minutes to work, minutes to rest and confirm it
        
        Attributes:
            func (function): a function to execute after confirm prompt
            *args (tuple): arguments for function passed
            **kwargs (dict): arguments for function passed
        """
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
        """
        Show a pretty prompt for update your pomodoro
        
        Attributes:
            func (function): a function to execute your update 
        """
        with console.status('Updating. Please wait...'):
            func()
        console.print('[green]Finished![/]')