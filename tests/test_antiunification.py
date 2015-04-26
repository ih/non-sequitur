import antiunification
import language
import unittest


class TestAntiunification(unittest.TestCase):
    def test_antiunify(self):
        expression1 = ['+', ['-', 3, 4], 2]
        expression2 = ['+', ['*', 3, 4], 3]
        parameters, abstract_expression = antiunification.antiunify(
            expression1, expression2)
        language.Symbol.reset_counter()
        variable1 = language.make_variable()
        variable2 = language.make_variable()
        correct_abstract_expression = ['+', [variable2, 3, 4], variable1]
        self.assertSetEqual(
            set([variable1, variable2]), set(parameters['variables']))
        self.assertEquals(abstract_expression, correct_abstract_expression)
        self.assertEquals(
            parameters['expression1_bindings'],
            {variable1: 2, variable2: '-'})
        self.assertEquals(
            parameters['expression2_bindings'],
            {variable1: 3, variable2: '*'})

    def test_antiunify_self(self):
        expression = ['+', ['-', 3, 4], 2]
        parameters, abstract_expression = antiunification.antiunify(
            expression, expression)
        self.assertEquals(
            parameters,
            {
                'expression1_bindings': {},
                'variables': [],
                'expression2_bindings': {}
            }
        )
        self.assertEquals(abstract_expression, expression)

    def test_generate_possible_pairs_self(self):
        test_expression = [[1, 2], [1, 2, [4, 5]], [7, 8], [1, 2]]
        possible_pairs = antiunification.generate_possible_pairs(
            test_expression, test_expression)
        correct_possible_pairs = [
            ([1, 2, [4, 5]], [1, 2, [4, 5]]),
            ([1, 2], [1, 2]),
            ([7, 8], [7, 8]),
            ([1, 2], [7, 8])
        ]
        self.assertEqual(possible_pairs, correct_possible_pairs)

    def test_apply_abstract_expression(self):
        test_expression = [[1, 2], [1, 2, [1, 2]], [7, 8], [1, 2]]
        sub_expression = [1, 2]
        variable = language.make_variable()
        variables = [variable]
        bindings = {variable: 2}
        applied_expression = antiunification.apply_abstract_expression(
            test_expression, sub_expression, variables, bindings)
        correct_applied_expression = [
            [['?', 2]], [['?', 2], [['?', 2]]], [7, 8], [['?', 2]]]
        self.assertEqual(applied_expression, correct_applied_expression)
