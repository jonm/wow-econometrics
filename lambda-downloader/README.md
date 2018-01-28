# Lambda Downloader

This pulls auction house data from the Blizzard Community API and stores it in S3.

## Building

```
$ pip install -r requirements.txt -t .
$ python -m compileall .
$ zip -r downloader.zip . -x \.* -x \*~
```
