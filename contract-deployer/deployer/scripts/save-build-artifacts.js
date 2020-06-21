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
  logger.info('Reading contracts build artifacts in %s', process.env.CONTRACT_BUILDS_DIR);
  const buildArtifactFiles = await fs.readdir(process.env.CONTRACT_BUILDS_DIR);
  logger.info('Contracts build artifacts are:[%s]', buildArtifactFiles);
  const S3 = new AWS.S3();
  for(const basename of buildArtifactFiles){
    const filename = path.join(process.env.CONTRACT_BUILDS_DIR, basename);
    const prefix = process.env.CONTRACT_KEY_PREFIX || '';
    const key = path.join(prefix, basename);
    await utils.S3.saveFile(S3, filename, process.env.CONTRACT_BUCKET_NAME, key);
  }
  logger.info('Done');
}

module.exports = async function(done){
  try{
    await main();
    done();
  }catch(e){
    logger.error(e);
    done();
  }
}
