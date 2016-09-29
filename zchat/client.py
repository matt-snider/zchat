import asyncio
import shutil
import textwrap

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
        self._wrapper = textwrap.TextWrapper(replace_whitespace=False,
                                             initial_indent=self.resp_prefix,
                                             subsequent_indent=self.resp_prefix)

    @asyncio.coroutine
    def run(self):
        print('Please enter a command...')
        while True:
            try:
                user_input = input(self.prompt)
                if not user_input:
                    continue
                self.dispatch(user_input)
            except InvalidCommand:
                print("Invalid command -- type /help for more info")
            except InvalidArgument:
                print('Invalid arguments to command')

    @asyncio.coroutine
    def receive(self):
        while True:
            cmd_name, *message = yield from self.socket.recv_multipart()
            command = self._commands[cmd_name.decode().upper()]
            command.on_message(self, [arg.decode() for arg in message])

    def execute_command(self, command, *args):
        return command.client(self, *args)

    def on_message(self, message):
        cmd_name, *message = message
        command = self._commands[cmd_name.decode().upper()]
        command.on_message(self, [arg.decode() for arg in message])

    def print_server_response(self, response):
        print('\n')
        width, _ = shutil.get_terminal_size()
        self._wrapper.width = width - len(self.resp_prefix)
        for line in response.splitlines():
            if not line:
                print(self.resp_prefix)
            else:
                print(self._wrapper.fill(line))
        print(self.prompt)


if __name__ == '__main__':
    client = ZChatClient()
    try:
        input('hi')
        loop.run_until_complete(asyncio.gather(client.run(), client.receive()))
    except KeyboardInterrupt:
        exit('Exiting zchat...')
