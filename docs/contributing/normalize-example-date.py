from climetlab.decorators import normalize


@normalize("option", "date(%Y-%m-%d)")
def f(self, option):
    print(option)
