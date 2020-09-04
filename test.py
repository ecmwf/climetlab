import inspect


def g(**wargs):
    pass


def args(frame):
    func = frame.f_globals[frame.f_code.co_name]
    user_args = inspect.getargvalues(frame)
    code_args = inspect.getfullargspec(func)
    given = {}
    for name, value in zip(code_args.args, code_args.defaults):
        if user_args.locals[name] is not value:
            given[name] = user_args.locals[name]
    return given


def f(a=1, b=2, c=3):
    print(args(inspect.currentframe()))


f(b=42)
