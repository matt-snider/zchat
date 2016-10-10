import asyncio
import urwid


def prompt():
    return urwid.Pile([urwid.Edit(('prompt', '>>> '))])


def response(text):
    return urwid.Text(('prompt', text + '\n'))


class CLI(urwid.ListBox):

    def __init__(self, zchat_client, loop):
        self.zchat_client = zchat_client
        self.loop = loop
        body = urwid.SimpleFocusListWalker([prompt()])
        self.commands = {
            'help': self.help,
            'connect': self.zchat_client.connect,
            'privmsg': self.zchat_client.message,
            'users': self.zchat_client.users,
        }
        super().__init__(body)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key != 'enter':
            return key
        cmd = self.focus[0].edit_text
        if not cmd:
            raise urwid.ExitMainLoop()

        self.body.insert(self.focus_position + 1, prompt())
        f = asyncio.ensure_future(self.execute_command(cmd))
        f.add_done_callback(self.on_message)

    def print(self, msg, increment=True):
        self.focus.contents[1:] = [(response(msg), self.focus.options())]
        if increment:
            self.focus_position += 1

    def on_message(self, f):
        result = f.result()
        if result:
            msg = ''.join(x.decode() for x in result)
            self.print(msg)

    @asyncio.coroutine
    def execute_command(self, cmd):
        cmd_name, *args = cmd.split()
        try:
            return (yield from self.commands[cmd_name.lower()](*args))
        except KeyError:
            self.print('Invalid command. Type /help for a list of commands')

    @asyncio.coroutine
    def help(self, cmd=None):
        """Lists available commands or displays help about specific commands

        Usage:
            /help [<cmd>]
        """
        if cmd:
            try:
                self.print(self.commands[cmd].__doc__)
            except KeyError:
                self.print('Invalid command')
        else:
            message = 'Available commands:\n'
            for cmd_name, cmd in self.commands.items():
                message += '\n  {} - {}'.format(cmd_name.upper(),
                                                cmd.__doc__.splitlines()[0])
            self.print(message)
