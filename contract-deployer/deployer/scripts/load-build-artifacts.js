const fs = require('fs').promises;
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');


async function main(){
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME',
    'CONTRACT_BUILDS_DIR'
  ]);
  const S3 = new AWS.S3();
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  logger.info('Listing contract build artifacts, prefix="%s"', prefix);
  const buildArtifactObjects = await S3.listObjects({
    Bucket: process.env.CONTRACT_BUCKET_NAME,
    Prefix: prefix
  }).promise();
  for(const object of buildArtifactObjects.Contents){
    logger.info('Found "%s" object', object.Key);
    const filename = path.join(process.env.CONTRACT_BUILDS_DIR, object.Key);
    await utils.S3.loadToFile(S3, process.env.CONTRACT_BUCKET_NAME, object.Key, filename);
  }
}


module.exports = async function(done){
  try{
    await main();
    done()
  }catch(e){
    logger.error('%s', e);
    done()
  }
}
