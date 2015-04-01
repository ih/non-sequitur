import antiunification
import unification

# TODO add expression abstract class if necessary, make function, variable, etc
# expressions
APPLICATION_PLACEHOLDER = '*'


def size(expression):
    if type(expression) is list:
        return sum([size(term) for term in expression])
    else:
        return 1


def substitute():
    pass


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
        best_substitution, new_body = self.find_best_unification()
        if size(new_body) < size(self.body):
            self.body = new_body
            self.check()
        else:
            # create a new function if it helps
            # here applications are
            # {name: function_name, body: body_with_application}
            new_parameters, new_body, application_self, application_other = (
                self.find_best_antiunification())
            other_function = Function.index[application_other['name']]
            application_self_is_smaller = (
                size(application_self['body']) < size(self.body))
            application_other_is_smaller = (
                size(application_other['body']) < size(other_function.body))
            if application_self_is_smaller and application_other_is_smaller:
                new_function = Function(
                    parameters=new_parameters, body=new_body)
                application_self_body = substitute(
                    new_function.name, APPLICATION_PLACEHOLDER,
                    application_self)
                application_other_body = substitute(
                    new_function.name, APPLICATION_PLACEHOLDER,
                    application_other)
                self.body = application_self_body
                self.check()
                other_function.body = application_other_body
                other_function.check()
        # remove any underutilized functions

    def find_best_unification(self):
        return unification.find_best(self)

    def find_best_antiunification(self):
        return antiunification.find_best(self)

    def __str__(self):
        string_parameters = [str(parameter) for parameter in self.parameters]
        return '[%s %s %s]' % (str(self.name), string_parameters, self.body)


def main(data):
    data_program = Function(name=Symbol('start'))
    for character in data:
        data_program.body.append(character)
        data_program.check()
