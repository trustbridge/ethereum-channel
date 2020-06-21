const HDWalletProvider = require("@truffle/hdwallet-provider");

function getEnv(name, defaultValue){
  const value === process.env[name] || defaultValue;
  if(value === undefined){
    throw Error('Missing "%s" environment variable');
  }
  return value;
}


const NETWORK_ID = getEnv('TRUFFLE_NETWORK_ID');
const WALLET_PK = getEnv('TRUFFLE_WALLET_PK');
const BLOCKCHAIN_ENDPOINT = getEnv('TRUFFLE_BLOCKCHAIN_ENDPOINT', null);



module.exports = {
  networks: {
    production:{
      network_id: NETWORK_ID,
      provider: ()=> HDWalletProvider([WALLET_PK], BLOCKCHAIN_ENDPOINT, 0)
    }
  }
}
