from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User


class exec_to(Method):
    """Execute a Dog command as one user and deliver it through that user's connector."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'chat.exec.to'

    def gdo_user_permission(self) -> str:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User('user').not_null(),
            GDT_RestOfText('command').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        user = self.param_value('user')
        command = self.param_value('command')
        server = user.get_server()
        announcement = (Message(f'{self._env_user.get_displayname()}: {command}', server.get_render_mode()).
                        env_copy(self).
                        env_server(server).
                        env_channel(None).
                        env_user(user, True).
                        result(f'{self._env_user.get_displayname()}: {command}'))
        await server.get_connector().send_to_user(announcement)
        await (Message(command, user.get_server().get_render_mode()).
               env_copy(self).
               env_server(server).
               env_channel(None).
               env_user(user, True).
               execute())
        return self.empty()
