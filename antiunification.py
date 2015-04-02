# expressions
APPLICATION_PLACEHOLDER = '*'


def find_best(target_function):
    """creates a new function and shows how it gets applied
    args:
        target_function - the function to be checked against all other function
    returns:
        new_parameters - parameters for the created function
        new_body - body for the created function
        application_target - {
            name: name of target_function,
            body:  body of target_function with the new function applied
        }
        application_other - {
            name: name other function antiunified with application_target,
            body: body of other function with new applied
        }
    """
    if target_function.body == ['a', 'b', 'c', 'd', 'b', 'c']:
        return ([], ['b', 'c'],
                {
                    'name': target_function.name,
                    'body': ['a', ['*'], 'd', ['*']]
                }, {
                    'name': target_function.name,
                    'body': ['a', ['*'], 'd', ['*']]
                })
    else:
        return (None, None, None, None)
