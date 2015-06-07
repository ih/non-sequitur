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
        # applications in the appplied function body
        applied_application_counts = language.get_functions_used(
            best_unification['applied_function'].body)
        for function_name, count in applied_application_counts.iteritems():
            language.Function.index[function_name].application_count -= count
        check(function)
        # remove any underutilized functions
        # TODO think about whether inlining should happen before check
        inline_underutilized(applied_application_counts)
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
            new_function.application_count = (
                best_antiunification['application_count'])
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
            applied_function_counts = language.get_functions_used(
                new_function.body)
            decrement_application_counts(applied_function_counts, new_function)
            inline_underutilized(applied_function_counts)


# TODO find a better place to put this
def decrement_application_counts(application_counts, new_function):
    """
    The number of applications for a function can decrease if they are in the
    of a newly created function.  This function is called after antiunification
    to decrement function application counts if appropriate
    """
    for function_name, application_count in application_counts.iteritems():
        # each place we applied the new function we reduced the number of calls
        # function_name by application_count, but we still have the calls in
        # the new_function body so that's where the -1 of application_count - 1
        # comes from
        applications_removed = (
            (new_function.application_count * application_count) - 1)
        language.Function.index[
            function_name].application_count -= applications_removed


def is_underutilized(function_name):
    return language.Function.index[function_name].application_count < 2


def inline_underutilized(application_counts):
    underutilized_function_names = [
        applied_function_name for applied_function_name
        in application_counts.keys()
        if is_underutilized(applied_function_name)]
    for underutilized_function_name in underutilized_function_names:
        language.Function.inline(underutilized_function_name)
        del language.Function.index[underutilized_function_name]


def main(data):
    start = time.clock()
    language.Function.reset_index()
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
test2 = 'aa1ccdqaa2ccdpaa3ccdmaa4ccdnaaccd'
