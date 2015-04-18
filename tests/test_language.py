import language
import unittest


class TestLanguage(unittest.TestCase):
    def setUp(self):
        language.Symbol.reset_counter()

    def test_size(self):
        self.assertEqual(language.size([1, [2, 3], 4]), 4)

    def test_symbol(self):
        language.Symbol('S')
        language.Symbol('S')
        language.Symbol('V')
        self.assertEquals(language.Symbol.prefix_counter['S'], 2)
        self.assertEquals(language.Symbol.prefix_counter['V'], 1)

    def test_function_reset_index(self):
        language.Function()
        language.Function()
        self.assertGreater(len(language.Function.index.keys()), 0)
        language.Function.reset_index()
        self.assertEqual(len(language.Function.index.keys()), 0)
