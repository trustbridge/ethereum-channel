const path = require('path');

const CONTRACT_DEPLOYMENT_DIR = '/tmp/contract-deployment';
const CONTRACT_ARTIFACTS_ZIP_FILENAME = '/tmp/contract-deployment/build-artifacts.zip';
const CONTRACT_BUILD_DIR = path.join(CONTRACT_DEPLOYMENT_DIR, 'build/contracts');
const CONTRACT_ARTIFACTS_KEY = 'build-artifacts.zip';

module.exports = {
  CONTRACT_DEPLOYMENT_DIR,
  CONTRACT_BUILD_DIR,
  CONTRACT_ARTIFACTS_ZIP_FILENAME,
  CONTRACT_ARTIFACTS_KEY
}
