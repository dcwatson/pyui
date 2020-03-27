def enumerate_last(items):
    iterator = iter(items)
    try:
        last_val = next(iterator)
    except StopIteration:
        return []
    idx = -1
    for idx, value in enumerate(iterator):
        yield idx, last_val, False
        last_val = value
    yield idx + 1, last_val, True


def clamp(value, low, high):
    return max(min(value, high), low)


def chunked(items, size):
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
