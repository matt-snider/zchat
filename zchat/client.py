import asyncio

import zmq
import zmq.asyncio

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

ctx = zmq.asyncio.Context()
loop = zmq.asyncio.ZMQEventLoop()
asyncio.set_event_loop(loop)


class ZChatClient:

    def __init__(self):
        super().__init__()
        self.socket = ctx.socket(zmq.DEALER)

    @asyncio.coroutine
    def connect(self, host, nick):
        """Connects to the server with the chosen handle/nickname

        Usage:
            /connect <host> <nick>
        """
        self.socket.identity = nick.encode()
        self.socket.connect('tcp://{}'.format(host))
        yield from self.socket.send(b'CONNECT')
        return (yield from self.socket.recv_multipart())

    @asyncio.coroutine
    def users(self):
        """Lists the users on the current server

        Usage:
            /users
        """
        yield from self.socket.send(b'USERS')
        return (yield from self.socket.recv_multipart())

    @asyncio.coroutine
    def message(self, target, msg):
        """Sends another user a private message

        Usage:
            /privmsg <user> :<message>
        """
        msg = b'PRIVMSG ' + target.encode() + b' :' + msg.encode()
        yield from self.socket.send(msg)
        return (yield from self.socket.recv_multipart())


if __name__ == '__main__':
    import urwid
    from .widget import CLI

    client = ZChatClient()
    urwid_loop = urwid.MainLoop(
        CLI(client, loop=loop),
        event_loop=urwid.AsyncioEventLoop(loop=loop),
        palette=[('prompt', 'default,bold', 'default')]
    )

    try:
        urwid_loop.run()
    except KeyboardInterrupt:
        exit('Exiting zchat...')
