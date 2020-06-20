const AWS = require('aws-sdk');
const Contract = artifacts.require(process.env.CONTRACT_ARTIFACT_NAME);

AWS.config.apiVersions = {
  s3: '2006-03-01'
};

module.exports = async function(done){
  try{
    const S3 = new AWS.S3();
    const contractInstance = await Contract.deployed();
    console.log(contractInstance.address);
  }catch(e){
    console.error(e);
  }
}
