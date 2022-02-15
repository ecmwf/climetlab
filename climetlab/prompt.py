import code
import inspect

frame = inspect.currentframe()
callers = inspect.getouterframes(frame, 0)

# Hacky way to get the calling frame
# It is number 6 in some cases
local = callers[6].frame.f_locals

code.interact(local=local)
