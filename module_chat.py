from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Bool import GDT_Bool
from gdo.chat.GDO_ChatShout import GDO_ChatShout


class module_chat(GDO_Module):
    def gdo_classes(self) -> list[type[GDO]]:
        return [GDO_ChatShout]

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('shout_show_sender').not_null().initial('1'),
            GDT_Bool('shout_allow_anon').not_null().initial('0'),
        ]

    def cfg_shout_show_sender(self) -> bool:
        return self.get_config_value('shout_show_sender')

    def cfg_shout_allow_anon(self) -> bool:
        return self.get_config_value('shout_allow_anon')
