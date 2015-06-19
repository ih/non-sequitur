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
        # TODO find a better way to manage application_count
        best_unification['applied_function'].application_count += 1
        functions_to_check = [function]
        # applications in the appplied function body
        applied_application_counts = language.get_functions_used(
            best_unification['applied_function'].body)
        for function_name, count in applied_application_counts.iteritems():
            language.Function.index[function_name].application_count -= count
            if is_underutilized(function_name):
                inlined_into_functions = language.Function.inline(
                    function_name)
                for inlined_into_function in inlined_into_functions:
                    functions_to_check.append(inlined_into_function)
        for function_to_check in functions_to_check:
            check(function_to_check)
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
            new_function = language.Function(
                parameters=best_antiunification['new_parameters']['variables'],
                body=best_antiunification['new_body'],
                application_count=best_antiunification['application_count'])
            applied_function_counts = language.get_functions_used(
                new_function.body)
            # one of the changed_functions will be function so we don't
            # explicitly adjust it here
            functions_to_check = []
            for changed_data in best_antiunification['changed_functions']:
                changed_function = language.Function.index[
                    changed_data['name']]
                new_function_body = substitute(
                    new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                    changed_function['body'])

                changed_function.body = new_function_body
                count_in_abstraction = (
                    applied_function_counts[changed_function.name])
                changed_function.application_count -= ((
                    new_function.application_count * count_in_abstraction) +
                                                       count_in_abstraction)
                if is_underutilized(changed_function.name):
                    inlined_into_functions = language.Function.inline(
                        changed_function.name)
                    for inlined_into_function in inlined_into_functions:
                        functions_to_check.append(inlined_into_function)
                else:
                    functions_to_check.append(changed_function)
            for function_to_check in functions_to_check:
                check(function_to_check)


def is_underutilized(function_name):
    return language.Function.index[function_name].compression_amount < 1


def main(data):
    start = time.clock()
    # language.Function.reset_index()
    data_program = language.Function(name=language.Symbol('start'))
    for i, character in enumerate(data):
        print 'processing character %s' % character
        data_program.body.append(character)
        check(data_program)
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
