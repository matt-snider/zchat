from abc import ABC, abstractmethod


class CommandRegistry:
    _commands = {}

    def __init__(self, owner, is_client=False):
        self._client = is_client
        self._owner = owner

    @classmethod
    def register(cls, cmd):
        cls._commands[cmd.name] = cmd

    def dispatch(self, cmd_string):
        cmd_name, *args = cmd_string.split()
        try:
            command = self._commands[cmd_name.upper()]
            if self._client:
                return command.execute_client(self._owner, *args)
            else:
                return command.execute_server(self._owner, *args)
        except TypeError:
            raise InvalidArgument(*args)
        except KeyError:
            raise InvalidCommand(cmd_name)


class InvalidCommand(Exception):
    pass


class InvalidArgument(Exception):
    pass


class Command(ABC):
    name = ''
    client_help = ''

    @classmethod
    @abstractmethod
    def execute_server(cls, server, *args):
        pass

    @classmethod
    @abstractmethod
    def execute_client(cls, client, *args):
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
    def execute_client(cls, client, host, nick):
        client.socket.identity = nick.encode()
        client.socket.connect('tcp://{}'.format(host))
        client.socket.send(b'CONNECT')
        welcome = client.socket.recv_string()
        print(welcome)

    @classmethod
    def execute_server(cls, server, nick):
        print('%s connected' % nick)
        server.socket.send_multipart([nick, 'Welcome!'])
