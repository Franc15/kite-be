// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OrderTracking {

    struct Order {
        uint id;
        address currentOwner;
        string status;
        History[] ownershipHistory;
    }

    struct History {
        address owner;
        string status;
        uint timestamp;
    }

    mapping(uint => Order) public orders;
    mapping(address => string) public addressToName;

    event OrderCreated(uint id, address owner);
    event OwnershipTransferred(uint id, address from, address to, string status);

    // Function to create a new order with an ID from the database
    function createOrder(uint _orderId) public {
        require(orders[_orderId].id == 0, "Order ID already exists");
        
        Order storage newOrder = orders[_orderId];
        newOrder.id = _orderId;
        newOrder.currentOwner = msg.sender;
        newOrder.status = "Created";
        newOrder.ownershipHistory.push(History(msg.sender, "Created", block.timestamp));

        emit OrderCreated(_orderId, msg.sender);
    }

    // Function to transfer ownership of an order
    function transferOwnership(uint _orderId, address _newOwner, string memory _status) public {
        require(orders[_orderId].id != 0, "Order does not exist");
        require(orders[_orderId].currentOwner == msg.sender, "Only the current owner can transfer ownership");
        
        Order storage order = orders[_orderId];
        order.currentOwner = _newOwner;
        order.status = _status;
        order.ownershipHistory.push(History(_newOwner, _status, block.timestamp));

        emit OwnershipTransferred(_orderId, msg.sender, _newOwner, _status);
    }

    // Function to retrieve the history of an order
    function getOrderHistory(uint _orderId) public view returns (History[] memory) {
        require(orders[_orderId].id != 0, "Order does not exist");
        return orders[_orderId].ownershipHistory;
    }

    // Function to retrieve the details of an order
    function getOrderDetails(uint _orderId) public view returns (Order memory) {
        require(orders[_orderId].id != 0, "Order does not exist");
        return orders[_orderId];
    }

    // Function to set the name for the caller's address
    function setName(string memory _name) public {
        addressToName[msg.sender] = _name;
    }

    // Function to get the name associated with an address
    function getName(address _addr) public view returns (string memory) {
        return addressToName[_addr];
    }

    // Function to get order history with names instead of addresses
    function getOrderHistoryWithNames(uint _orderId) public view returns (string[] memory) {
        require(orders[_orderId].id != 0, "Order does not exist");
        
        History[] memory history = orders[_orderId].ownershipHistory;
        string[] memory historyWithNames = new string[](history.length);
        
        for (uint i = 0; i < history.length; i++) {
            string memory ownerName = addressToName[history[i].owner];
            if (bytes(ownerName).length == 0) {
                ownerName = toAsciiString(history[i].owner);
            }
            historyWithNames[i] = string(abi.encodePacked(ownerName, " - ", history[i].status, " - ", uint2str(history[i].timestamp)));
        }
        
        return historyWithNames;
    }

    // Helper function to convert uint to string
    function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len;
        while (_i != 0) {
            k = k-1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }

    // Helper function to convert address to string
    function toAsciiString(address x) internal pure returns (string memory) {
        bytes memory s = new bytes(40);
        for (uint i = 0; i < 20; i++) {
            bytes1 b = bytes1(uint8(uint(uint160(x)) / (2**(8*(19 - i)))));
            bytes1 hi = bytes1(uint8(b) / 16);
            bytes1 lo = bytes1(uint8(b) - 16 * uint8(hi));
            s[2*i] = char(hi);
            s[2*i+1] = char(lo);
        }
        return string(s);
    }

    // Helper function to convert byte to char
    function char(bytes1 b) internal pure returns (bytes1 c) {
        if (uint8(b) < 10) return bytes1(uint8(b) + 0x30);
        else return bytes1(uint8(b) + 0x57);
    }
}
