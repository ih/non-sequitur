import language


def find_best(target_function, possible_functions):
    """Search through functions and look at potential ways to compress function.
    Args:
        target_function - Function object function to be compressed
        possible_functions - possible functions to apply
    Returns:
        (best_substitution, new_body) - best_substitution is the parameter
    argument mapping for the function that best compressed target_function.
    new_body is the body of the target_function with the best function applied
    """
    best_unification = {
        'bindings': {}, 'new_body': [], 'size_difference': 0}
    for function in possible_functions:
        # try to match the body of function in different places of target_
        # function body
        if len(function.body) > len(target_function.body):
            continue
        last_start_index = len(target_function.body) - len(function.body)
        for start_index in range(0, last_start_index+1):
            bindings = unify(
                target_function.body[start_index: len(function.body)],
                function.body, {})
            if bindings:
                new_target_body = apply_function(
                    target_function.body, start_index, bindings, function)
                size_difference = (
                    len(target_function.body) - len(new_target_body))
                if size_difference < best_unification['size_difference']:
                    best_unification = {
                        'bindings': bindings,
                        'new_body': new_target_body,
                        'size_difference': size_difference
                    }
    return best_unification


def unify(expression1, expression2, environment):
    if not environment:
        return False
    evaluated_expression1 = evaluate(expression1)
    evaluated_expression2 = evaluate(expression2)
    if evaluated_expression1 == evaluated_expression2:
        return environment
    elif language.is_variable(expression1):
        if occurs_within(expression1, expression2, environment):
            return False
        else:
            environment[expression1] = expression2
            return environment
    elif language.is_variable(expression2):
        if occurs_within(expression2, expression1, environment):
            return False
        else:
            environment[expression2] = expression1
            return environment
    elif type(expression1) is list and type(expression2) is list:
        new_environment = unify(expression1[0], expression2[0], environment)
        return unify(expression1[1:], expression2[1:], new_environment)
    else:
        False


def occurs_within(variable, expression, environment):
    if evaluate(expression, environment) == variable:
        return True
    elif type(expression) is list and len(expression) > 0:
        return (occurs_within(variable, expression[0], environment) or
                occurs_within(variable, expression[1:], environment))
    else:
        return False


def evaluate(expression, environment):
    if language.is_variable(expression) and expression in environment:
        return environment[expression]
    return expression
