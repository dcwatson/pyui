def enumerate_last(items):
    iterator = iter(items)
    try:
        last_val = next(iterator)
    except StopIteration:
        return []
    for idx, value in enumerate(iterator):
        yield idx, last_val, False
        last_val = value
    yield idx + 1, last_val, True
