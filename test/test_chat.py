import os
from unittest.mock import AsyncMock, MagicMock, patch

from gdo.base.Message import Message
from gdo.chat.method.say_in import say_in
from gdo.chat.method.say_to import say_to
from gdo.chat.method.exec_in import exec_in
from gdo.chat.method.exec_to import exec_to
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
        channel, prefix, message = say_in().gdo_parameters()
        self.assertFalse(channel.is_multiple())
        self.assertEqual('1', prefix.get_initial())
        self.assertIsInstance(message, GDT_RestOfText)

    def test_say_methods_need_admin(self):
        self.assertEqual('admin', say_in().gdo_user_permission())
        self.assertEqual('admin', say_to().gdo_user_permission())

    def test_say_methods_allow_explicit_prefix_control(self):
        for method_type in (say_in, say_to):
            method = method_type()
            self.assertTrue(method.param_value('prefix'))
            method.input('prefix', '0')
            method.parameters(reset=True)
            self.assertFalse(method.param_value('prefix'))

    def test_message_can_suppress_connector_sender_prefix(self):
        message = Message('raw command', Mode.render_cli).no_sender_prefix()
        self.assertTrue(message._no_sender_prefix)

    def test_message_renders_top_bar_with_a_connector_specific_result(self):
        page = MagicMock()
        page._top_bar.render.side_effect = lambda mode: f'top-{mode.name}'
        result = MagicMock()
        result.render.side_effect = lambda mode: f'body-{mode.name}'
        message = Message('command', Mode.render_cli).result_gdt(result)
        with patch.object(Application, 'get_page', return_value=page):
            self.assertEqual(
                'top-render_irc body-render_irc',
                message.render_response(Mode.render_irc),
            )

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

    async def test_exec_to_uses_target_user_connector_context(self):
        requester = await Bash.get_server().get_or_create_user('chat_exec_requester')
        target = await Bash.get_server().get_or_create_user('chat_exec_target_user')
        method = exec_to().env_user(requester, True).env_server(Bash.get_server()).env_channel(None)
        method.input('user', str(target.get_id())).input('command', '$ping')
        with (patch.object(target.get_server().get_connector(), 'send_to_user', new=AsyncMock()) as send,
              patch.object(Message, 'execute', new=AsyncMock()) as execute):
            await method.gdo_execute()
        send.assert_awaited_once()
        announced = send.await_args.args[0]
        self.assertEqual(f'{requester.get_displayname()}: $ping', announced._result)
        self.assertIs(target, announced._env_user)
        execute.assert_awaited_once()
        executed = Message.CURRENT
        self.assertEqual('$ping', executed._message)
        self.assertIsNone(executed._env_channel)
        self.assertIs(target.get_server(), executed._env_server)
        self.assertIs(target, executed._env_user)
