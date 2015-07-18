import collections
import utility

VARIABLE_PREFIX = 'V'
FUNCTION_PREFIX = 'F'
FUNCTION_NAME_SIZE = 1


def expression_size(expression):
    if type(expression) is list:
        return sum([expression_size(term) for term in expression])
    else:
        return 1


def function_size(function):
    return (
        FUNCTION_NAME_SIZE + expression_size(function.body) +
        len(function.parameters))


class Symbol(object):
    prefix_counter = {}

    def __init__(self, prefix='S', count=None):
        if count is not None:
            self.value = prefix + str(count)
        else:
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


class Program(object):
    def __init__(self):
        self.functions = {}
        self.application_counts = {}

    def get_function(self, function_name):
        return self.functions[function_name]

    def get_all_functions(self):
        return self.functions.values()

    def add_new_function(self, new_function, application_count=0):
        self.functions[new_function.name] = new_function
        self.application_counts[new_function.name] = application_count

    def change_application_count(self, function_name, amount_difference):
        self.application_counts[function_name] += amount_difference

    def size(self):
        return sum(
            [function_size(function) for function in self.functions.values()])

    def __str__(self):
        all_functions = ''
        for function in self.functions.values():
            all_functions += str(function) + '\n'
        return all_functions

    def inline(self, inline_function):
        if is_function_name(inline_function):
            inline_function = self.functions[inline_function]
        # optimize by keeping track of where applications are
        functions_with_applications = self.find_applications(inline_function)
        assert len(functions_with_applications) == 1

        def is_inline_application(term):
            return is_application(term) and term[0] == inline_function.name
        for function_with_application in functions_with_applications:
            function_with_application.body = substitute(
                is_inline_application, inline_function.body,
                function_with_application.body)
        return functions_with_applications

    def find_applications(self, function):
        functions_with_applications = []
        for other_function in self.functions.values():
            functions_used = get_functions_used(other_function.body)
            if function.name in functions_used:
                functions_with_applications.append(other_function)
        return functions_with_applications

    def count_applications(self, function):
        application_count = 0
        for other_function in self.functions.values():
            functions_used = get_functions_used(other_function.body)
            if function.name in functions_used:
                application_count += functions_used[function.name]
        return application_count

    def compression_amount(self, function):
        body_size = len(function.body)
        parameter_size = len(function.parameters)
        return (((body_size - (parameter_size + 1)) *
                 self.application_counts[function.name]) -
                (body_size + parameter_size + 1))

        def is_underutilized(self, function_name):
            return self.compression_amount(function_name) < 1


class Function(object):
    def __init__(
            self, name=None, parameters=None, body=None, application_count=0):
        # can't set default argument to Symbol('F') since it is only run once
        if name is None:
            name = Symbol(FUNCTION_PREFIX)
        if parameters is None:
            parameters = []
        if body is None:
            body = []
        self.name = name
        self.parameters = parameters
        self.body = body
        self.application_count = application_count

    def __str__(self):
        string_parameters = [str(parameter) for parameter in self.parameters]
        string_body = []
        for term in self.body:
            if type(term) is list:
                string_body.append([str(subterm) for subterm in term])
            else:
                string_body.append(str(term))
        return '[%s %s %s] %s' % (
            str(self.name), string_parameters, string_body)


def make_variable():
    return Symbol(VARIABLE_PREFIX)


def is_variable(expression):
    return (isinstance(expression, Symbol) and
            expression.value.startswith(VARIABLE_PREFIX))


def is_function_name(expression):
    return (isinstance(expression, Symbol) and
            expression.value.startswith(FUNCTION_PREFIX))


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


def get_functions_used(expression):
    """
    Get the functions used in an expression as well as how many times they are
    used.

    Return:
        {function_name: number of applications, ...}
    """
    functions = {}
    for term in utility.traverse(expression):
        if is_function_name(term):
            if term not in functions:
                functions[term] = 0
            functions[term] += 1
    return functions


def substitute(replacement_check, replacement, expression):
    substitution = []
    for term in expression:
        if replacement_check(term):
            substitution.extend(replacement)
        elif type(term) is list:
            substitution.append(
                substitute(replacement_check, replacement, term))
        else:
            substitution.append(term)
    return substitution


def is_application(term):
    return type(term) is list and is_function_name(term[0])


def evaluate(expression, environment):
    if is_application(expression):
        new_environment = bind_variables(expression, environment)
        # look up the function in the environment not the global index or pass
        # a program?
        return evaluate(Function.index[expression[0]].body, new_environment)
    elif type(expression) is list:
        evaluated_expression = []
        for term in expression:
            evaluated_term = evaluate(term, environment)
            if is_application(term):
                evaluated_expression.extend(evaluated_term)
            else:
                evaluated_expression.append(evaluated_term)
        return evaluated_expression
    elif is_variable(expression):
        return environment[expression]
    else:
        # primitive case
        return expression


def bind_variables(function_application, environment):
    if len(function_application) == 1:
        return environment
    new_environment = environment.copy()
    function_name = function_application[0]
    function_arguments = function_application[1:]
    # look up the function in the environment not the global index or pass
    # a program?
    evaluated_arguments = [
        evaluate(argument, environment) for argument in function_arguments]
    new_environment.update(
        zip(Function.index[function_name].parameters, evaluated_arguments))
    return new_environment
