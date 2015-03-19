

# TODO add expression abstract class if necessary, make function, variable, etc
# expressions
class Function():
    def __init__(self, name=FunctionSymbol()):
        pass


# self-evaluating things like numbers or characters
class Value():
    def __init__(self, value):
        self.value = value


def main():
    data_program = Function(name=FunctionSymbol('start'), body=Value([]))
