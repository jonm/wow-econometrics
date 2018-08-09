# make-training-data

This generates a CSV dataset to be used for machine learning.

## Building Docker image on Windows

Use "Docker Quickstart Terminal" for running docker commands (installed
as part of Docker for Windows (non-professional)). Will require installing
Python for Windows and pip-installing `awscli`.

```
$ aws ecr get-login --no-include-email --region us-east-1
```

The above command will output a command line to run to log into the
ECR repository.

```
$ docker build -t wowecon/make-training-dataset .
$ docker tag wowecon/make-training-dataset:latest 385198630581.dkr.ecr.us-east-1.amazonaws.com/wowecon/make-training-dataset:latest
$ docker push 385198630581.dkr.ecr.us-east-1.amazonaws.com/wowecon/make-training-dataset:latest
```

