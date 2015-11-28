import shutil
import textwrap

import zmq

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

context = zmq.Context()


class ZChatClient(CommandRegistry):
    prompt = '>>> '
    resp_prefix = '* '

    def __init__(self):
        super().__init__()
        self.socket = context.socket(zmq.DEALER)
        self._wrapper = textwrap.TextWrapper(replace_whitespace=False,
                                             initial_indent=self.resp_prefix,
                                             subsequent_indent=self.resp_prefix)

    @property
    def _commands(self):
        return self._client_commands

    def run(self):
        print('Please enter a command...')
        while True:
            try:
                self.dispatch(input(self.prompt))
            except InvalidCommand:
                print("Invalid command -- type /help for more info")
            except InvalidArgument:
                print('Invalid arguments to command')

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
