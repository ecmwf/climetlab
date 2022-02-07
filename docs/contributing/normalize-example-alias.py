from climetlab.decorators import normalize


@normalize("param", ["tp", "gh"])
def f(param):
    return param


assert f(param="tp") == "tp"
# f(param="t2m") # fails
