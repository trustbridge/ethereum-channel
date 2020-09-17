#!/usr/bin/env bash

set -euo pipefail
echo "Creating resources..."
echo "Creating queues..."

awslocal sqs create-queue --queue-name "notifications-gb" --output text > /dev/null
awslocal sqs create-queue --queue-name "delivery-outbox-gb" --output text > /dev/null
awslocal sqs create-queue --queue-name "channel-gb" --output text > /dev/null

awslocal sqs create-queue --queue-name "notifications-au" --output text > /dev/null
awslocal sqs create-queue --queue-name "delivery-outbox-au" --output text > /dev/null
awslocal sqs create-queue --queue-name "channel-au" --output text > /dev/null

echo "Done"
echo "Creating buckets..."
awslocal s3api create-bucket --bucket "subscriptions-gb"
awslocal s3api create-bucket --bucket "subscriptions-au"
awslocal s3api create-bucket --bucket "contract"
echo "Done"
echo "Done"
awslocal sqs list-queues --output table
awslocal s3api list-buckets --output table
