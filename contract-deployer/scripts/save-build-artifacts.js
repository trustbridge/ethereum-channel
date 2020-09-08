const fs = require('fs').promises;
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');
const constants = require('./constants');


async function main(){
  logger.info('Started: save-build-artifacts...');
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  await utils.archive.zip(constants.CONTRACT_BUILD_DIR, constants.CONTRACT_ARTIFACTS_ZIP_FILENAME);
  const S3 = new AWS.S3()
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  const key = path.join(prefix, constants.CONTRACT_ARTIFACTS_KEY);
  await utils.S3.saveFile(S3, constants.CONTRACT_ARTIFACTS_ZIP_FILENAME, process.env.CONTRACT_BUCKET_NAME, key);
  logger.info('Deleting local build artifacts archive...');
  await fs.unlink(constants.CONTRACT_ARTIFACTS_ZIP_FILENAME);
  logger.info('Deleted');
  logger.info('Done');
}

module.exports = async function(done){
  try{
    await main();
    done();
  }catch(e){
    logger.error(e);
    process.exit(1);
  }
}
