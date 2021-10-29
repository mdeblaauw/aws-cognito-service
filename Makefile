initiate_repo:
	python -m venv venv
	source venv/bin/active
	pip install -e lambda_utils/

tests:
	cd lambda_functions && coverage run -m unittest discover -s tests -p "test_*.py" -b
	cd lambda_utils && coverage run -m unittest discover -s tests -p "test_*.py" -b

coverage:
	cd lambda_functions && coverage run -m unittest discover -s tests -p "test_*.py" -b
	cd lambda_utils && coverage run -m unittest discover -s tests -p "test_*.py" -b
	coverage combine lambda_functions/.coverage lambda_utils/.coverage
	coverage html --skip-covered
	open htmlcov/index.html