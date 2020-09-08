const os = require('os');
const fs = require('fs').promises;
const _ = require('lodash');
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');
const constants = require('./constants');

async function main(){
  logger.info('Started: self-test...');
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  const S3 = new AWS.S3();
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  const key = path.join(prefix, constants.CONTRACT_ARTIFACTS_KEY);
  const tmpDirectory = await fs.mkdtemp(path.join(os.tmpdir(),'deployer_'));
  logger.info('Created temp dir %s', tmpDirectory);
  try{
    await utils.S3.loadToFile(S3, process.env.CONTRACT_BUCKET_NAME, key, constants.CONTRACT_ARTIFACTS_ZIP_FILENAME);
    await utils.archive.unzip(constants.CONTRACT_ARTIFACTS_ZIP_FILENAME, tmpDirectory);
    logger.info('Deleting local build artifacts archive...');
    await fs.unlink(constants.CONTRACT_ARTIFACTS_ZIP_FILENAME);
    logger.info('Reading local and S3 files lists');
    const S3ArchiveFiles = await fs.readdir(tmpDirectory);
    const localArchiveFiles = await fs.readdir(constants.CONTRACT_BUILD_DIR);
    S3ArchiveFiles.sort();
    localArchiveFiles.sort();
    logger.info('S3=%O | local=%O', S3ArchiveFiles, localArchiveFiles);
    if(!_.isEqual(S3ArchiveFiles, localArchiveFiles)){
      throw new Error('local build artifacts and s3 build artifacts filename lists are not equal');
    }else{
      logger.info('local build artifacts and s3 build artifacts filename lists are equal');
    }
    for(const filename of S3ArchiveFiles){
      const localFilename = path.join(constants.CONTRACT_BUILD_DIR, filename);
      const S3Filename = path.join(tmpDirectory, filename);
      const localFile = await fs.readFile(localFilename);
      const S3File = await fs.readFile(S3Filename);
      if(!localFile.equals(S3File)){
        throw new Error(`S3 ${filename} != local ${filename}`);
      }else{
        logger.info(`S3 ${filename} = local ${filename}`);
      }
    }
  }catch(e){
    if(e.code == 'NoSuchKey'){
      throw Error(`bucket:${process.env.CONTRACT_BUCKET_NAME}//${key} not found`);
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
