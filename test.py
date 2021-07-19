from climetlab.utils import string_to_args

print(string_to_args("a"))
print(string_to_args("a()"))
print(string_to_args("a(1,2)"))
print(string_to_args("a(1,p=2)"))
print(string_to_args("a-b(i,j)"))
print(string_to_args("a-b(i=2,j=9)"))
