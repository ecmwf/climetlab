def colourize(colour):

    r = dict(n=0)

    def f(txt):

        r['n'] = r['n'] + 1
        return f"<font colour={colour}>{txt}{r['n']}</font>"

    return f


red = colourize('red')
blue = colourize('blue')


print(blue('hello'), red('world'))
print(red('hello'), red('world'))
