#!/bin/bash
awslocal s3 mb s3://temporary-document-bucket
awslocal s3 mb s3://permanent-document-bucket
awslocal s3api put-bucket-cors --bucket temporary-document-bucket --cors-configuration file:///etc/localstack/init/ready.d/cors.json
awslocal s3api put-bucket-cors --bucket permanent-document-bucket --cors-configuration file:///etc/localstack/init/ready.d/cors.json
