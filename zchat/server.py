import sys
import logging

import zmq

from zchat.commands import CommandRegistry, InvalidCommand, InvalidArgument

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

context = zmq.Context()


class ZChatServer:

    welcome = b"""Welcome to zchat server!

    This is a welcome message that needs to be updated with something
    more interesting. Hello world! Foo bar biz baz bam!
    """

    def __init__(self, port):
        self.socket = context.socket(zmq.ROUTER)
        self.port = port
        self.registry = CommandRegistry('server', self.socket)

    def start(self):
        self.socket.bind('tcp://*:{}'.format(self.port))
        logger.info('Server started on port %s', self.port)
        while True:
            try:
                user, cmd = self.socket.recv_multipart()
                self.registry.dispatch(cmd.decode())
            except (InvalidCommand, InvalidArgument):
                logger.debug('Client<%s> sent invalid command: %s' % (user, cmd))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit('Usage: python -m zchat.server <port>')

    logger.info('Starting zchat server...')
    server = ZChatServer(sys.argv[1])
    try:
        server.start()
    except KeyboardInterrupt:
        exit('Closing server.')
