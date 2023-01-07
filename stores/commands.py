from typing import Dict, Callable, Tuple, Pattern, List
import re

COMMAND_TYPE = Tuple[Pattern, Callable]
SPACE_RE = re.compile(r'\s+')

class CommandStore:
    def __init__(self):
        self.commands: Dict[str] = {}

    def set(self, *commands, **arguments):
        def wrapper(func):
            patterns: List[str] = []
            for k, v in arguments.items():
                patterns.append(f'(?P<{k}>{v})')
            pattern = re.compile('^' + '\s+'.join(patterns) + '$')
            for command in commands:
                self.commands[command] = (pattern, func)
            return func
        return wrapper

    def get(self, text):
        command, arg_text = SPACE_RE.split(text, 1)

        if command not in self.commands:
            return None

        pattern, func = self.commands[command]
        match = pattern.match(arg_text)
        if match:
            return func, match.groupdict()
