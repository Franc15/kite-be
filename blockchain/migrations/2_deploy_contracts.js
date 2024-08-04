const ShipmentTracker = artifacts.require("ShipmentTracker");

module.exports = function(deployer) {
  deployer.deploy(ShipmentTracker);
};