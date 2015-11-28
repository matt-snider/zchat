import json
from abc import ABC, abstractmethod
from functools import partial


class CommandRegistry(ABC):
    _server_commands = {}
    _client_commands = {}
    _command_list = set()

    def __init__(self):
        for name, command in self._commands.items():
            self._commands[name] = partial(command, self)

    @property
    @abstractmethod
    def _commands(self):
        return []

    @classmethod
    def register(cls, cmd):
        assert issubclass(cmd, Command), '%s is not command' % cmd

        cmd_name = cmd.get_name()
        cls._server_commands[cmd_name] = cmd.server
        cls._client_commands[cmd_name] = cmd.client
        cls._command_list.add(cmd_name)
        return cmd

    def dispatch(self, cmd_string, user=None):
        cmd_string, *trailing_arg = cmd_string.split(' :')
        cmd_name, *args = cmd_string.split()
        args.extend(trailing_arg)
        if user:
            args.insert(0, user)

        try:
            command = self._commands[cmd_name.upper()]
            command(*args)
        except TypeError as e:
            raise InvalidArgument(*args)
        except KeyError as e:
            raise InvalidCommand(cmd_name)

    @classmethod
    def get_list(cls):
        return sorted(cls._command_list)


class InvalidCommand(Exception):
    pass


class InvalidArgument(Exception):
    pass


class Command(ABC):

    @classmethod
    def get_help(cls):
        return cls.__doc__

    @classmethod
    def get_name(cls):
        return cls.get_help().split('\n', 1)[0].strip()

    @abstractmethod
    def server(self, user, *args):
        pass

    @abstractmethod
    def client(self, *args):
        pass


@CommandRegistry.register
class Connect(Command):
    """CONNECT

    Connects to the server with the chosen handle/nickname.

    Usage:
        /connect <host> <nick>
    """

    def client(self, host, nick):
        self.socket.identity = nick.encode()
        self.socket.connect('tcp://{}'.format(host))
        self.socket.send(b'CONNECT')
        welcome = self.socket.recv_string()
        self.print_server_response(welcome)

    def server(self, user):
        print('%s connected' % user)
        self.socket.send_multipart([user, self.welcome])
        self.clients.append(user.decode())


@CommandRegistry.register
class Users(Command):
    """USERS

    Lists the users on the current server
    
    Usage:
        /users 
    """

    def client(self):
        self.socket.send(b'USERS')
        users = self.socket.recv_json()
        self.print_server_response('Users:\n\t%s' % '\n\t'.join(users))

    def server(self, user):
        # this wont work without addr!
        user_list = json.dumps(self.clients).encode()
        self.socket.send_multipart([user, user_list])


@CommandRegistry.register
class Message(Command):
    """PRIVMSG

    Sends another user a private message.

    Usage:
        /privmsg <user> :<message>
    """
    
    # TODO: this would be much better with ZMQStream and on_recv()/on_send()
    def client(self, target, msg):
        me = self.socket.identity.decode()
        print('<%s> %s' % (me, msg))
        while True:
            self.socket.send(b'PRIVMSG ' + target.encode() + b' :' + msg.encode())
            response = self.socket.recv_string()
            print('<%s> %s' % (target, response)) 
            msg = input('<%s> '  % me)

    def server(self, user, target, msg):
        self.socket.send_multipart([target.encode(), msg.encode()])


@CommandRegistry.register
class Help(Command):
    """HELP

    Displays a list of commands or info about a specific command.

    Usage:
        /help <command_name>
    """

    def client(self, command=None):
        if command:
            Help._print_command_help(command)
        else:
            Help._print_command_list()

    @classmethod
    def _print_command_help(cls, command):
        try:
            command = CommandRegistry._commands[command.upper()]
            print(command.get_help())
        except KeyError:
            print("'%s' is not a zchat command\n" % command)
            cls._print_command_list()

    @classmethod
    def _print_command_list(cls):
        print('Command list (/help <command> for more details):')

        for command_name in CommandRegistry.get_list():
            print('\t%s' % command_name)
