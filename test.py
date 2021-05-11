class A:
    @classmethod
    def foo(*args):
        print(args)


class B(A):
    pass


A.foo(1)
B.foo(2)

B().foo(3)
