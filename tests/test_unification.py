import language
import unification
import unittest


class TestUnificationMethods(unittest.TestCase):
    def test_evaluate(self):
        variable_expression = language.Symbol('V')
        test_environment = {
            variable_expression: 3
        }
        self.assertEqual(
            unification.evaluate(variable_expression, test_environment), 3)

        empty_environment = {}
        self.assertEqual(
            unification.evaluate(variable_expression, empty_environment),
            variable_expression)

        compound_expression = [language.Symbol('V'), 3, 5]
        self.assertEqual(
            unification.evaluate(compound_expression, test_environment),
            compound_expression)

    def test_occurs_within(self):
        variable = language.Symbol('V')
        expression_with_variable = [[language.Symbol('F'), 2, variable], 'a']
        self.assertEqual(
            unification.occurs_within(variable, expression_with_variable, {}),
            True)
        expression_without_variable = [[language.Symbol('F'), 2], 'a']
        self.assertEqual(
            unification.occurs_within(
                variable, expression_without_variable, {}),
            False)

    def test_apply_function(self):
        variable1 = language.Symbol('V')
        variable2 = language.Symbol('V')
        function_name = language.Symbol('F')
        test_function = language.Function(
            name=function_name,
            parameters=[variable1, variable2],
            body=['+', 3, variable1, 4, variable2])
        test_expression = ['a', 5, '+', 3, 2, 4, 5, 7]
        test_bindings = {
            variable1: 2,
            variable2: 5
        }
        self.assertEqual(
            unification.apply_function(
                test_expression, 2, test_bindings, test_function),
            ['a', 5, [function_name, 2, 5], 7])

    def test_unify(self):
        x = language.Symbol('V')
        y = language.Symbol('V')
        z = language.Symbol('V')
        self.assertEqual(unification.unify(['+', x, 1], ['+', x, 1], {}), {})
        self.assertEqual(
            unification.unify(['+', x, 1], ['+', x, y], {}), {y: 1})
        self.assertEqual(
            unification.unify(['+', x, z], ['+', x, y], {}), {z: y})
        self.assertEqual(
            unification.unify(['+', x, 1, 2], ['+', 1, x, x], {}), False)
        self.assertEqual(
            unification.unify([x, y, 'a'], [y, x, x], {}), {y: 'a', x: y})

    def test_find_best(self):
        target_function = language.Function(
            parameters=[], body=[1, 1, 1, 1, 2, 2, 2])
        # a function that doesn't compress
        bad_function = language.Function(
            parameters=[], body=[0])
        # a function that compresses a small amount
        ok_function = language.Function(
            parameters=[], body=[2, 2, 2])
        # a function that compresses a large amount
        good_function = language.Function(
            parameters=[], body=[1, 1, 1, 1])

        best_unification = unification.find_best(
                target_function, [bad_function, ok_function, good_function])
        self.assertEqual(
            best_unification,
            {
                'bindings': {},
                'new_body': [[good_function.name], 2, 2, 2],
                'size_difference': 3,
                'applied_function': good_function
            })

    def test_compress_function(self):
        variable = language.make_variable()
        compressor = language.Function(
            parameters=[variable], body=['a', variable, 'c'])
        to_compress_string = 'a1cqa2cma3coa4cpa5cra6c'
        to_compress = language.Function(body=list(to_compress_string))
        compressed = unification.compress_function(compressor, to_compress)
        self.assertEqual(
            compressed.body,
            [[compressor.name, '1'], 'q',
             [compressor.name, '2'], 'm',
             [compressor.name, '3'], 'o',
             [compressor.name, '4'], 'p',
             [compressor.name, '5'], 'r',
             [compressor.name, '6']])
