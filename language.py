import collections
import utility

VARIABLE_PREFIX = 'V'


def size(expression):
    if type(expression) is list:
        return sum([size(term) for term in expression])
    else:
        return 1


class Symbol(object):
    prefix_counter = {}

    def __init__(self, prefix='S'):
        if prefix in Symbol.prefix_counter:
            self.value = prefix + str(Symbol.prefix_counter[prefix])
            Symbol.prefix_counter[prefix] += 1
        else:
            self.value = prefix + '0'
            Symbol.prefix_counter[prefix] = 1

    @classmethod
    def reset_counter(cls):
        cls.prefix_counter = {}

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.value == other.value

    def __str__(self):
        return self.value


class Function(object):
    index = {}

    @classmethod
    def reset_index(cls):
        cls.index = {}

    def __init__(self, name=None, parameters=None, body=None):
        # can't set default argument to Symbol('F') since it is only run once
        if name is None:
            name = Symbol('F')
        if parameters is None:
            parameters = []
        if body is None:
            body = []
        self.name = name
        self.parameters = parameters
        self.body = body
        self.application_count = 0
        assert name not in Function.index
        Function.index[self.name] = self

    def __str__(self):
        string_parameters = [str(parameter) for parameter in self.parameters]
        string_body = []
        for term in self.body:
            if type(term) is list:
                string_body.append([str(subterm) for subterm in term])
            else:
                string_body.append(str(term))
        return '[%s %s %s]' % (str(self.name), string_parameters, string_body)


def make_variable():
    return Symbol(VARIABLE_PREFIX)


def is_variable(expression):
    return (isinstance(expression, Symbol) and
            expression.value.startswith(VARIABLE_PREFIX))


def generate_subexpressions(expression, minimum_length):
    """ Produce all unique* subarrays of length minimum_length or greater
    e.g. for [[1, 2, 3], 5, [7, 8]] w/ minimum_length 2
    we'd get [[[1,2,3], 5], [5, [7. 8]], [1, 2], [2, 3], [7, 8],
    [[1,2,3], 5, [7, 8]], [1, 2, 3]]

    * We use unique subexpressions so we can find and replace when applying new
    abstractions.  This works because we look for antiunifications between a
    function and itself.
    """
    subexpressions = set([])
    possible_lengths = range(minimum_length, longest_term_length(expression)+1)
    for length in possible_lengths:
        subexpressions.update(
            utility.list2tuple(
                generate_subexpressions_of_length(expression, length)))
    return [
        utility.tuple2list(subexpression) for subexpression in subexpressions]


def longest_term_length(expression):
    expression_queue = collections.deque([expression])
    max_length = 0
    while len(expression_queue) > 0:
        current_expression = expression_queue.popleft()
        if len(current_expression) > max_length:
            max_length = len(current_expression)
        for term in current_expression:
            if type(term) is list:
                expression_queue.append(term)
    return max_length


def generate_subexpressions_of_length(expression, length):
    expression_queue = collections.deque([expression])
    # TODO make subexpressions a set
    subexpressions = []
    while len(expression_queue) > 0:
        current_expression = expression_queue.popleft()
        if len(current_expression) >= length:
            for i in range(0, len(current_expression) - length + 1):
                subexpressions.append(current_expression[i:length+i])
        for term in current_expression:
            if type(term) is list:
                expression_queue.append(term)
    return subexpressions
