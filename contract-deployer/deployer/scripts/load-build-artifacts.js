const fs = require('fs').promises;
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');
const constants = require('./constants');

async function main(){
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  const S3 = new AWS.S3();
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  logger.info('Listing contract build artifacts, prefix="%s"', prefix);
  const buildArtifactObjects = await S3.listObjects({
    Bucket: process.env.CONTRACT_BUCKET_NAME,
    Prefix: prefix
  }).promise();
  if (!buildArtifactObjects.Contents){
    loggger.info('No objects found');
  }
  for(const object of buildArtifactObjects.Contents){
    logger.info('Found "%s" object', object.Key);
    const filename = path.join(constants.CONTRACT_BUILD_DIR, path.basename(object.Key));
    await utils.S3.loadToFile(S3, process.env.CONTRACT_BUCKET_NAME, object.Key, filename);
  }
  logger.info('Done');
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
