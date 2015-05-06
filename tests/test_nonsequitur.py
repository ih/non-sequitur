import unittest
import language
import nonsequitur


class TestNonSequiturMethods(unittest.TestCase):
    def test_substitute(self):
        name = language.Symbol('test')
        after_application = nonsequitur.substitute(
            name, '*', ['*', ['*', 2, 3], '*'])
        self.assertEqual(after_application, [name, [name, 2, 3], name])

    # def test_check(self):


if __name__ == '__main__':
    unittest.main()
