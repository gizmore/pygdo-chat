from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_Text import GDT_Text
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created


class GDO_ChatShout(GDO):
    """Auditable record of a cross-network shout; anonymity is display-only."""

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('shout_id'),
            GDT_User('shout_creator').not_null(),
            GDT_Channel('shout_channel').cascade_delete(),
            GDT_Bool('shout_anonymous').not_null().initial('0'),
            GDT_Text('shout_message').not_null().maxlen(4096),
            GDT_Created('shout_created'),
        ]
