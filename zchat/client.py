import sys
import zmq

context = zmq.Context()


class ZChatClient:

    def __init__(self, user, hostname, port):
        self.url = 'tcp://{}:{}'.format(hostname, port)
        self.socket = context.socket(zmq.DEALER)
        self.socket.identity = user.encode()
        self.commands = set()

    def run(self):
        self.socket.connect(self.url)
        self.socket.send(b'REGISTER')
        welcome = self.socket.recv_string()
        print(welcome)

        print('Please enter a command...')
        try:
            while True:
                cmd = self.parse_and_validate_command(input())
                if not cmd:
                    continue
                self.socket.send(cmd.encode())
                response = self.socket.recv_multipart()
                print('Response: %s' % response)

        except KeyboardInterrupt:
            exit('Exiting zchat...')

    def parse_and_validate_command(self, cmd):
        if not cmd.startswith('/'):
            print("Prefix commands with '/' -- type /help for more info")
            return

        cmd = cmd.strip('/')
        if cmd not in self.commands:
            print("Invalid command: '%s' -- type /help for a list of commands" % cmd)
            return
        return cmd


if __name__ == '__main__':
    if len(sys.argv) != 4:
        exit('Usage: python -m zchat.client <user> <hostname> <port>')

    user, hostname, port = sys.argv[1:]
    client = ZChatClient(user, hostname, port)
    client.run()
