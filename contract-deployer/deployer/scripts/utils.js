const fs = require('fs').promises;
const path = require('path');
const md5 = require('md5');
const {logger} = require('./logging');

module.exports = {
  requireEnv: function(requiredEnvVarsNames){
    logger.info('Checking required environment variables...');
    for(const name of requiredEnvVarsNames){
      if(process.env[name] === undefined){
        throw Error('Missing required env variable "%s"')
      }else{
        logger.info('%s="%s"', name, process.env[name]);
      }
    }
    logger.info('Required environment variables are in place.')
  },
  S3: {
    saveFile: async function(S3, filename, bucket, key){
      logger.info('Saving "%s" to "%s" bucket under "%s" key...', filename, bucket, key);
      const filedata = await fs.readFile(filename);
      await S3.putObject({
        Body: filedata,
        ContentMD5: new Buffer(md5(filedata), 'hex').toString('base64'),
        Bucket: bucket,
        Key: key
      }).promise();
      logger.info('Saved');
    },
    loadToFile: async function(S3, bucket, key, filename){
      logger.info('Saving S3 object under key "%s" from bucket "%s" as file "%s"...', key, bucket, filename);
      logger.info('Loading file from S3...');
      const response = await S3.getObject({
        Bucket: bucket,
        Key: key
      }).promise();
      logger.info('Loaded. Saving file to FS...');
      const dirname = path.dirname(filename);
      await fs.mkdir(dirname, {recursive: true});
      await fs.writeFile(filename, response.Body);
      logger.info('Saved');
    }
  }
}
