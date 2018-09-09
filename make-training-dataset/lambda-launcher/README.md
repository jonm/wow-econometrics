# Lambda launcher for make-training-dataset

The job for generating an ML training dataset runs as a one-shot EC2 launch
that installs the generation software on startup, runs the job, and then
terminates itself. We would like to be able to launch that job from a Lambda
function essentially running as a cron job to generate a new training
dataset every so often (e.g. weekly).

# Building the Lambda zip file

```
$ pip install -r requirements.txt -t .
$ cp ../ec2-userdata.sh.template .
$ python -m compileall .
$ rm -f lambda-launcher.zip; zip -r lambda-launcher.zip . -x \.* -x \*~
```

# Creating a role for the Lambda

The Lambda will need to be able to:
* read from the DynamoDB table `GLOBAL_TABLE_NAME`
* read from the DynamoDB table `INDEX_TABLE_NAME`
* launch an EC2 instance (RunInstances,CreateTags)
* assign the IAM role to the EC2 instance (PassRole)

# Creating the Lambda

```
$ aws lambda create-function \
  --function-name wowecon-make-training-dataset-launcher \
  --runtime python2.7 \
  --role arn:aws:iam::385198630581:role/wowecon-make-training-dataset-launcher \
  --handler handler.handle \
  --timeout 60 \
  --zip-file fileb://lambda-launcher.zip
```
