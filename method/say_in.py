from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_RestOfText import GDT_RestOfText


class say_in(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'say.in'

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

    async def execute(self):
        msg_txt = self.param_value('message')
        if self.param_value('prefix'):
            sender = self._env_user.get_displayname().capitalize()
            msg_txt = f'{sender} says: {msg_txt}'
        for channel in self.get_channels():
            await channel.send(msg_txt)
        return self.empty()
    
