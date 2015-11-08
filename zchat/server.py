import sys
import logging

import zmq

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
            user, cmd = self.socket.recv_multipart()
            result = self.handle_command(user, cmd)
            self.socket.send_multipart([user, result])

    def handle_command(self, user, cmd):
        logger.debug("User<%s> sent command: %s" % (user, cmd))
        if cmd == b'REGISTER':
            self.clients.append(user)
            return self.welcome
        else:
            return cmd


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit('Usage: python -m zchat.server <port>')

    logger.info('Starting zchat server...')
    server = ZChatServer(sys.argv[1])
    try:
        server.start()
    except KeyboardInterrupt:
        exit('Closing server.')
