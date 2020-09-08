const fs = require('fs').promises;
const {exec} = require('child_process');
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
  archive:{
    zip: async function(dirname, out){
      logger.info(`Zipping "${dirname}" into "${out}..."`);
      return new Promise(function(resolve, reject){
        exec(`zip -rj0 ${out} ${dirname}`, function(err, stdout, stderr){
          if(err){reject(err); return}
          if(stderr){reject(stderr); return}
          logger.info(`Zipped "${dirname}" into "${out}"`);
          resolve();
        });
      });
    },
    unzip: async function(filename, out){
      logger.info(`Unzipping "${filename}" into "${out}..."`);
      return new Promise(function(resolve, reject){
        exec(`unzip -o ${filename} -d ${out}`, function(err, stdout, stderr){
          if(err){reject(err); return}
          if(stderr){reject(stderr); return}
          logger.info(`Unzipped "${filename}" into "${out}"`);
          resolve();
        });
      });
    }
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
