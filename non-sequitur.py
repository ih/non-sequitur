# TODO add expression abstract class if necessary, make function, variable, etc
# expressions


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
        assert name not in Function.index
        Function.index[self.name] = self

    def check(self):
        for function in Function.index.values().remove(self):
            pass

    def __str__(self):
        string_parameters = [str(parameter) for parameter in self.parameters]
        return '[%s %s %s]' % (str(self.name), string_parameters, self.body)


def main(data):
    data_program = Function(name=Symbol('start'))
    for character in data:
        data_program.body.append(character)
        data_program.check()
