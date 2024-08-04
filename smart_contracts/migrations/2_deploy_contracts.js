const OrderTracking = artifacts.require("OrderTracking");

module.exports = function(deployer) {
  deployer.deploy(OrderTracking);
};