from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.Connector import Connector
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User


class say_to(Method):

    def gdo_trigger(self) -> str:
        return 'say.to'

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_User('to').not_null(),
            GDT_RestOfText('message').not_null(),
        ]

    def get_target(self) -> GDO_User:
        return self.param_value('to')

    async def gdo_execute(self) -> GDT:
        target = self.get_target()
        message = self.param_value('message')
        await target.get_server().send_to_user(target, '%s', [message])
        return self.empty()
