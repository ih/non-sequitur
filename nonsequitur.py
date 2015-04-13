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
        new_parameters, new_body, application_this, application_other = (
            antiunification.find_best(function))
        if application_other:
            other_function = language.Function.index[application_other['name']]
        application_this_is_smaller = (
            application_this and
            language.size(application_this['body']) <
            language.size(function.body))
        application_other_is_smaller = (
            application_other and
            language.size(application_other['body']) <
            language.size(other_function.body))
        if application_this_is_smaller and application_other_is_smaller:
            new_function = language.Function(
                parameters=new_parameters, body=new_body)
            application_this_body = substitute(
                new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                application_this['body'])
            application_other_body = substitute(
                new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                application_other['body'])
            function.body = application_this_body
            check(function)
            other_function.body = application_other_body
            other_function.check()
    # remove any underutilized functions


def main(data):
    data_program = language.Function(name=language.Symbol('start'))
    for character in data:
        data_program.body.append(character)
        check(data_program)
    print data_program


test_data = 'abcdbcabcd'
