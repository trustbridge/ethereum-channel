const fs = require('fs').promises;
const path = require('path');
const AWS = require('aws-sdk');
const md5 = require('md5');


AWS.config.apiVersions = {
  s3: '2006-03-01'
};
AWS.config.endpoint = process.env.AWS_ENDPOINT_URL;

module.exports = async function(done){
  try{
    const S3 = new AWS.S3({s3ForcePathStyle:true});
    const Contract = artifacts.require(process.env.CONTRACT_ARTIFACT_NAME);
    const build_artifact_data = await fs.readFile(path.join(
      process.env.CONTRACT_BUILDS_DIR,
      process.env.CONTRACT_ARTIFACT_NAME+'.json'
    ));
    const build_artifact_json = JSON.parse(build_artifact_data);
    const contractInstance = await Contract.deployed();
    const contract_data = JSON.stringify(
      {
        abi: build_artifact_json.abi,
        address: contractInstance.address
      }
    );
    const contract_data_md5 = new Buffer(md5(contract_data), 'hex').toString('base64');
    const result = await S3.putObject({
      Body: contract_data,
      ContentMD5: contract_data_md5,
      ContentType: 'application/json',
      Bucket: process.env.CONTRACT_BUCKET_NAME,
      Key: process.env.CONTRACT_DATA_BUCKET_KEY
    }).promise();
    console.log('Saved');
    done();
  }catch(e){
    console.error(e);
    done();
  }
}
