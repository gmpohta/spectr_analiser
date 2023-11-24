build:
	python3 -m venv ./venv
	. venv/bin/activate; \
	pip install -r requirements; \
	pyinstaller --onefile spectr_analiser_main.py libwidgets.py myfunct.py