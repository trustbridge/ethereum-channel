import os
import json
import boto3


def Contract(web3, config):
    if config.S3:
        s3 = boto3.resource('s3', endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))
        bucket = s3.Bucket(config.S3.Bucket)
        artifact = json.load(bucket.Object(config.S3.Key).get()['Body'])
        address = artifact['networks'][config.S3.NetworkId]['address']
        abi = artifact['abi']
    elif config.File:
        with open(config.File.Address, 'rt') as f:
            address = f.read()
        with open(config.File.ABI, 'rt') as f:
            abi = json.load(f)['abi']
    else:
        raise ValueError("Contract config.File and config.S3 sections are undefined")
    return web3.eth.contract(address=address, abi=abi)
