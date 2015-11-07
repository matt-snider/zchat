import sys
import zmq


def run_chat_server(port):
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind('tcp://*:%s' % port)

    try:
        while True:
            user, cmd = socket.recv_multipart()
            handle_command(user, cmd)
    except KeyboardInterrupt:
        exit('Closing server.')


def handle_command(user, cmd):
    print("User '%s' sent command '%s'" % (user, cmd))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit('Usage: python -m zchat.server <port>')

    run_chat_server(sys.argv[1])