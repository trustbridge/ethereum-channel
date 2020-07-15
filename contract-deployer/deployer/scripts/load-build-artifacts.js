const fs = require('fs').promises;
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');
const constants = require('./constants');

async function main(){
  logger.info('Started: load-build-artifacts...');
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  const S3 = new AWS.S3();
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  const key = path.join(prefix, constants.CONTRACT_ARTIFACTS_KEY);
  try{
    await utils.S3.loadToFile(S3, process.env.CONTRACT_BUCKET_NAME, key, constants.CONTRACT_ARTIFACTS_ZIP_FILENAME);
    await utils.archive.unzip(constants.CONTRACT_ARTIFACTS_ZIP_FILENAME, constants.CONTRACT_BUILD_DIR);
    logger.info('Deleting local build artifacts archive...');
    await fs.unlink(constants.CONTRACT_ARTIFACTS_ZIP_FILENAME);
    logger.info('Deleted');
  }catch(e){
    if(e.code == 'NoSuchKey'){
      logger.info('Contract build artifacts archive object does not exits');
    }else{
      throw e;
    }
  }
  logger.info('Done');
}


module.exports = async function(done){
  try{
    await main();
    done()
  }catch(e){
    logger.error('%s', e);
    process.exit(1);
  }
}
