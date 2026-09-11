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
        method._env_user = Mock(get_displayname=lambda: 'Tester')
        method.param_value = Mock(return_value='hello everyone')
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
                patch('gdo.chat.method.shout.Message') as message_cls:
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
