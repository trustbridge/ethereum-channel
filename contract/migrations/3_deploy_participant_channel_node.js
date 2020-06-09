const ChannelNode = artifacts.require("ChannelNode");

module.exports = function(deployer) {
  deployer.deploy(ChannelNode, ["JA"], {from: "0x2E5D4e4425f7D13A176665E50a9e87FD88400a30"});
};