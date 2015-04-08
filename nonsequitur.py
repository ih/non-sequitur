import ipdb

import antiunification
import unification


def size(expression):
    if type(expression) is list:
        return sum([size(term) for term in expression])
    else:
        return 1


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


class Symbol(object):
    prefix_counter = {}

    def __init__(self, prefix='S'):
        if prefix in Symbol.prefix_counter:
            Symbol.prefix_counter[prefix] += 1
            self.value = prefix + str(Symbol.prefix_counter[prefix])
        else:
            Symbol.prefix_counter[prefix] = 0
            self.value = prefix + '0'

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return self.value


class Function(object):
    index = {}

    def __init__(self, name=Symbol('F'), parameters=[], body=[]):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.application_count = 0
        assert name not in Function.index
        Function.index[self.name] = self

    def check(self):
        # apply existing functions
        best_unification = self.find_best_unification()
        if best_unification['size_difference'] > 0:
            self.body = best_unification['new_body']
            self.check()
        else:
            # create a new function if it helps
            # here applications are
            # {name: function_name, body: body_with_application}
            new_parameters, new_body, application_self, application_other = (
                self.find_best_antiunification())
            if application_other:
                other_function = Function.index[application_other['name']]
            application_self_is_smaller = (
                application_self and
                size(application_self['body']) < size(self.body))
            application_other_is_smaller = (
                application_other and
                size(application_other['body']) < size(other_function.body))
            if application_self_is_smaller and application_other_is_smaller:
                new_function = Function(
                    parameters=new_parameters, body=new_body)
                application_self_body = substitute(
                    new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                    application_self['body'])
                application_other_body = substitute(
                    new_function.name, antiunification.APPLICATION_PLACEHOLDER,
                    application_other['body'])
                self.body = application_self_body
                self.check()
                other_function.body = application_other_body
                other_function.check()
        # remove any underutilized functions

    def find_best_unification(self):
        """argument mapping for the function that best compressed target_
        function.
        Returns:
            {
                bindings: dictionary
                new_body: expression with application
                size_difference: size without application minus size with
            }
        """
        return unification.find_best(self, Function.index)

    def find_best_antiunification(self):
        return antiunification.find_best(self)

    def __str__(self):
        string_parameters = [str(parameter) for parameter in self.parameters]
        string_body = []
        for term in self.body:
            if type(term) is list:
                string_body.append([str(subterm) for subterm in term])
            else:
                string_body.append(str(term))
        return '[%s %s %s]' % (str(self.name), string_parameters, string_body)


def main(data):
    data_program = Function(name=Symbol('start'))
    for character in data:
        data_program.body.append(character)
        data_program.check()
    print data_program


test_data = 'abcdbcabcd'
