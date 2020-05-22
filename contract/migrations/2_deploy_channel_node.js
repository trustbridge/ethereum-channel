const ChannelNode = artifacts.require("ChannelNode");

module.exports = function(deployer) {
  deployer.deploy(ChannelNode, ["JB"], {from: "0x75B703d1EA18df823c1c618478EEDd51319a1392"});
};