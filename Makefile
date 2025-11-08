clean:
	rm -v *.html *.epub

veryclean: clean
	rm -rf img

prepare:
	pip install -r requirements.txt

run:
	python3 main.py

.PHONY: run clean veryclean