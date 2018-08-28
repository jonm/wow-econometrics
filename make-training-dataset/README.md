# make-training-data

This generates a CSV dataset to be used for machine learning.

## Building an egg and wheel file

```
$ python setup.py bdist_egg
$ wheel convert dist/*.egg
$ for f in *.whl; do
> aws s3 cp $f s3://wowecon-artifacts/make_training_dataset/$f
done
```

## Launching an instance

Populate the following environment variables:
* `MTD_VERSION`
* `GLOBAL_TABLE_NAME`
* `INDEX_TABLE_NAME`
* `SRC_BUCKET_NAME`
* `DST_BUCKET_NAME`
* `EARLIEST_DATASET`
* `LATEST_DATASET`

Then generate the instance userdata script via:
```
$ ./make-userdata.sh
```

Then launch the instance by, for example:
```
$ aws ec2 run-instances --image-id ami-0ff8a91507f77f867 \
    --key-name jonm-pc \
    --security-group-ids sg-0a1ea9bc1c9015fe1 \
    --subnet-id subnet-233deb55 \
    --user-data file://ec2-userdata.sh \
    --instance-type t2.micro \
    --iam-instance-profile Arn=arn:aws:iam::385198630581:instance-profile/wowecon-make-training-dataset
    
```

The image `ami-0ff8a91507f77f867` is "Amazon Linux AMI 2018.03.0 (HVM),
SSD Volume Type". 