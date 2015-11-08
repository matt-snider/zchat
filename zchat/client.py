import sys
import zmq

from zchat.commands import CommandRegistry

context = zmq.Context()


class ZChatClient:

    def __init__(self):
        self.socket = context.socket(zmq.DEALER)
        self.registry = CommandRegistry('client', self.socket)

    def run(self):
        print('Please enter a command...')
        while True:
            try:
                self.registry.dispatch(input())
            except:
                print("Invalid command -- type /help for more info")


if __name__ == '__main__':
    client = ZChatClient()
    try:
        client.run()
    except KeyboardInterrupt:
        exit('Exiting zchat...')
