// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ShipmentTracker {
    // Struct to store product information
    struct Product {
        uint id;
        string name;
        string owner;
        string description;
        string image;
    }

    // Struct to store order item information
    struct OrderItem {
        uint productId;
        uint quantity;
    }

    // Struct to store order information
    struct Order {
        uint id;
        string from;
        string to;
        uint256 timestamp;
        string status;
    }

    // Struct to store shipment information
    struct Shipment {
        uint id;
        uint[] orderIds;
        string status;
        uint256 timestamp;
    }

    // Struct to store asset information
    struct Asset {
        uint id;
        string owner;
        string description;
        string serialNumber;
        string image;
        string status;
    }

    // Struct to store movement history information
    struct Movement {
        uint timestamp;
        string from;
        string to;
        string status;
    }

    // Mappings to store products, orders, shipments, and assets
    mapping(uint => Product) public products;
    mapping(uint => Order) public orders;
    mapping(uint => Shipment) public shipments;
    mapping(uint => Asset) public assets;
    mapping(uint => OrderItem[]) public orderItems; // Mapping for storing order items
    mapping(uint => Movement[]) public productMovements; // Mapping for storing product movements

    // Counters to keep track of the number of products, orders, shipments, and assets
    uint public productCount;
    uint public orderCount;
    uint public shipmentCount;
    uint public assetCount;

    // Events to be emitted when a product, order, shipment, or asset is added or updated
    event ProductAdded(uint id, string name, string description);
    event OrderAdded(uint id, string from, string to, uint256 timestamp, string status);
    event OrderUpdated(uint id, string status);
    event OrderItemAdded(uint orderId, uint productId, uint quantity);
    event ShipmentAdded(uint id, uint[] orderIds, string status, uint256 timestamp);
    event ShipmentUpdated(uint id, string status);
    event AssetAdded(uint id, string owner, string description, string status);
    event AssetUpdated(uint id, string status);
    event ProductMovementUpdated(uint productId, uint timestamp, string from, string to, string status);

    // Function to add a new product
    function addProduct(string memory _name, string memory _description, string memory _owner, string memory _image) public {
        productCount++;
        products[productCount] = Product(productCount, _name, _owner, _description, _image);
        emit ProductAdded(productCount, _name, _description);
    }

    // Function to add a new order
    function addOrder(string memory _from, string memory _to, string memory _status) public returns (uint) {
        orderCount++;
        orders[orderCount] = Order(orderCount, _from, _to, block.timestamp, _status);
        emit OrderAdded(orderCount, _from, _to, block.timestamp, _status);
        return orderCount;
    }

    // Function to add order items to an existing order
    function addOrderItems(uint _orderId, uint[] memory _productIds, uint[] memory _quantities) public {
        require(_orderId > 0 && _orderId <= orderCount, "Order ID is invalid");
        require(_productIds.length == _quantities.length, "Product IDs and quantities must match");

        // Adding items to the order
        for (uint i = 0; i < _productIds.length; i++) {
            orderItems[_orderId].push(OrderItem(_productIds[i], _quantities[i]));
            emit OrderItemAdded(_orderId, _productIds[i], _quantities[i]);
        }
    }

    // Function to get order items for a specific order
    function getOrderItems(uint _orderId) public view returns (OrderItem[] memory) {
        return orderItems[_orderId];
    }

    // Function to update the status of an order
    function updateOrder(uint _id, string memory _status) public {
        require(_id > 0 && _id <= orderCount, "Order ID is invalid");
        Order storage order = orders[_id];
        order.status = _status;
        emit OrderUpdated(_id, _status);
    }

    // Function to add a new shipment
    function addShipment(uint[] memory _orderIds, string memory _status) public {
        shipmentCount++;
        shipments[shipmentCount] = Shipment(shipmentCount, _orderIds, _status, block.timestamp);
        emit ShipmentAdded(shipmentCount, _orderIds, _status, block.timestamp);
    }

    // Function to update the status of a shipment
    function updateShipment(uint _id, string memory _status) public {
        require(_id > 0 && _id <= shipmentCount, "Shipment ID is invalid");
        Shipment storage shipment = shipments[_id];
        shipment.status = _status;
        emit ShipmentUpdated(_id, _status);
    }

    // Function to add a new asset
    function addAsset(string memory _owner, string memory _description, string memory _image, string memory _serialNumber, string memory _status) public {
        assetCount++;
        assets[assetCount] = Asset(assetCount, _owner, _description, _serialNumber, _image, _status);
        emit AssetAdded(assetCount, _owner, _description, _status);
    }

    // Function to update the status of an asset
    function updateAsset(uint _id, string memory _status) public {
        require(_id > 0 && _id <= assetCount, "Asset ID is invalid");
        Asset storage asset = assets[_id];
        asset.status = _status;
        emit AssetUpdated(_id, _status);
    }

    // Function to get shipments by order ID
    function getShipmentsByOrderId(uint _orderId) public view returns (Shipment[] memory) {
        uint shipmentCountForOrder;
        for (uint i = 1; i <= shipmentCount; i++) {
            for (uint j = 0; j < shipments[i].orderIds.length; j++) {
                if (shipments[i].orderIds[j] == _orderId) {
                    shipmentCountForOrder++;
                    break;
                }
            }
        }

        Shipment[] memory result = new Shipment[](shipmentCountForOrder);
        uint counter = 0;
        for (uint i = 1; i <= shipmentCount; i++) {
            for (uint j = 0; j < shipments[i].orderIds.length; j++) {
                if (shipments[i].orderIds[j] == _orderId) {
                    result[counter] = shipments[i];
                    counter++;
                    break;
                }
            }
        }
        return result;
    }

    // Function to update product ownership and status
    function updateProductMovement(uint _productId, string memory _from, string memory _to, string memory _status) public {
        require(_productId > 0 && _productId <= productCount, "Product ID is invalid");
        Product storage product = products[_productId];
        product.owner = _to;

        productMovements[_productId].push(Movement(block.timestamp, _from, _to, _status));
        emit ProductMovementUpdated(_productId, block.timestamp, _from, _to, _status);
    }

    // Function to get the movement history of a product
    function getProductMovements(uint _productId) public view returns (Movement[] memory) {
        return productMovements[_productId];
    }

    // Function to get all products by owner
    function getProductsByOwner(string memory _owner) public view returns (Product[] memory) {
        uint ownerProductCount = 0;
        for (uint i = 1; i <= productCount; i++) {
            if (keccak256(abi.encodePacked(products[i].owner)) == keccak256(abi.encodePacked(_owner))) {
                ownerProductCount++;
            }
        }

        Product[] memory result = new Product[](ownerProductCount);
        uint counter = 0;
        for (uint i = 1; i <= productCount; i++) {
            if (keccak256(abi.encodePacked(products[i].owner)) == keccak256(abi.encodePacked(_owner))) {
                result[counter] = products[i];
                counter++;
            }
        }
        return result;
    }
}
