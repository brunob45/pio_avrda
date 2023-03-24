format: $(wildcard *.py)
	isort --profile black $?
	black $?