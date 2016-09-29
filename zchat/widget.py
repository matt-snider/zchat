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
        super().__init__(body)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key != 'enter':
            return key
        cmd = self.focus[0].edit_text
        if not cmd:
            raise urwid.ExitMainLoop()

        self.body.insert(self.focus_position + 1, prompt())
        f = asyncio.ensure_future(self.zchat_client.run_command(cmd))
        f.add_done_callback(self.on_message)

    def on_message(self, f):
        msg = f.result()
        self.focus.contents[1:] = [(response(msg), self.focus.options())]
        self.focus_position += 1

