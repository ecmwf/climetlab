from climetlab.decorators import alias_argument


@alias_argument(param="parameter")
def func(param, other):
    return "param=" + param


func(param="tp", other=1)
# -> param=tp

func(parameter="tp", other=1)
# -> param=tp
