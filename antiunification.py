import collections
import language
import utility
import unification
# expressions
APPLICATION_PLACEHOLDER = '?'
MINIMUM_SUBEXPRESSION_LENGTH = 2


def find_best(target_function, other_functions):
    """Find the antiunification between target_function and other_functions that
    compresses other_functions the most.  Assumes other_functions contains
    target_function
    args:
        target_function - the function to be checked against all other function
    Returns:  {
        new_function: the function created through antiunification,
        compressed_functions: a list of functions where the new_function was
            applied in the body
    }
    """
    assert(target_function in other_functions)
    best_antiunification = None
    best_compression_amount = 0
    target_function_subexpressions = language.generate_subexpressions(
        target_function.body, MINIMUM_SUBEXPRESSION_LENGTH)
    for other_function in other_functions:
        function_subexpressions = language.generate_subexpressions(
            other_function.body, MINIMUM_SUBEXPRESSION_LENGTH)
        subexpression_pairs = generate_possible_pairs(
            target_function_subexpressions, function_subexpressions)
        # this can probably be parallelized
        for target_subexpression, other_subexpression in subexpression_pairs:
            abstracted_function = antiunify(
                target_subexpression, other_subexpression)
            compressed_functions = unification.compress_functions(
                abstracted_function, other_functions)
            compression_amount = compute_compression_amount(
                compressed_functions, other_functions)
            if compression_amount > best_compression_amount:
                best_antiunification = {
                    'new_function': abstracted_function,
                    'compressed_functions': compressed_functions
                }
    return best_antiunification


def compute_compression_amount(compressed_functions, possible_functions):
    # TODO cleaner way to write this w/o internal function?
    def find_original(target_function, all_functions):
        for function in all_functions:
            if target_function.name == function.name:
                return function
        assert(False)
    compression_amount = 0
    for compressed_function in compressed_functions:
        original_function = find_original(
            compressed_function, possible_functions)
        compressed_function_size = language.function_size(compressed_function)
        original_size = language.function_size(original_function)
        assert(compressed_function_size < original_size)
        compression_amount += (original_size - compressed_function_size)
    return compression_amount


def apply_abstract_expression(expression, subexpression, variables, bindings):
    """
    replace subexpression in expression with a call to an unknown function
    pass the arguments based on bindings to the function call

    it'd be more efficient if there was a reference to the position of the
    subexpression in function instead of searching.  also by relying on search
    we need to enforce uniqueness of subexpressions when generating them

    actually maybe this is more efficient since we replace multiple
    of the subexpression and now we only need to antiunify one
    """
    application_count = 0
    function_call = (
        [APPLICATION_PLACEHOLDER] +
        [bindings[variable] for variable in variables])
    applied_expression = []
    subexpression_queue = collections.deque(
        [(expression, applied_expression)])

    while len(subexpression_queue) > 0:
        current_subexpression, current_applied = subexpression_queue.popleft()
        start_index = 0
        while start_index < len(current_subexpression):
            current_segment = current_subexpression[
                start_index: start_index+len(subexpression)]
            if (current_segment == subexpression):
                application_count += 1
                current_applied.append(function_call)
                start_index += len(subexpression)
            else:
                term = current_subexpression[start_index]
                start_index += 1
                if type(term) is list:
                    current_applied.append([])
                    subexpression_queue.append((term, current_applied[-1]))
                else:
                    current_applied.append(term)
    return applied_expression, application_count


def antiunify(expression1, expression2):
    """Create a new function from two expressions by replacing the differences
    with variables.

    e.g. [+, [-, 3, 4], 2] and [+, [*, 3, 4] , 3] => [+, [x, 3, 4], y]

    Returns:
        Function - a language.Function with name prefixed by Temp
    """
    if len(expression1) != len(expression2):
        return False
    abstract_expression = []
    expression_queue1 = collections.deque([(expression1, abstract_expression)])
    expression_queue2 = collections.deque([expression2])
    # key is the variable name
    # value the value of the variable in each expression
    parameters = {}

    while len(expression_queue1) > 0:
        (current_expression1,
         current_abstract_expression) = expression_queue1.popleft()
        current_expression2 = expression_queue2.popleft()

        for index, term1 in enumerate(current_expression1):
            term2 = current_expression2[index]
            if term1 == term2:
                current_abstract_expression.append(term1)
            elif (type(term1) is list and type(term2) is list and
                  len(term1) == len(term2)):
                current_abstract_expression.append([])
                expression_queue1.append(
                    (term1, current_abstract_expression[-1]))
                expression_queue2.append(term2)
            else:
                new_variable = language.make_variable()
                parameters[new_variable] = (term1, term2)
                current_abstract_expression.append(new_variable)
    parameters, abstract_expression = reduce_parameters(
        parameters, abstract_expression)
    # reformat parameters data for convenience
    variables = parameters.keys()
    parameters = {
        'variables': variables,
        'expression1_bindings': dict([
            (variable, parameters[variable][0]) for variable in variables]),
        'expression2_bindings': dict([
            (variable, parameters[variable][1]) for variable in variables])
    }
    new_function = language.Function(
        name=language.Symbol('Temp'), parameters=variables,
        body=abstract_expression)
    return new_function


def reduce_parameters(parameters, abstract_expression):
    # TODO if different variables take on the same values then reduce to
    # the same variable
    # e.g. {x: (4, 2), y: (4, 2)} => {x: (4, 2)}
    return parameters, abstract_expression


# this is in antiunification instead of language because we only look
# at pairs for antiunification (same length and unique)
def generate_possible_pairs(expression_list1, expression_list2):
    # use a dict for filtering duplicates
    pairs = {}
    for expression1 in expression_list1:
        for expression2 in expression_list2:
            if len(expression1) == len(expression2):
                possible_pair = (
                    utility.list2tuple(expression1),
                    utility.list2tuple(expression2))
                reverse_pair = (possible_pair[1], possible_pair[0])
                if possible_pair not in pairs and reverse_pair not in pairs:
                    pairs[possible_pair] = True
    return [(utility.tuple2list(pair[0]), utility.tuple2list(pair[1])) for
            pair in pairs]
