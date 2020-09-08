#!/usr/bin/env bash

set -euo pipefail
echo "Creating resources..."
echo "Creating queues..."
awslocal sqs create-queue --queue-name "notifications" --output text > /dev/null
awslocal sqs create-queue --queue-name "delivery-outbox" --output text > /dev/null
awslocal sqs create-queue --queue-name "channel" --output text > /dev/null

awslocal sqs create-queue --queue-name queue-1 --output text
awslocal sqs create-queue --queue-name queue-2 --output text
awslocal sqs create-queue --queue-name queue-3 --output text
awslocal sqs create-queue --queue-name queue-4 --output text

echo "Done"
echo "Creating buckets..."
awslocal s3api create-bucket --bucket "subscriptions"
awslocal s3api create-bucket --bucket "contract"
echo "Done"
echo "Done"
awslocal sqs list-queues --output table
awslocal s3api list-buckets --output table
