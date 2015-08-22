import language
import antiunification
import time
import unification
import cPickle as pickle


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


def check(function_name, program):
    """Any time a function changes try to see if a compression can be made.
    First try to apply an existing pattern, then try to create a new pattern,
    then remove any under-utilized patterns."""
    try:
        function = program.get_function(function_name)
    except KeyError:
        return
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
        changed_functions = enforce_rule_utility(
            best_unification['applied_function'].body, 1, program)
        functions_to_check.extend(changed_functions)
        for function in functions_to_check:
            check(function.name, program)
    else:
        other_functions = program.get_all_functions()
        assert(function in other_functions)
        best_antiunification = antiunification.find_best(
            function, other_functions)
        if best_antiunification is not None:
            for compressed_function in best_antiunification[
                    'compressed_functions']:
                program.set_function(
                    compressed_function.name, compressed_function)
            new_function = best_antiunification['new_function']
            program.add_new_function(new_function)
            new_function_application_count = program.count_applications(
                new_function.name)
            program.change_application_count(
                new_function.name, new_function_application_count)
            changed_functions = enforce_rule_utility(
                new_function.body, new_function_application_count, program)
            changed_functions.extend(
                best_antiunification['compressed_functions'])
            functions_to_check = list(set(changed_functions))

            for function_to_check in functions_to_check:
                check(function_to_check.name, program)


def enforce_rule_utility(body, application_count, program):
    # inline functions
    changed_functions = []
    underutilized_function_names = (
        reduce_application_counts_for_applied_body_applications(
            body, application_count, program))
    for function_name in underutilized_function_names:
        assert function_name in program.functions
        changed_functions.extend(program.inline(function_name))
    return changed_functions


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
    start_function = language.Function(name=language.Symbol('start'))
    data_program = language.Program(start_function)
    for i, character in enumerate(data):
        print 'processing character %s' % character
        print data_program
        data_program.get_function(start_function.name).body.append(character)
        check(start_function.name, data_program)
    end = time.clock()
    print end-start
    print data_program
    return data_program

# test_data = 'abcdbcabcd'
peas = """pease porridge hot,
pease porridge cold,
pease porridge in the pot,
nine days old.

some like it hot,
some like it cold,
some like it in the pot,
nine days old."""

# test = 'aa1ccaa2ccaa3ccaa4ccaa5cc'
# test2 = 'aa1ccdqaa2ccdpaa3ccdmaa4ccdnaa5ccd'
# test3 = 'a1cqa2cma3coa4cpa5cra6c'

pickle.dump(main(peas), open('peas', 'wb'))
