from typing import Dict, Callable, Tuple, Pattern, List
import re

COMMAND_TYPE = Tuple[Pattern, Callable]
SPACE_RE = re.compile(r'\s+')

class CommandEngine:
    def __init__(self):
        self.commands: Dict[str] = {}

    def add(self, *commands, **arguments):
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
        match = SPACE_RE.split(text, 1)
        if len(match) == 1:
            command, arg_text = match[0], ''
        else:
            command, arg_text = match

        if command not in self.commands:
            return None

        pattern, func = self.commands[command]
        match = pattern.match(arg_text)
        if match:
            return func, match.groupdict()
