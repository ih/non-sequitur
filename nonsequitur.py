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
    best_unification = unification.find_best(
        function, language.Function.index.values())
    if best_unification['size_difference'] > 0:
        function.body = best_unification['new_body']
        check(function)
    else:
        # create a new function if it helps
        # here applications are
        # {name: function_name, body: body_with_application}
        possible_functions = language.Function.index.values()

        best_antiunification = antiunification.find_best(
            function, possible_functions)
        if 'applied_in_other' in best_antiunification:
            other_function = language.Function.index[
                antiunification['applied_in_other']['name']]
        if best_antiunification['size_difference'] > 0:
            new_function = language.Function(
                parameters=best_antiunification['new_parameters'],
                body=best_antiunification['new_body'])
            application_this_body = substitute(
                new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                best_unification['applied_in_target']['body'])
            application_other_body = substitute(
                new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                best_unification['application_other']['body'])
            function.body = application_this_body
            check(function)
            other_function.body = application_other_body
            check(other_function)
    # remove any underutilized functions


def main(data):
    data_program = language.Function(name=language.Symbol('start'))
    for character in data:
        data_program.body.append(character)
        check(data_program)
    print data_program


test_data = 'abcdbcabcd'
