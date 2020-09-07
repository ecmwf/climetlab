#!/usr/bin/env make -f

tests := $(patsubst %.ipynb,%.test,$(wildcard ??-*.ipynb))

all : $(tests)


.ipynb.py:
	jupyter nbconvert --to script $<

.py.test:
	python3 -mIPython $<
	touch $@

clean:
	rm -f *.test *.py

.SUFFIXES: .py .ipynb .test
