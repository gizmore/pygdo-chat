import unittest

from gdo.chat.method.global_message import global_message


class GlobalMessageVisibilityTest(unittest.TestCase):
    def test_short_trigger_and_hidden(self):
        self.assertEqual('gmsg', global_message.gdo_trig())
        self.assertEqual('global.message', global_message.gdo_trigger())
        self.assertTrue(global_message.gdo_method_hidden(object.__new__(global_message)))
