import sys
import logging

import zmq


logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run_chat_server(port):
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind('tcp://*:%s' % port)
    logger.info('Server started on port %s', port)

    try:
        while True:
            user, cmd = socket.recv_multipart()
            result = handle_command(user, cmd)
            socket.send_multipart([user, result])
    except KeyboardInterrupt:
        exit('Closing server.')


def handle_command(user, cmd):
    logger.debug("User<%s> sent command: %s" % (user, cmd))
    return cmd

if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit('Usage: python -m zchat.server <port>')

    logger.info('Starting zchat server...')
    run_chat_server(sys.argv[1])
