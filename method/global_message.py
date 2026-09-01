from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_RestOfText import GDT_RestOfText


class global_message(Method):
    """Send one owner announcement to every known PyGDO channel."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'global.message'

    @classmethod
    def gdo_trig(cls) -> str:
        return 'gmsg'

    def gdo_user_permission(self) -> str | None:
        return 'owner'

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_RestOfText('message').not_null()]

    async def gdo_execute(self) -> GDT:
        text = self.param_value('message')
        channels = GDO_Channel.table().all()
        for channel in channels:
            server = channel.get_server()
            message = (Message(text, server.get_render_mode()).env_copy(self).
                       env_server(server).env_channel(channel).result(text))
            await server.get_connector().send_to_channel(message)
        return self.reply('msg_global_message_sent', (len(channels),))
