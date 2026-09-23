from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_UInt import GDT_UInt
from gdo.chat.GDO_ChatShout import GDO_ChatShout
from gdo.chat.module_chat import module_chat


class shout(Method):
    """Broadcast to all servers' channels; the origin server sets the credit price."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'shout'

    @classmethod
    def gdo_method_config_server(cls) -> list[GDT]:
        return [GDT_UInt('price').min(0).max(100000000).not_null().initial('100')]

    def gdo_method_price(self) -> float:
        return float(self.get_config_server('price').get_value())

    def gdo_needs_authentication(self) -> bool:
        return True

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Bool('anon').not_null().initial('0'),
            GDT_RestOfText('message').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        anonymous = self.param_value('anon')
        chat = module_chat.instance()
        if anonymous and not chat.cfg_shout_allow_anon():
            return self.err('err_shout_anon_disabled')
        message = self.param_value('message')
        GDO_ChatShout.blank({
            'shout_creator': self._env_user.get_id(),
            'shout_channel': self._env_channel.get_id() if self._env_channel else None,
            'shout_anonymous': str(int(anonymous)),
            'shout_message': message,
        }).insert()
        sender = self._env_user.get_displayname() if chat.cfg_shout_show_sender() and not anonymous else 'Someone'
        text = f'{sender} shouts: {message}'
        channels = GDO_Channel.table().select().exec()
        count = 0
        for channel in channels:
            server = channel.get_server()
            message = (Message(text, server.get_render_mode()).env_copy(self)
                       .env_server(server).env_channel(channel).result(text).no_sender_prefix())
            await server.get_connector().send_to_channel(message)
            count += 1
        return self.reply('msg_shout_sent', (count,))
