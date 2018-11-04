#!/bin/bash

sudo yum update -y
source activate tensorflow_p27

# make the CA trust bundle appear in the place the TF library expects
# it to show up
sudo ln -s /etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt /etc/ssl/certs/ca-certificates.crt

