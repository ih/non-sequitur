import language
import antiunification
import unification


def substitute(function_name, place_holder, application_body):
    """replace the place_holder with function_name in application_body"""
    substitution = []
    for term in application_body:
        if term == place_holder:
            substitution.append(function_name)
        elif type(term) is list:
            substitution.append(substitute(function_name, place_holder, term))
        else:
            substitution.append(term)
    return substitution


def check(function):
    """Any time a function changes try to see if a compression can be made.
    First try to apply an existing pattern, then try to create a new pattern,
    then remove any under-utilized patterns."""
    # apply existing functions
    other_functions = language.Function.index.values()
    other_functions.remove(function)
    best_unification = unification.find_best(
        function, other_functions)
    if best_unification['size_difference'] > 0:
        function.body = best_unification['new_body']
        check(function)
    else:
        # create a new function if it helps
        # here applications are
        # {name: function_name, body: body_with_application}
        possible_functions = language.Function.index.values()
        # since possible_functions includes function we always check for
        # patterns within the function itself
        best_antiunification = antiunification.find_best(
            function, possible_functions)
        if best_antiunification['size_difference'] > 0:
            other_function = language.Function.index[
                best_antiunification['applied_in_other']['name']]
            new_function = language.Function(
                parameters=best_antiunification['new_parameters']['variables'],
                body=best_antiunification['new_body'])
            application_this_body = substitute(
                new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                best_antiunification['applied_in_target']['body'])
            application_other_body = substitute(
                new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                best_antiunification['applied_in_other']['body'])
            function.body = application_this_body
            check(function)
            other_function.body = application_other_body
            check(other_function)
    # remove any underutilized functions
    # only need to check functions used in the body of new_function?
    # only do if there was an antiunification?
    applied_functions = language.get_functions_used(new_function.body)
    underutilized_functions = [
        applied_function for applied_function in applied_functions
        if is_underutilized(applied_function)]
    for underutilized_function in underutilized_functions:
        inline_function(underutilized_function)





def main(data):
    language.Function.reset_index()
    data_program = language.Function(name=language.Symbol('start'))
    for character in data:
        print 'processing character %s' % character
        data_program.body.append(character)
        check(data_program)
    return data_program


test_data = 'abcdbcabcd'
