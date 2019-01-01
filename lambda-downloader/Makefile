all: lambda-downloader.zip

.dep: requirements.txt
	pip install -r requirements.txt -t .
	touch .dep

lambda-downloader.zip: .dep handler.py battlenet.py downloader.py
	python -m compileall .
	rm -f lambda-downloader.zip
	zip -r lambda-downloader.zip . -x \.* -x \*~ -x Makefile

clean:
	rm -f *.pyc lambda-downloader.zip *~

distclean: clean
	rm -fr bin *.dist-info boto3 botocore certifi chardet concurrent
	rm -fr dateutil docutils idna jmespath requests s3transfer
	rm -fr six.py urllib3
	rm -f .dep

depend: .dep
