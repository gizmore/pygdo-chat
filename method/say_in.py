from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_RestOfText import GDT_RestOfText


class say_in(Method):

    def gdo_trigger(self) -> str:
        return 'say.in'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Channel('channel').not_null().multiple(),
            GDT_RestOfText('message').not_null(),
        ]

    def get_channels(self) -> list[GDO_Channel]:
        return self.param_value('channel')

    async def execute(self):
        msg_txt = self.param_value('message')
        for channel in self.get_channels():
            await channel.send(msg_txt)
        return self.empty()
    