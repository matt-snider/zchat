import sys
import zmq

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

context = zmq.Context()


class ZChatClient:

    def __init__(self):
        self.socket = context.socket(zmq.DEALER)
        self.registry = CommandRegistry(self, is_client=True)

    def run(self):
        print('Please enter a command...')
        while True:
            try:
                self.registry.dispatch(input())
            except InvalidCommand:
                print("Invalid command -- type /help for more info")
            except InvalidArgument:
                print('Invalid arguments to command')


if __name__ == '__main__':
    client = ZChatClient()
    try:
        client.run()
    except KeyboardInterrupt:
        exit('Exiting zchat...')
