# Lambda Batch Summary

This runs after downloading an hourly batch of auction info. This
collapses multiple records of the same item into one record recording
the total volume and lowest unit buyout price.

## Building

```
$ pip install -r requirements.txt -t .
$ python -m compileall .
$ zip -r lambda-batch-summary.zip . -x \.* -x \*~
```
