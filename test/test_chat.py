import os
from unittest.mock import AsyncMock, patch

from gdo.base.Message import Message
from gdo.chat.method.say_in import say_in
from gdo.chat.method.exec_in import exec_in
from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.connector.Bash import Bash
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdotest.TestUtil import GDOTestCase


class test_chat(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    def test_target(self):
        pass

    def test_say_in_accepts_rest_of_text(self):
        Application.mode(Mode.render_cli)
        channel, message = say_in().gdo_parameters()
        self.assertFalse(channel.is_multiple())
        self.assertIsInstance(message, GDT_RestOfText)

    async def test_exec_in_uses_target_channel_context(self):
        user = await Bash.get_server().get_or_create_user('chat_exec')
        channel = Bash.get_server().get_or_create_channel('chat_exec_target')
        method = exec_in().env_user(user, True).env_server(Bash.get_server()).env_channel(None)
        method.input('channel', str(channel.get_id())).input('command', '$ping')
        with (patch.object(channel.get_server().get_connector(), 'send_to_channel', new=AsyncMock()) as send,
              patch.object(Message, 'execute', new=AsyncMock()) as execute):
            await method.gdo_execute()
        send.assert_awaited_once()
        announced = send.await_args.args[0]
        self.assertEqual(f'{user.get_displayname()}: $ping', announced._result)
        self.assertIs(user, announced._env_user)
        self.assertIs(channel, announced._env_channel)
        execute.assert_awaited_once()
        executed = Message.CURRENT
        self.assertEqual('$ping', executed._message)
        self.assertIs(channel, executed._env_channel)
        self.assertIs(channel.get_server(), executed._env_server)
        self.assertIs(user, executed._env_user)
