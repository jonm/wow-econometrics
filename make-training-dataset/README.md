# make-training-data

This generates a CSV dataset to be used for machine learning.

## Building

```
$ pip install -r requirements.txt -t .
$ python -m compileall .
$ zip -r training.zip . -x \.* -x \*~
```
