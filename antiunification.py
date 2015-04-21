import collections
import language
# expressions
APPLICATION_PLACEHOLDER = '*'
MINIMUM_SUBEXPRESSION_LENGTH = 4


def find_best(target_function, possible_functions):
    """Creates a new function and shows how it gets applied.
    args:
        target_function - the function to be checked against all other function
    Returns:  {
        new_parameters - parameters for the created function,
        new_body - body for the created function,
        applied_in_target - {
            name: name of target_function,
            body:  body of target_function with the new function applied
        },
        applied_in_other - {
            name: name other function antiunified with application_target,
            body: body of other function with new applied
        },
        size_difference: integer
    }
    """
    best_overall_antiunification = {
        'new_parameters': [],
        'new_body': [],
        'applied_in_target': [],
        'applied_in_other': [],
        'size_difference': 0
    }
    target_function_subexpressions = generate_subexpressions(
        target_function.body, MINIMUM_SUBEXPRESSION_LENGTH)
    target_function_size = language.size(target_function)
    for other_function in possible_functions:
        function_subexpressions = generate_subexpressions(
            other_function.body, MINIMUM_SUBEXPRESSION_LENGTH)
        other_function_size = language.size(other_function)
        total_size = target_function_size + other_function_size
        subexpression_pairs = generate_possible_pairs(
            target_function_subexpressions, function_subexpressions)
        best_function_antiunification = {
            'new_parameters': [],
            'new_body': [],
            'applied_in_target': [],
            'applied_in_other': [],
            'size_difference': 0
        }
        # this can probably be parallelized
        for target_subexpression, other_subexpression in subexpression_pairs:
            parameters, abstract_expression = antiunify(
                target_subexpression, other_subexpression)
            applied_in_target = apply_abstract_expression(
                target_function.body, target_subexpression,
                parameters['variables'],
                parameters['expression1_bindings'])
            applied_in_other = apply_abstract_expression(
                other_function.body, other_subexpression,
                parameters['variables'],
                parameters['expression2_bindings'])
            new_total_size = (
                language.size(applied_in_target) +
                language.size(applied_in_other) +
                language.size(abstract_expression))
            new_size_difference = total_size - new_total_size
            if (new_size_difference >
                    best_function_antiunification['size_difference']):
                best_function_antiunification = {
                    'new_parameters': parameters,
                    'new_body': abstract_expression,
                    'applied_in_target': applied_in_target,
                    'applied_in_other': applied_in_other
                }
        if (best_function_antiunification['size_difference'] >
                best_overall_antiunification['size_difference']):
            best_overall_antiunification = best_function_antiunification
    return best_overall_antiunification


def apply_abstract_expression(expression, subexpression, variables, bindings):
    """
    it'd be more efficient if there was a reference to the position of the
    subexpression in function instead of searching.  also by relying on search
    we need to enforce uniqueness of subexpressions when generating them

    actually maybe this is more efficient since we replace multiple
    of the subexpression and now we only need to antiunify one
    """

    function_call = ['?'] + [bindings[variable] for variable in variables]
    applied_expression = []
    subexpression_queue = collections.deque(
        [(expression, applied_expression)])

    while len(subexpression_queue) > 0:
        current_subexpression, current_applied = subexpression_queue
        start_index = 0
        while start_index < (len(current_subexpression)-len(subexpression))+1:
            current_segment = current_subexpression[
                start_index: start_index+len(subexpression)]
            if (current_segment == subexpression):
                current_applied.append(function_call)
                start_index += len(subexpression)
            else:
                term = current_subexpression[start_index]
                start_index += 1
                if type(term) is list:
                    current_applied.append([])
                    subexpression_queue.append(term, current_applied[-1])
                else:
                    current_applied.append(term)

    return applied_expression


def antiunify(expression1, expression2):
    """Create a new function from two expressions by replacing the differences
    with variables.

    e.g. [+, [-, 3, 4], 2] and [+, [*, 3, 4] , 3] => [+, [x, 3, 4], y]

    Returns:
        parameters - {
            'variables': [variable, ...],
            'expression1_arguments': {'variable': value, ...},
            'expression2_arguments': {'variable': value, ...}
        }
        abstract_expression - [expression containing variables]
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
    return parameters, abstract_expression


def reduce_parameters(parameters, abstract_expression):
    # TODO if different variables take on the same values then reduce to
    # the same variable
    # e.g. {x: (4, 2), y: (4, 2)} => {x: (4, 2)}
    return parameters, abstract_expression

# make the following private to module or add to language?


def generate_subexpressions(expression, minimum_length):
    """ Produce all unique* subarrays of length minimum_length or greater
    e.g. for [[1, 2, 3], 5, [7, 8]] w/ minimum_length 2
    we'd get [[[1,2,3], 5], [5, [7. 8]], [1, 2], [2, 3], [7, 8],
    [[1,2,3], 5, [7, 8]], [1, 2, 3]]

    We use unique subexpressions so we can find and replace when applying new
    abstractions.  This works because we look for antiunifications between a
    function and itself.
    """
    subexpressions = []
    possible_lengths = sorted(find_term_lengths(expression, minimum_length))
    for length in possible_lengths:
        subexpressions.extend(
            generate_subexpressions_of_length(expression, length))
    return subexpressions


def find_term_lengths(expression, minimum_length):
    expression_queue = collections.deque([expression])
    # TODO make lengths a set
    lengths = []
    while len(expression_queue) > 0:
        current_expression = expression_queue.popleft()
        if len(current_expression) >= minimum_length:
            lengths.append(len(current_expression))
        for term in current_expression:
            if type(term) is list:
                expression_queue.append(term)
    return sorted(list(set(lengths)))


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


def generate_possible_pairs(expression_list1, expression_list2):
    # TODO make pairs a set
    pairs = []
    for expression1 in expression_list1:
        for expression2 in expression_list2:
            if len(expression1) == len(expression2):
                pairs.append((expression1, expression2))
    return pairs
