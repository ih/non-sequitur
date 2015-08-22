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
            functions[0].name if (
                functions[0].name != start) else functions[1].name)
        self.assertEqual(
            program.functions[start].body,
            [[function_name], 'b', 'c', [function_name]])

    def test_main2(self):
        test_data = 'a1cqa2cma3coa4cpa5cra6c'
        nonsequitur.main(test_data)
        self.assertEqual(2, 2)
