import sys
import zmq

commands = set()

def run_chat_client(user, hostname, port):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.identity = user.encode()

    # Connect to the server, register, and print
    # the welcome message response
    socket.connect('tcp://{}:{}'.format(hostname, port))
    socket.send(b'REGISTER')
    welcome = socket.recv_string()
    print(welcome)

    print('Please enter a command...')
    try:
        while True:
            cmd = parse_and_validate_command(input())
            if not cmd:
                continue
            socket.send(cmd.encode())
            response = socket.recv_multipart()
            print('Response: %s' % response)

    except KeyboardInterrupt:
        exit('Exiting zchat...')


def parse_and_validate_command(cmd):
    if not cmd.startswith('/'):
        print("Prefix commands with '/' -- type /help for more info")
        return

    cmd = cmd.strip('/')
    if cmd not in commands:
        print("Invalid command: '%s' -- type /help for a list of commands" % cmd)
        return
    return cmd

if __name__ == '__main__':
    if len(sys.argv) != 4:
        exit('Usage: python -m zchat.client <user> <hostname> <port>')

    user, hostname, port = sys.argv[1:]
    run_chat_client(user, hostname, port)
