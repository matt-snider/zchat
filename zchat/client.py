import shutil
import textwrap

import zmq
from zmq.eventloop import zmqstream

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

context = zmq.Context()


class ZChatClient(CommandRegistry):
    prompt = '>>> '
    resp_prefix = '* '

    def __init__(self):
        super().__init__()
        self.socket = context.socket(zmq.DEALER)
        self.stream = zmqstream.ZMQStream(self.socket)
        self.stream.on_recv(self.on_message)
        self._wrapper = textwrap.TextWrapper(replace_whitespace=False,
                                             initial_indent=self.resp_prefix,
                                             subsequent_indent=self.resp_prefix)

    def run(self):
        print('Please enter a command...')
        while True:
            try:
                self.dispatch(input(self.prompt))
            except InvalidCommand:
                print("Invalid command -- type /help for more info")
            except InvalidArgument:
                print('Invalid arguments to command')

    def execute_command(self, command, *args):
        return command.client(self, *args)

    def on_message(self, message):
        cmd_name, message = message
        command = self._commands[cmd_name]
        command.on_message(self, message)

    def print_server_response(self, response):
        width, _ = shutil.get_terminal_size()
        self._wrapper.width = width - len(self.resp_prefix)
        for line in response.splitlines():
            if not line:
                print(self.resp_prefix)
            else:
                print(self._wrapper.fill(line))


if __name__ == '__main__':
    client = ZChatClient()
    try:
        client.run()
    except KeyboardInterrupt:
        exit('Exiting zchat...')
