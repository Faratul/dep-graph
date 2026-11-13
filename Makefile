PYTHON ?= python3
ARGS ?=

.PHONY: run test lint

run:
	$(PYTHON) -m src.main $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

lint:
	$(PYTHON) -m flake8 --max-complexity 10 src tests
