import language
import unittest
import utility


class TestLanguage(unittest.TestCase):
    def setUp(self):
        language.Symbol.reset_counter()

    def test_size(self):
        self.assertEqual(language.expression_size([1, [2, 3], 4]), 4)

    def test_symbol(self):
        language.Symbol('S')
        language.Symbol('S')
        language.Symbol('V')
        self.assertEquals(language.Symbol.prefix_counter['S'], 2)
        self.assertEquals(language.Symbol.prefix_counter['V'], 1)

    def test_symbol_equality(self):
        s0 = language.Symbol('S')
        also_s0 = language.Symbol('S', 0)
        self.assertEqual(s0, also_s0)
        self.assertFalse(s0 != also_s0)

    def test_program_size(self):
        function1 = language.Function(
            parameters=[],
            body=[[1, 2, 3], [3, 4, 5, 5, 7, 8, 9]])
        function2 = language.Function(
            parameters=[language.Symbol('V'), language.Symbol('V')],
            body=[[1, 2, 3]])
        program = language.Program()
        program.add_new_function(function1)
        program.add_new_function(function2)
        self.assertEqual(program.size(), 17)

    def test_longest_term_length(self):
        test_expression = [[1, 2, 3], 5, [7, [3, 4, 5, 6, 7, 8], 8], 10]
        self.assertEquals(language.longest_term_length(test_expression), 6)

    def test_generate_subexpressions(self):
        test_expression = [[1, 2, 3], 5, [7, 8, 9, 10]]
        subexpressions = language.generate_subexpressions(test_expression, 2)
        correct_subexpressions = [
            [[1, 2, 3], 5],
            [5, [7, 8, 9, 10]],
            [1, 2],
            [2, 3],
            [7, 8],
            [8, 9],
            [9, 10],
            [[1, 2, 3], 5, [7, 8, 9, 10]],
            [1, 2, 3],
            [7, 8, 9],
            [8, 9, 10],
            [7, 8, 9, 10]
        ]
        self.assertSetEqual(
            set(utility.list2tuple(subexpressions)),
            set(utility.list2tuple(correct_subexpressions)))

    def test_generate_subexpressions_duplication(self):
        test_expression = [1, 1, 1, 1]
        subexpressions = language.generate_subexpressions(test_expression, 3)
        correct_subexpressions = [[1, 1, 1], [1, 1, 1, 1]]
        self.assertEqual(
            len(subexpressions), len(set(utility.list2tuple(subexpressions))))
        self.assertSetEqual(
            set(utility.list2tuple(subexpressions)),
            set(utility.list2tuple(correct_subexpressions)))

    def test_get_functions_used(self):
        function1 = language.Function()
        function2 = language.Function()
        test_expression = [
            [function1.name, 3, 4], [function1.name, [2, [function2.name]]]]
        self.assertEqual(
            language.get_functions_used(test_expression),
            {
                function1.name: 2,
                function2.name: 1
            })

    def test_evaluation_single_function(self):
        parameter1 = language.make_variable()
        parameter2 = language.make_variable()
        function = language.Function(
            parameters=[parameter1, parameter2],
            body=[1, 2, parameter1, parameter2, 3])
        expression = [1, 2, [function.name, 5, 6]]
        program = language.Program()
        program.add_new_function(function)
        self.assertEqual(
            language.evaluate(expression, program, {}), [1, 2, 1, 2, 5, 6, 3])

    def test_evaluation_multiple_functions(self):
        parameter1 = language.make_variable()
        parameter2 = language.make_variable()
        function = language.Function(
            parameters=[parameter1, parameter2],
            body=[1, 2, parameter1, parameter2, 3])
        function2 = language.Function(
            parameters=[parameter1],
            body=[[[function.name, 10, parameter1]],  3])
        expression = [1, 2, [function2.name, 5]]
        program = language.Program()
        program.add_new_function(function)
        program.add_new_function(function2)
        self.assertEqual(
            language.evaluate(
                expression, program, {}), [1, 2, [1, 2, 10, 5, 3], 3])
