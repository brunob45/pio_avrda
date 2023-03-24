files = patchpio.py

format: $(files)
	isort --profile black ./
	black ./