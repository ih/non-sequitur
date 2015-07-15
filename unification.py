import collections
import copy
import language


def find_best(target_function, possible_functions):
    """Search through functions and look at potential ways to compress function.
    Args:
        target_function - Function object function to be compressed
        possible_functions - possible functions to apply
    Returns: {
        bindings - {variable: value,...},
        new_body - [],
        size_difference - integer,
    }
    """
    best_unification = {
        'bindings': {}, 'new_body': [], 'size_difference': 0,
        'applied_function': None}
    for function in possible_functions:
        # try to match the body of function in different places of target_
        # function body
        if len(function.body) > len(target_function.body):
            continue
        last_start_index = len(target_function.body) - len(function.body)

        for start_index in range(0, last_start_index+1):
            bindings = unify(
                target_function.body[
                    start_index: start_index+len(function.body)],
                function.body, {})
            if bindings is not False:
                new_target_body = apply_function(
                    target_function.body, start_index, bindings, function)
                size_difference = (
                    language.expression_size(target_function.body) -
                    language.expression_size(new_target_body))
                if size_difference > best_unification['size_difference']:
                    best_unification = {
                        'bindings': bindings,
                        'new_body': new_target_body,
                        'size_difference': size_difference,
                        'applied_function': function
                    }
    return best_unification


def apply_function(expression, start_index, bindings, function):
    """Replace part of expression with an application of function"""
    # remove the part of expression being replaced
    abbreviated_expression = (
        expression[0:start_index] +
        expression[start_index+len(function.body):])
    # create the function application
    application = (
        [function.name] +
        [bindings[parameter] for parameter in function.parameters])
    # insert the application into the expression
    abbreviated_expression.insert(start_index, application)
    return abbreviated_expression


def unify(expression1, expression2, environment):
    if environment is False:
        return False
    evaluated_expression1 = evaluate(expression1, environment)
    evaluated_expression2 = evaluate(expression2, environment)
    if evaluated_expression1 == evaluated_expression2:
        return environment
    elif language.is_variable(evaluated_expression1):
        if occurs_within(
                evaluated_expression1, evaluated_expression2, environment):
            return False
        else:
            environment[evaluated_expression1] = evaluated_expression2
            return environment
    elif language.is_variable(evaluated_expression2):
        if occurs_within(
                evaluated_expression2, evaluated_expression1, environment):
            return False
        else:
            environment[evaluated_expression2] = evaluated_expression1
            return environment
    elif (type(evaluated_expression1) is list and
          type(evaluated_expression2) is list):

        new_environment = unify(
            evaluated_expression1[0], evaluated_expression2[0], environment)
        return unify(
            evaluated_expression1[1:], evaluated_expression2[1:],
            new_environment)
    else:
        return False


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


def compress_functions(compressor, functions_to_compress):
    """use the compressor function to compress functions_to_compress via
    unification

    return a list of functions from functions_to_compress where compressor
    function acutally compressed the function
    """
    compressed_functions = []
    for function in functions_to_compress:
        compressed_function = compress_function(
            compressor, function)
        if language.function_size(
                compressed_function) < language.function_size(function):
            compress_functions.append(compressed_function)
    return compressed_functions


def compress_function(compressor, function):
    compressed_function = copy.deepcopy(function)
    compressed_body = []
    subexpression_queue = collections.deque(
        [(compressed_function.body, compressed_body)])

    while len(subexpression_queue) > 0:
        current_subexpression, current_applied = subexpression_queue.popleft()
        start_index = 0
        while start_index < len(current_subexpression):
            current_segment = current_subexpression[
                start_index: start_index+len(compressor.body)]
            bindings = unify(compressor.body, current_segment, {})
            if bindings:
                function_call = [compressor.name] + [
                    bindings[variable] for variable in compressor.parameters]
                current_applied.append(function_call)
                start_index += len(compressor.body)
            else:
                term = current_subexpression[start_index]
                start_index += 1
                if type(term) is list:
                    current_applied.append([])
                    subexpression_queue.append((term, current_applied[-1]))
                else:
                    current_applied.append(term)
    compressed_function.body = compressed_body
    return compressed_function
