import code
import inspect


def get_locals(callers):
    for c in callers[1:]:
        if not c.filename.startswith("<frozen importlib"):
            return c.frame.f_locals
    import logging

    logging.debug("Cannot find calling frame.")
    return {}


frame = inspect.currentframe()
callers = inspect.getouterframes(frame, 0)

code.interact(local=get_locals(callers))
