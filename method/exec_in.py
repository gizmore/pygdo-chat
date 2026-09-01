from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_RestOfText import GDT_RestOfText


class exec_in(Method):
    """Execute a Dog command in a target channel and deliver its result there."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'chat.exec.in'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Channel('channel').not_null(),
            GDT_RestOfText('command').not_null(),
        ]

    async def gdo_execute(self) -> GDT:
        channel = self.param_value('channel')
        command = self.param_value('command')
        server = channel.get_server()
        announcement = (Message(f'{self._env_user.get_displayname()}: {command}', server.get_render_mode()).
                        env_copy(self).
                        env_server(server).
                        env_channel(channel).
                        result(f'{self._env_user.get_displayname()}: {command}'))
        await server.get_connector().send_to_channel(announcement)
        message = (Message(command, channel.get_server().get_render_mode()).
                   env_copy(self).
                   env_server(server).
                   env_channel(channel))
        await message.execute()
        return self.empty()
