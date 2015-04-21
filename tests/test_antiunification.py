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
