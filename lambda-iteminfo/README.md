# Lambda Iteminfo

This runs after downloading an hourly batch of auction info and prefetches
item info from the Blizzard Community API into DynamoDB. The current
integration has the S3 bucket where the auction batches get downloaded
publish a `PutObject` event into an SNS topic; this Lambda is subscribed
to that topic.

## Building

```
$ pip install -r requirements.txt -t .
$ python -m compileall .
$ zip -r lambda-iteminfo.zip . -x \.* -x \*~
```
