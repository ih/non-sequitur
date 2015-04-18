VARIABLE_PREFIX = 'V'


def size(expression):
    if type(expression) is list:
        return sum([size(term) for term in expression])
    else:
        return 1


class Symbol(object):
    prefix_counter = {}

    def __init__(self, prefix='S'):
        if prefix in Symbol.prefix_counter:
            self.value = prefix + str(Symbol.prefix_counter[prefix])
            Symbol.prefix_counter[prefix] += 1
        else:
            self.value = prefix + '0'
            Symbol.prefix_counter[prefix] = 1


    @classmethod
    def reset_counter(cls):
        cls.prefix_counter = {}

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.value == other.value

    def __str__(self):
        return self.value


class Function(object):
    index = {}

    @classmethod
    def reset_index(cls):
        cls.index = {}

    def __init__(self, name=None, parameters=[], body=[]):
        # can't set default argument to Symbol('F') since it is only run once
        if name is None:
            name = Symbol('F')
        self.name = name
        self.parameters = parameters
        self.body = body
        self.application_count = 0
        assert name not in Function.index
        Function.index[self.name] = self

    def __str__(self):
        string_parameters = [str(parameter) for parameter in self.parameters]
        string_body = []
        for term in self.body:
            if type(term) is list:
                string_body.append([str(subterm) for subterm in term])
            else:
                string_body.append(str(term))
        return '[%s %s %s]' % (str(self.name), string_parameters, string_body)


def is_variable(expression):
    return (isinstance(expression, Symbol) and
            expression.value.startswith(VARIABLE_PREFIX))
