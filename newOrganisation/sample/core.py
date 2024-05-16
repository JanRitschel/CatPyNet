# -*- coding: utf-8 -*-
from . import Utilities

def get_hmm():
    """Get a thought."""
    return 'hmmm...'


def hmm():
    """Contemplation..."""
    if Utilities.get_answer():
        print(get_hmm())
