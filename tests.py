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


if __name__ == '__main__':
    unittest.main()
