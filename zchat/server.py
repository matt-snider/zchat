import sys
import logging

import zmq

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

context = zmq.Context()


class ZChatServer(CommandRegistry):

    welcome = (b'Welcome to zchat server!\n\n'
               b'This is a welcome message that needs to be updated with '
               b'something more interesting. Hello world! Foo bar biz '
               b'baz bam!')

    def __init__(self, port):
        super().__init__()
        self.socket = context.socket(zmq.ROUTER)
        self.port = port
        self.clients = set()

    def start(self):
        self.socket.bind('tcp://*:{}'.format(self.port))
        logger.info('Server started on port %s', self.port)
        while True:
            user, cmd = self.socket.recv_multipart()
            try:
                self.dispatch(cmd.decode(), user)
                logger.debug('Server handled Client<%s> command: %s' % (user, cmd))
            except (InvalidCommand, InvalidArgument):
                logger.debug('Client<%s> sent invalid command: %s' % (user, cmd))

    def execute_command(self, command, *args):
        return command.server(self, *args)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit('Usage: python -m zchat.server <port>')

    logger.info('Starting zchat server...')
    server = ZChatServer(sys.argv[1])
    try:
        server.start()
    except KeyboardInterrupt:
        exit('Closing server.')
