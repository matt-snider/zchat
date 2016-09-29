import asyncio

import zmq
import zmq.asyncio

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

ctx = zmq.asyncio.Context()
loop = zmq.asyncio.ZMQEventLoop()
asyncio.set_event_loop(loop)


class ZChatClient(CommandRegistry):
    prompt = '>>> '
    resp_prefix = '* '

    def __init__(self):
        super().__init__()
        self.socket = ctx.socket(zmq.DEALER)

    @asyncio.coroutine
    def run_command(self, command):
        try:
            self.dispatch(command)
            cmd_name, *message = yield from self.socket.recv_multipart()
            command = self._commands[cmd_name.decode().upper()]
            return command.on_message(self, [arg.decode() for arg in message])
        except InvalidCommand:
            return "Invalid command -- type /help for more info"
        except InvalidArgument:
            return 'Invalid arguments to command'

    def execute_command(self, command, *args):
        return command.client(self, *args)


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
