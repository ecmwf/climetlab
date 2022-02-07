from climetlab.decorators import normalize


@normalize("option", "date(%Y-%m-%d)")
def f(option):
    return option


assert f(option="2022-12-31") == "2022-12-31"
assert f(option="20221231") == "2022-12-31"
assert f(option=20221231) == "2022-12-31"
