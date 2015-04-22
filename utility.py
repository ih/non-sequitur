def list2tuple(list_data):
    if type(list_data) is not list:
        return list_data
    return tuple([list2tuple(item) for item in list_data])


def tuple2list(tuple_data):
    if type(tuple_data) is not tuple:
        return tuple_data
    return [tuple2list(item) for item in tuple_data]
