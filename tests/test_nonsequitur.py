import unittest
import language
import nonsequitur


class TestNonSequiturMethods(unittest.TestCase):
    def test_substitute(self):
        name = language.Symbol('test')
        after_application = nonsequitur.substitute(
            name, '*', ['*', ['*', 2, 3], '*'])
        self.assertEqual(after_application, [name, [name, 2, 3], name])

    def test_main(self):
        test_data = 'abcdbcabcd'
        program = nonsequitur.main(test_data)
        self.assertEqual(str(program), "[start0 [] [['F1'], ['F0'], ['F1']]]")
        self.assertEqual(
            str(language.Function.index[language.Symbol('F', 1)]),
            "[F1 [] ['a', ['F0'], 'd']]")
        self.assertEqual(
            str(language.Function.index[language.Symbol('F', 0)]),
            "[F0 [] ['b', 'c']]")


if __name__ == '__main__':
    unittest.main()
