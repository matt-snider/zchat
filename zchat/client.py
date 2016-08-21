import asyncio
import os
import sys
import shutil
import textwrap

from asyncio.streams import StreamWriter, FlowControlMixin

import zmq
import zmq.asyncio

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

ctx = zmq.asyncio.Context()
loop = zmq.asyncio.ZMQEventLoop()
asyncio.set_event_loop(loop)


reader, writer = None, None

@asyncio.coroutine
def stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)

    writer_transport, writer_protocol = yield from loop.connect_write_pipe(FlowControlMixin, os.fdopen(0, 'wb'))
    writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    yield from loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return reader, writer

@asyncio.coroutine
def async_input(message):
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = yield from stdio()

    writer.write(message)
    yield from writer.drain()

    line = yield from reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')


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
                user_input = yield from async_input('>>> ')
                if not user_input:
                    continue
                self.dispatch(user_input)
            except InvalidCommand:
                print("Invalid command -- type /help for more info")
            except InvalidArgument:
                print('Invalid arguments to command')

    @asyncio.coroutine
    def async_input(self):
        input = yield from self._stdin.read_until(delimiter=b'\n')
        return input.strip().decode()

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
        writer.write(b'\r')
        width, _ = shutil.get_terminal_size()
        self._wrapper.width = width - len(self.resp_prefix)
        for line in response.splitlines():
            if not line:
                writer.write(self.resp_prefix.encode())
            else:
                writer.write(self._wrapper.fill(line).encode())
        writer.write(self.prompt.encode())


if __name__ == '__main__':
    client = ZChatClient()
    try:
        loop.run_until_complete(asyncio.gather(client.run(), client.receive()))
    except KeyboardInterrupt:
        exit('Exiting zchat...')
