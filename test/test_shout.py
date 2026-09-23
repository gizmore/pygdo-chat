import unittest
from unittest.mock import Mock, AsyncMock, patch

from gdo.base.Render import Mode
from gdo.base.Application import Application
from gdo.chat.method.shout import shout


class ShoutTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        Application.init_cli()
        Application.STORAGE.lang = 'en'

    def test_price(self):
        method = object.__new__(shout)
        field = shout.gdo_method_config_server()[0]
        self.assertEqual('100', field.get_initial())
        method.get_config_server = Mock(return_value=Mock(get_value=lambda: 137))
        self.assertEqual(137.0, method.gdo_method_price())
        method.get_config_server.assert_called_once_with('price')

    async def test_routes_each_channel_to_its_server(self):
        method = object.__new__(shout)
        method._env_user = Mock(get_id=lambda: 42, get_displayname=lambda: 'Tester')
        method._env_channel = Mock(get_id=lambda: 7)
        method.param_value = Mock(side_effect=lambda key: {'anon': False, 'message': 'hello everyone'}[key])
        method.reply = Mock()
        servers = [Mock(), Mock()]
        channels = [Mock(), Mock()]
        for server, channel in zip(servers, channels):
            channel.get_server.return_value = server
            server.get_render_mode.return_value = Mode.render_txt
            server.get_connector.return_value.send_to_channel = AsyncMock()
        table = Mock()
        table.select.return_value.exec.return_value = channels
        with patch('gdo.chat.method.shout.GDO_Channel.table', return_value=table), \
                patch('gdo.chat.method.shout.GDO_ChatShout.blank') as shout_record, \
                patch('gdo.chat.method.shout.module_chat.instance') as chat, \
                patch('gdo.chat.method.shout.Message') as message_cls:
            chat.return_value.cfg_shout_allow_anon.return_value = False
            chat.return_value.cfg_shout_show_sender.return_value = True
            shout_record.return_value.insert.return_value = Mock()
            messages = [Mock(), Mock()]
            message_cls.side_effect = messages
            for message in messages:
                message.env_copy.return_value = message
                message.env_server.return_value = message
                message.env_channel.return_value = message
                message.result.return_value = message
                message.no_sender_prefix.return_value = message
            await method.gdo_execute()
            for server, channel, message in zip(servers, channels, messages):
                message.env_server.assert_called_once_with(server)
                message.env_channel.assert_called_once_with(channel)
                server.get_connector.return_value.send_to_channel.assert_awaited_once_with(message)
            method.reply.assert_called_once_with('msg_shout_sent', (2,))
            table.select.return_value.where.assert_not_called()
            shout_record.assert_called_once_with({
                'shout_creator': 42,
                'shout_channel': 7,
                'shout_anonymous': '0',
                'shout_message': 'hello everyone',
            })

    async def test_anonymous_shout_requires_module_config(self):
        method = object.__new__(shout)
        method._env_user = Mock(get_id=lambda: 42, get_displayname=lambda: 'Tester')
        method._env_channel = Mock(get_id=lambda: 7)
        method.param_value = Mock(side_effect=lambda key: {'anon': True, 'message': 'private hello'}[key])
        method.err = Mock(return_value='denied')
        with patch('gdo.chat.method.shout.module_chat.instance') as chat:
            chat.return_value.cfg_shout_allow_anon.return_value = False
            self.assertEqual('denied', await method.gdo_execute())
        method.err.assert_called_once_with('err_shout_anon_disabled')

    async def test_anonymous_shout_is_persisted_but_hides_the_display_name(self):
        method = object.__new__(shout)
        method._env_user = Mock(get_id=lambda: 42, get_displayname=lambda: 'Tester')
        method._env_channel = Mock(get_id=lambda: 7)
        method.param_value = Mock(side_effect=lambda key: {'anon': True, 'message': 'private hello'}[key])
        method.reply = Mock(return_value='sent')
        channels = [Mock()]
        server = Mock()
        channels[0].get_server.return_value = server
        server.get_render_mode.return_value = Mode.render_txt
        server.get_connector.return_value.send_to_channel = AsyncMock()
        table = Mock()
        table.select.return_value.exec.return_value = channels
        with patch('gdo.chat.method.shout.module_chat.instance') as chat, \
                patch('gdo.chat.method.shout.GDO_ChatShout.blank') as shout_record, \
                patch('gdo.chat.method.shout.GDO_Channel.table', return_value=table), \
                patch('gdo.chat.method.shout.Message') as message_cls:
            chat.return_value.cfg_shout_allow_anon.return_value = True
            chat.return_value.cfg_shout_show_sender.return_value = True
            shout_record.return_value.insert.return_value = Mock()
            message = message_cls.return_value
            message.env_copy.return_value = message
            message.env_server.return_value = message
            message.env_channel.return_value = message
            message.result.return_value = message
            message.no_sender_prefix.return_value = message
            self.assertEqual('sent', await method.gdo_execute())
        shout_record.assert_called_once_with({
            'shout_creator': 42,
            'shout_channel': 7,
            'shout_anonymous': '1',
            'shout_message': 'private hello',
        })
        message_cls.assert_called_once_with('Someone shouts: private hello', Mode.render_txt)
