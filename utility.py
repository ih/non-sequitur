import collections


def list2tuple(list_data):
    if type(list_data) is not list:
        return list_data
    return tuple([list2tuple(item) for item in list_data])


def tuple2list(tuple_data):
    if type(tuple_data) is not tuple:
        return tuple_data
    return [tuple2list(item) for item in tuple_data]


def traverse(nested_list, iterable_types=[list, tuple]):
    item_queue = collections.deque([nested_list])
    while len(item_queue) > 0:
        current_item = item_queue.popleft()
        if type(current_item) not in iterable_types:
            yield current_item
        else:
            for item in current_item[::-1]:
                item_queue.appendleft(item)
