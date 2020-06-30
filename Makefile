PYTHON=/usr/bin/python

test-%:
	${PYTHON} -m unittest discover -b ./$**/ -p *_test.py
