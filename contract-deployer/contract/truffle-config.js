// this config will not work in the current setup. Deployment script must replace it.

module.exports = {
  networks: {
    development: {
      host: "ec-cd-ganache-cli",
      port: 8585,             // Custom port
      network_id: 15,       // Custom network
      from: "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", // Account to send txs from (default: accounts[0])
      websockets: true        // Enable EventEmitter interface for web3 (default: false)
    }
  }
}
