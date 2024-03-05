#!/bin/bash
awslocal s3 mb s3://static-files
awslocal s3api put-bucket-cors --bucket static-files --cors-configuration file:///etc/localstack/init/ready.d/cors.json
