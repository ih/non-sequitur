import unittest
import nonsequitur


class TestNonSequiturMethods(unittest.TestCase):
    def test_size(self):
        self.assertEqual(nonsequitur.size([1, [2, 3], 4]), 4)

    def test_substitute(self):
        name = nonsequitur.Symbol('test')
        after_application = nonsequitur.substitute(
            name, '*', ['*', ['*', 2, 3], '*'])
        self.assertEqual(after_application, [name, [name, 2, 3], name])

if __name__ == '__main__':
    unittest.main()
