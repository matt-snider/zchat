from abc import ABC, abstractmethod


class CommandRegistry:
    _commands = {}

    def __init__(self, type, socket):
        if type not in ('client', 'server'):
            raise ValueError("type must be 'client' or 'server'")
        self._client = type == 'client'
        self._socket = socket

    @classmethod
    def register(cls, cmd):
        cls._commands[cmd.name] = cmd

    def dispatch(self, cmd_string):
        try:
            cmd_name, *args = cmd_string.split()
            command = self._commands[cmd_name]
            if self._client:
                return command.execute_client(self._socket, *args)
            else:
                return command.execute_server(self._socket, *args)
        except TypeError:
            # Invalid arguments passed
            pass
        except KeyError:
            # Command does not exist
            pass


class Command(ABC):
    name = ''
    client_help = ''

    @classmethod
    @abstractmethod
    def execute_server(cls, socket, *args):
        pass

    @classmethod
    @abstractmethod
    def execute_client(cls, socket, *args):
        pass


@CommandRegistry.register
class Connect(Command):
    name = 'CONNECT'
    client_help = """CONNECT
    Connects to the server with the chosen handle/nickname.

    Usage:
        /connect <host> <nick>
    """

    @classmethod
    def execute_client(cls, socket, host, nick):
        socket.connect('tcp://{}'.format(host))
        socket.send(b'CONNECT')
        response = socket.recv_string()
        print(response)

    @classmethod
    def execute_server(cls, socket, nick):
        print('%s connected' % nick)
        socket.send([nick, 'Welcome!'])
