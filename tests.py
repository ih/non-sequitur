import unittest
import language
import nonsequitur
import unification


class TestNonSequiturMethods(unittest.TestCase):
    def test_size(self):
        self.assertEqual(nonsequitur.size([1, [2, 3], 4]), 4)

    def test_substitute(self):
        name = language.Symbol('test')
        after_application = nonsequitur.substitute(
            name, '*', ['*', ['*', 2, 3], '*'])
        self.assertEqual(after_application, [name, [name, 2, 3], name])


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


if __name__ == '__main__':
    unittest.main()
