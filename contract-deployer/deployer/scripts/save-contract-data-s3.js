const fs = require('fs').promises;
const path = require('path');
const AWS = require('aws-sdk');
const md5 = require('md5');
const pino = require('pino');

AWS.config.apiVersions = {
  s3: '2006-03-01'
};
AWS.config.endpoint = process.env.AWS_ENDPOINT_URL;


module.exports = async function(done){
  const logger = pino({level: process.env.LOG_LEVEL || 'info'});
  try{
    function checkRequiredEnvVars(requiredEnvVars){
      logger.info('Checking required environment variables...');
      for(const name of requiredEnvVars){
        if(process.env[name] === undefined){
          throw Error('missing required env variable "%s"')
        }else{
          logger.info('%s="%s"', name, process.env[name]);
        }
      }
      logger.info('Required environment variables are in place.')
    }
    checkRequiredEnvVars([
      'CONTRACT_ARTIFACT_NAME',
      'CONTRACT_BUILDS_DIR',
      'CONTRACT_ARTIFACT_NAME',
      'CONTRACT_BUCKET_NAME',
      'CONTRACT_DATA_BUCKET_KEY'
    ]);
    const S3 = new AWS.S3({s3ForcePathStyle:process.env.AWS_ENDPOINT_URL!==undefined});
    const Contract = artifacts.require(process.env.CONTRACT_ARTIFACT_NAME);
    const build_artifact_data_filename = path.join(
      process.env.CONTRACT_BUILDS_DIR,
      process.env.CONTRACT_ARTIFACT_NAME+'.json'
    )
    logger.info('Reading %s', build_artifact_data_filename);
    const build_artifact_data = await fs.readFile(build_artifact_data_filename);
    const build_artifact_json = JSON.parse(build_artifact_data);
    logger.info('Reading %s address', process.env.CONTRACT_ARTIFACT_NAME);
    const contractInstance = await Contract.deployed();
    const contract_data = JSON.stringify(
      {
        abi: build_artifact_json.abi,
        address: contractInstance.address
      }
    );
    logger.info('Contract file composed');
    const contract_data_md5 = new Buffer(md5(contract_data), 'hex').toString('base64');
    logger.info('Contract file md5 base64 %s', contract_data_md5);
    logger.info(
        'Saving contract to s3 bucket="%s", key="%s"',
        process.env.CONTRACT_BUCKET_NAME,
        process.env.CONTRACT_DATA_BUCKET_KEY
    );
    const result = await S3.putObject({
      Body: contract_data,
      ContentMD5: contract_data_md5,
      ContentType: 'application/json',
      Bucket: process.env.CONTRACT_BUCKET_NAME,
      Key: process.env.CONTRACT_DATA_BUCKET_KEY
    }).promise();
    logger.info('Saved');
    done();
  }catch(e){
    logger.error(e);
    done();
  }
}
