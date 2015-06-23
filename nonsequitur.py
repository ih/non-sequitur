import language
import antiunification
import time
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


def check(function, program):
    """Any time a function changes try to see if a compression can be made.
    First try to apply an existing pattern, then try to create a new pattern,
    then remove any under-utilized patterns."""
    # apply existing functions
    other_functions = program.get_all_functions()
    other_functions.remove(function)
    best_unification = unification.find_best(
        function, other_functions)
    if best_unification['size_difference'] > 0:
        function.body = best_unification['new_body']
        # TODO find a better way to manage application_count
        program.application_counts[
            best_unification['applied_function'].name] += 1
        functions_to_check = [function]
        # applications in the appplied function body
        underutilized_function_names = (
            reduce_application_counts_for_applied_body_applications(
                best_unification['applied_function'].body, 1, program))
        for function_name in underutilized_function_names:
            program.inline(function_name)
        for function_name in underutilized_function_names:
            functions_to_check.append(program.get_function(function_name))
        for function in functions_to_check:
            check(function, program)
    else:
        # create a new function if it helps
        # here applications are
        # {name: function_name, body: body_with_application}
        possible_functions = program.get_all_functions()
        # since possible_functions includes function we always check for
        # patterns within the function itself
        best_antiunification = antiunification.find_best(
            function, possible_functions)
        if best_antiunification['size_difference'] > 0:
            new_function = language.Function(
                parameters=best_antiunification['new_parameters']['variables'],
                body=best_antiunification['new_body'])
            program.add_new_function(
                new_function, best_antiunification['application_count'])
            functions_to_check = []
            increase_application_counts_for_new_function_applications(
                new_function.body, program)
            underutilized_function_names = (
                reduce_application_counts_for_applied_body_applications(
                    new_function.body,
                    best_antiunification['application_count'], program))
            for function_name in underutilized_function_names:
                program.inline(function_name)
            for function_name in underutilized_function_names:
                functions_to_check.append(program.get_function(function_name))
            for changed_function_data in best_antiunification[
                    'changed_functions']:
                changed_function = program.get_function(
                    changed_function_data['name'])
                new_function_body = substitute(
                    new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                    changed_function_data['body'])
                changed_function.body = new_function_body
                functions_to_check.append(changed_function)
            for function_to_check in functions_to_check:
                check(function_to_check)


def increase_application_counts_for_new_function_applications(
        new_function_body, program):
    applied_application_counts = language.get_functions_used(
        new_function_body)
    for function_name, count in applied_application_counts:
        program.change_application_count(function_name, count)


def reduce_application_counts_for_applied_body_applications(
        body, body_application_count, program):
    underutilized_functions = []
    applied_application_counts = language.get_functions_used(
        body)
    for function_name, count in applied_application_counts.iteritems():
        program.change_application_count(
            function_name, -count*body_application_count)
        if program.is_underutilized(function_name):
            underutilized_functions.append(function_name)
    return underutilized_functions


def main(data):
    start = time.clock()
    # language.Function.reset_index()
    data_program = language.Program()
    start_function = language.Function(name=language.Symbol('start'))
    data_program.add_new_function(start_function)
    for i, character in enumerate(data):
        print 'processing character %s' % character
        start_function.body.append(character)
        check(start_function, data_program)
    end = time.clock()
    print end-start
    return data_program


test_data = 'abcdbcabcd'
peas = """pease porridge hot,
pease porridge cold,
pease porridge in the pot,
nine days old.

some like it hot,
some like it cold,
some like it in the pot,
nine days old."""

test = 'aa1ccaa2ccaa3ccaa4ccaa5cc'
test2 = 'aa1ccdqaa2ccdpaa3ccdmaa4ccdnaa5ccd'
test3 = 'a1cqa2cma3coa4cpa5cra6c'

# v = language.make_variable()
# language.Function(parameters=[v], body=['a', v, 'c'])

# v = language.make_variable()
# language.Function(parameters=[v], body=['a', 'a', v, 'c', 'c', 'd'])
