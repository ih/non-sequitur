import collections
# expressions
APPLICATION_PLACEHOLDER = '*'
MINIMUM_SUBEXPRESSION_LENGTH = 4


def find_best(target_function, possible_functions):
    """creates a new function and shows how it gets applied
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
    for function in possible_functions:
        function_subexpressions = generate_subexpressions(
            function.body, MINIMUM_SUBEXPRESSION_LENGTH)
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
        for target_subexpression, function_subexpression in subexpression_pairs:
            antiunification = antiunify(
                target_subexpression, function_subexpression)
            if (antiunification['size_difference'] >
                    best_function_antiunification['size_difference']):
                best_function_antiunification = antiunification
        if (best_function_antiunification['size_difference'] >
                best_overall_antiunification['size_difference']):
            best_overall_antiunification = best_function_antiunification
    return best_overall_antiunification

# make the following private to module or add to language?


def generate_subexpressions(expression, minimum_length):
    """ Produce all subarrays of length minimum_length or greater
    e.g. for [[1, 2, 3], 5, [7, 8]] w/ minimum_length 2
    we'd get [[[1,2,3], 5], [5, [7. 8]], [1, 2], [2, 3], [7, 8],
    [[1,2,3], 5, [7, 8]], [1, 2, 3]]
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


def antiunify():
    pass
