const EventEmitter = artifacts.require("EventEmitter");
const fs = require('fs').promises;
const path = require('path');

module.exports = async function(deployer) {
  const ADDRESS_DIR = path.join('.', 'address');
  const EVENT_EMITTER_ADDRESS_FILE = path.join(ADDRESS_DIR, 'EventEmitter.address');

  await fs.mkdir(ADDRESS_DIR, {recursive:true});

  await deployer.deploy(EventEmitter);
  await fs.writeFile(EVENT_EMITTER_ADDRESS_FILE, EventEmitter.address);
  console.log(`[EventEmitter address] ${EventEmitter.address} -> ${EVENT_EMITTER_ADDRESS_FILE}`);
};
