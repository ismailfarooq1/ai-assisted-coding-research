PYTHON ?= python3

.PHONY: setup check doctor status test
setup:
	$(PYTHON) tools/setup.py setup all
check:
	$(PYTHON) tools/setup.py check all
doctor:
	$(PYTHON) tools/setup.py doctor
status:
	$(PYTHON) tools/setup.py status
test:
	$(PYTHON) -m unittest discover -s tools/tests -v
