import os

from gdo.chat.method.say_in import say_in
from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdotest.TestUtil import GDOTestCase


class test_chat(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    def test_target(self):
        pass

    def test_say_in_accepts_rest_of_text(self):
        Application.mode(Mode.render_cli)
        channel, message = say_in().gdo_parameters()
        self.assertFalse(channel.is_multiple())
        self.assertIsInstance(message, GDT_RestOfText)
