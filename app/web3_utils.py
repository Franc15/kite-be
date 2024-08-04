# app/web3_utils.py
from web3 import Web3
import json

class Web3Utils:
    def __init__(self, provider_uri, contract_address, contract_abi_path):
        self.w3 = Web3(Web3.HTTPProvider(provider_uri))
        if not self.w3.is_connected():
            raise Exception("Web3 is not connected")

        self.contract_address = contract_address
        if not self.contract_address:
            raise Exception("Contract address is not configured")

        with open(contract_abi_path) as file:
            compiled_sol = json.load(file)

        self.abi = compiled_sol.get("abi")
        if not self.abi:
            raise Exception("ABI not found in the compiled contract")

        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
    
    def get_contract(self):
        return self.contract
    
    def get_web3(self):
        return self.w3

# Initialize the Web3Utils instance
web3_utils = Web3Utils(
    provider_uri='http://127.0.0.1:7545',  # You can use the config value here
    contract_address='0x2C56746513f59e68057BeeB856e8c3851504F480',  # You can use the config value here
    contract_abi_path='smart_contracts/build/contracts/OrderTracking.json'
)
