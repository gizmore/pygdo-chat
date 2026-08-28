from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_RestOfText import GDT_RestOfText


class say_in(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'say.in'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Channel('channel').not_null(),
            GDT_Bool('prefix').not_null().initial('1'),
            GDT_RestOfText('message').not_null(),
        ]

    def get_channels(self) -> list[GDO_Channel]:
        return [self.param_value('channel')]

    async def gdo_execute(self) -> GDT:
        msg_txt = self.param_value('message')
        with_prefix = self.param_value('prefix')
        if with_prefix:
            sender = self._env_user.get_displayname().capitalize()
            msg_txt = f'{sender} says: {msg_txt}'
        for channel in self.get_channels():
            server = channel.get_server()
            message = (Message(msg_txt, server.get_render_mode()).env_copy(self).
                       env_server(server).env_channel(channel).result(msg_txt))
            if not with_prefix:
                message.no_sender_prefix()
            await server.get_connector().send_to_channel(message)
        return self.empty()
    
