import inspect


def g(**wargs):
    print(wargs)


def args(frame):
    func = frame.f_globals[frame.f_code.co_name]
    user_args = inspect.getargvalues(frame)
    code_args = inspect.getfullargspec(func)
    given = {}

    if code_args.kwonlydefaults:
        pairs = list(code_args.kwonlydefaults.items())
    else:
        pairs = list(zip(code_args.args, code_args.defaults))

    for name, value in pairs:
        if user_args.locals[name] is not value:
            given[name] = user_args.locals[name]
    return given


def f(*, a=1, b=2, c=3):
    g(**args(inspect.currentframe()))


f(b=42)
