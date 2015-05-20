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
        applied_expression, count = (antiunification.apply_abstract_expression(
            test_expression, sub_expression, variables, bindings))
        correct_applied_expression = [
            [['?', 2]], [['?', 2], [['?', 2]]], [7, 8], [['?', 2]]]
        self.assertEqual(
            (applied_expression, count), (correct_applied_expression, 4))

    def test_apply_abstract_expression2(self):
        test_expression = [
            [1, 2], [1, 2, [1, 2]], [7, 8, 9], [7, 8, 9], [1, 2]]
        sub_expression = [7, 8, 9]
        variable1 = language.make_variable()
        variable2 = language.make_variable()
        variable3 = language.make_variable()
        variables = [variable1, variable2, variable3]
        bindings = {
            variable1: 7,
            variable2: 8,
            variable3: 9
        }
        applied_expression, count = antiunification.apply_abstract_expression(
            test_expression, sub_expression, variables, bindings)
        correct_applied_expression = [
            [1, 2], [1, 2, [1, 2]], [['?', 7, 8, 9]], [['?', 7, 8, 9]], [1, 2]]
        self.assertEqual(
            (applied_expression, count), (correct_applied_expression, 2))

    def test_find_best_self(self):
        test_function = language.Function(
            parameters=[],
            body=[[1, 2], [1, 2, [1, 2]], [7, 8, 9], [7, 8, 9], [1, 2]])
        alternative_function = language.Function(
            parameters=[],
            body=['-', ['+', 2, 3, 4], 3])
        best = antiunification.find_best(
            test_function, [test_function, alternative_function])
        true_best = {
            'new_parameters': {
                'expression1_bindings': {},
                'expression2_bindings': {},
                'variables': []
            },
            'new_body': [1, 2],
            'applied_in_target': {
                'name': test_function.name,
                'body': [
                    [['?']], [['?'], [['?']]], [7, 8, 9], [7, 8, 9], [['?']]]},
            'applied_in_other': {
                'name': test_function.name,
                'body': [
                    [['?']], [['?'], [['?']]], [7, 8, 9], [7, 8, 9], [['?']]]},
            'application_count': 8,
            'size_difference': 2
        }
        self.assertEqual(best, true_best)

    def test_find_best(self):
        test_function = language.Function(
            parameters=[],
            body=[[1, 2, 3], [3, 4, 5, 5, 7, 8, 9]])
        alternative_function1 = language.Function(
            parameters=[],
            body=['-', [3, 4, 5, 6, 7, 8, 9], 3])
        alternative_function2 = language.Function(
            parameters=[],
            body=[1, 2, 3])
        best = antiunification.find_best(
            test_function, [alternative_function1, alternative_function2])
        true_best = {
            'applied_in_target': {'body': [[1, 2, 3], [['?', 5]]]},
            'applied_in_other': {'body': ['-', [['?', 6]], 3]},
            'size_difference': 2
        }
        self.assertEqual(
            best['applied_in_target']['body'],
            true_best['applied_in_target']['body'])
        self.assertEqual(
            best['applied_in_other']['body'],
            true_best['applied_in_other']['body'])
        self.assertEqual(
            best['size_difference'], true_best['size_difference'])
