import unittest
import language
import nonsequitur


class TestNonSequiturMethods(unittest.TestCase):
    def setUp(self):
        language.Symbol.reset_counter()

    def test_substitute(self):
        name = language.Symbol('test')
        after_application = nonsequitur.substitute(
            name, '*', ['*', ['*', 2, 3], '*'])
        self.assertEqual(after_application, [name, [name, 2, 3], name])

    def test_main(self):
        test_data = 'abcdbcabcd'
        program = nonsequitur.main(test_data)
        functions = program.functions.values()
        self.assertEqual(len(functions), 2)
        start = language.Symbol('start', 0)
        function_name = (
            functions[0].name if functions[0].name != start else function[1].name)
        self.assertEqual(
            program.functions[start].body, [[function_name], 'b', 'c', [function_name]])

        # self.assertEqual(
        #     str(program), "[start0 [] [['F1'], ['F0'], ['F1']]] 0")
        # self.assertEqual(
        #     str(language.Function.index[language.Symbol('F', 1)]),
        #     "[F1 [] ['a', ['F0'], 'd']] 2")
        # self.assertEqual(
        #     str(language.Function.index[language.Symbol('F', 0)]),
        #     "[F0 [] ['b', 'c']] 2")


if __name__ == '__main__':
    unittest.main()
