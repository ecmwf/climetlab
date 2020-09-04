import types


def create_function(name, args):
    def y(a, b, c):
        pass

    co = y.__code__
    y_code = types.CodeType(
        args,
        co.co_posonlyargcount,
        co.co_kwonlyargcount,
        co.co_nlocals,
        co.co_stacksize,
        co.co_flags,
        co.co_code,
        co.co_consts,
        co.co_names,
        co.co_varnames,
        co.co_filename,
        co.co_name,
        co.co_firstlineno,
        co.co_lnotab,
        co.co_freevars,
        co.co_cellvars,
    )

    print(co.co_varnames)
    d = types.FunctionType(y_code, y.__globals__, "sss")

    return d


myfunc = create_function("myfunc", 3)

print(repr(myfunc))

myfunc()
