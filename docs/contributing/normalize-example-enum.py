from climetlab.decorators import normalize


@normalize("param", ["tp", "gh"])
def f(self, param):
    print(param)
