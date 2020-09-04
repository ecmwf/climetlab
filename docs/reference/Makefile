all: plotting.rst actions.py

plotting.rst: ~/git/magics/src/params/*.xml xml2rst.py
	./xml2rst.py --rst ~/git/magics/src/params/*.xml > plotting.tmp
	mv plotting.tmp plotting.rst

actions.py: ~/git/magics/src/params/*.xml xml2rst.py
	./xml2rst.py --python ~/git/magics/src/params/*.xml > actions.tmp
	mv actions.tmp actions.py
