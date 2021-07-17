from climetlab.readers.csv import is_csv
from climetlab.readers.text import is_text

print(is_text("/dev/random"))
print(is_text("/dev/zero"))
print(is_text("/dev/null"))

print(is_csv("/dev/random"))
print(is_csv("/dev/zero"))
print(is_csv("/dev/null"))

print(is_text("test"))

print(is_csv("test"))
