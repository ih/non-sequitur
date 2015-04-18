import antiunification
import unittest


class TestAntiunification(unittest.TestCase):
    def test_antiunify(self):
        expression1 = ['+', ['-', 3, 4], 2]
        expression2 = ['+', ['*', 3, 4], 3]
        print antiunification.antiunify(expression1, expression2)
