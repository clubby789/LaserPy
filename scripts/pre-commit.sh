pylint `find . -type f -name "*.py"|xargs`
python3 -m flake8 .
python3 -m pytest
