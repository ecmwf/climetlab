from climetlab.decorators import normalize


@normalize("option", "int", multiple=True)
def f(option):
    return option


# Alternative shorter version
@normalize("option", "int-list")
def g(option):
    return option


assert f(option="2022") == [2022]
assert g(option="2022") == [2022]
assert f(option=[48, 72.0, "96"]) == [48, 72, 96]
assert g(option=[48, 72.0, "96"]) == [48, 72, 96]
