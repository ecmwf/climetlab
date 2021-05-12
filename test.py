def colourize(colour):

    n = 0

    def f(txt):
        nonlocal n

        n += 1
        return f"<font colour={colour}>{txt}{n}</font>"

    return f


red = colourize("red")
blue = colourize("blue")


print(blue("hello"), red("world"))
print(red("hello"), red("world"))
