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
                        'bindingds': bindings,
                        'new_body': new_target_body,
                        'size_difference': size_difference
                    }
    return best_unification
