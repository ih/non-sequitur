import unittest
import language
import nonsequitur
import unification


class TestNonSequiturMethods(unittest.TestCase):
    def test_substitute(self):
        name = language.Symbol('test')
        after_application = nonsequitur.substitute(
            name, '*', ['*', ['*', 2, 3], '*'])
        self.assertEqual(after_application, [name, [name, 2, 3], name])


class TestLanguage(unittest.TestCase):
    def test_size(self):
        self.assertEqual(language.size([1, [2, 3], 4]), 4)

    def test_symbol(self):
        language.Symbol()
        language.Symbol()
        self.assertEquals(len(language.Symbol.prefix_counter), 2)

    def test_function_reset_index(self):
        language.Function()
        language.Function()
        self.assertGreater(len(language.Function.index.keys()), 0)
        language.Function.reset_index()
        self.assertEqual(len(language.Function.index.keys()), 0)


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
                'size_difference': 3
            })


if __name__ == '__main__':
    unittest.main()
