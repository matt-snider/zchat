from abc import ABC, abstractmethod


class Command(ABC):
    _commands = {}

    @classmethod
    def register(cls, cmd):
        cls._commands[cmd.name] = cmd

    @classmethod
    def dispatch(cls, cmd_string):
        try:
            cmd_name, *args = cmd_string.split()
            command = cls._commands[cmd_name]
            return command.execute(*args)
        except TypeError:
            # Invalid arguments passed
            pass
        except KeyError:
            # Command does not exist
            pass

    @abstractmethod
    def execute(self, *args):
        pass
