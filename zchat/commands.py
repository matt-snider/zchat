import json
from abc import ABC, abstractmethod


class CommandRegistry:
    _commands = {}

    def __init__(self, owner, is_client=False):
        self._client = is_client
        self._owner = owner

    @classmethod
    def register(cls, cmd):
        cls._commands[cmd.get_name()] = cmd

    def dispatch(self, cmd_string, user=None):
        cmd_string, *trailing_arg = cmd_string.split(' :')
        cmd_name, *args = cmd_string.split()
        args.extend(trailing_arg)
        try:
            command = self._commands[cmd_name.upper()]
            if self._client:
                return command.execute_client(self._owner, *args)
            else:
                return command.execute_server(self._owner, user, *args)
        except TypeError:
            raise InvalidArgument(*args)
        except KeyError:
            raise InvalidCommand(cmd_name)


class InvalidCommand(Exception):
    pass


class InvalidArgument(Exception):
    pass


class Command(ABC):

    @classmethod
    def get_help(self):
        return self.__doc__

    @classmethod
    def get_name(self):
        return self.get_help().split('\n', 1)[0].strip()

    @abstractmethod
    def execute_server(cls, server, user, *args):
        pass

    @abstractmethod
    def execute_client(cls, client, *args):
        pass


@CommandRegistry.register
class Connect(Command):
    """CONNECT

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
        client.print_server_response(welcome)

    @classmethod
    def execute_server(cls, server, user):
        print('%s connected' % user)
        server.socket.send_multipart([user, server.welcome])
        server.clients.append(user.decode())


@CommandRegistry.register
class Users(Command):
    """USERS

    Lists the users on the current server
    
    Usage:
        /users 
    """

    @classmethod
    def execute_client(cls, client):
        client.socket.send(b'USERS')
        users = client.socket.recv_json()
        client.print_server_response('Users:\n\t%s' % '\n\t'.join(users))

    @classmethod
    def execute_server(cls, server, user):
        # this wqont work without addr!
        user_list = json.dumps(server.clients).encode()
        server.socket.send_multipart([user, user_list])


@CommandRegistry.register
class Message(Command):
    """PRIVMSG

    Sends another user a private message.

    Usage:
        /privmsg <user> :<message>
    """
    
    # TODO: this would be much better with ZMQStream and on_recv()/on_send()
    @classmethod
    def execute_client(cls, client, target, msg):
        me = client.socket.identity.decode()
        print('<%s> %s' % (me, msg))
        while True:
            client.socket.send(b'PRIVMSG ' + target.encode() + b' :' + msg.encode())
            response = client.socket.recv_string()
            print('<%s> %s' % (target, response)) 
            msg = input('<%s> '  % me)

    @classmethod
    def execute_server(cls, server, user, target, msg):
        server.socket.send_multipart([target.encode(), msg.encode()])

