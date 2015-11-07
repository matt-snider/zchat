import sys
import zmq


def run_chat_client(user, hostname, port):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.identity = user.encode()
    socket.connect('tcp://{}:{}'.format(hostname, port))

    print('Please enter a command...')
    try:
        while True:
            cmd = input()
            # parse and validate
            socket.send(cmd.encode())
            response = socket.recv_multipart()
            print('Response: %s' % response)

    except KeyboardInterrupt:
        exit('Exiting zchat...')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        exit('Usage: python -m zchat.client <user> <hostname> <port>')

    user, hostname, port = sys.argv[1:]
    run_chat_client(user, hostname, port)
