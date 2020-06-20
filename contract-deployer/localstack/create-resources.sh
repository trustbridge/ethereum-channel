#!/usr/bin/env bash

pwd
awslocal s3api create-bucket --bucket "contract"
awslocal s3api list-buckets --output table
