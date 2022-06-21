from climetlab.decorators import alias_argument


@alias_argument(param=["parameter", "variable"])
def func(param, other=1):
    return "param=" + param


func(param="tp")
# -> param=tp

func(parameter="tp")
# -> param=tp

func(variable="tp")
# -> param=tp
