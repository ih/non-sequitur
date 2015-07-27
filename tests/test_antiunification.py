import antiunification
import language
import unification
import unittest


class TestAntiunification(unittest.TestCase):
    def test_antiunify(self):
        expression1 = ['+', ['-', 3, 4], 2]
        expression2 = ['+', ['*', 3, 4], 3]
        abstracted_function = antiunification.antiunify(
            expression1, expression2)
        language.Symbol.reset_counter()
        variable1 = language.make_variable()
        variable2 = language.make_variable()
        correct_abstract_expression = ['+', [variable2, 3, 4], variable1]
        self.assertEqual(unification.is_equivalent_expression(
            abstracted_function.body, correct_abstract_expression), True)

    def test_antiunify_self(self):
        expression = ['+', ['-', 3, 4], 2]
        abstracted_function = antiunification.antiunify(
            expression, expression)
        self.assertEquals(abstracted_function.body, expression)

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
        self.assertEqual(best['new_function'].body, [1, 2])

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
        self.assertEqual(best, None)
        best = antiunification.find_best(
            test_function,
            [alternative_function1, alternative_function2, test_function])
        self.assertEqual(len(best['new_function'].parameters), 1)
        variable = best['new_function'].parameters[0]
        self.assertEqual(unification.is_equivalent_expression(
            best['new_function'].body, [3, 4, 5, variable, 7, 8, 9]), True)
        self.assertEqual(len(best['compressed_functions']), 2)
