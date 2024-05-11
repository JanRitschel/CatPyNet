def get_answer():
    """Get an answer."""
    return True

def contains_all(set:iter, subset:iter) -> bool:
    '''check if iteralble "set" contains all elements of another iterable "subset"'''
    return all(element in set for element in subset)