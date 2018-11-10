all: lambda-batch-summary.zip

.dep: requirements.txt
	pip install -r requirements.txt -t .
	touch .dep

lambda-batch-summary.zip: .dep handler.py summarize.py
	python -m compileall .
	rm -f lambda-batch-summary.zip
	zip -r lambda-batch-summary.zip . -x \.* -x \*~

depend: .dep
