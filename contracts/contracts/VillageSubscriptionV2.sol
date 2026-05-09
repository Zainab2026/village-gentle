// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VillageSubscriptionV2 {
    address public owner;
    
    struct Subscription {
        uint256 expiryTimestamp;
        bool isActive;
    }
    
    // Mapping: User Address -> Feature ID -> Subscription
    mapping(address => mapping(uint256 => Subscription)) public subscriptions;
    
    // Plan durations in seconds
    uint256 constant WEEK = 7 days;
    uint256 constant MONTH = 30 days;
    uint256 constant YEAR = 365 days;
    
    // Plan prices in Wei
    uint256 public weeklyPrice = 0.1 ether; 
    uint256 public monthlyPrice = 0.3 ether;
    uint256 public yearlyPrice = 3 ether;
    
    event SubscriptionPurchased(address indexed user, uint256 indexed featureId, uint256 expiry, string planType);
    event SubscriptionCancelled(address indexed user, uint256 indexed featureId);
    
    constructor() {
        owner = msg.sender;
    }
    
    // New function to allow the app's wallet to pay for a user
    function purchaseSubscriptionFor(address user, uint256 featureId, uint256 planType) public payable {
        require(featureId == 1 || featureId == 2, "Invalid feature ID");
        
        uint256 duration;
        uint256 price;
        string memory planName;
        
        if (planType == 1) {
            duration = WEEK;
            price = weeklyPrice;
            planName = "Weekly";
        } else if (planType == 2) {
            duration = MONTH;
            price = monthlyPrice;
            planName = "Monthly";
        } else if (planType == 3) {
            duration = YEAR;
            price = yearlyPrice;
            planName = "Yearly";
        } else {
            revert("Invalid plan type");
        }
        
        require(msg.value >= price, "Insufficient payment");
        
        // Calculate new expiry
        Subscription storage sub = subscriptions[user][featureId];
        uint256 currentExpiry = sub.expiryTimestamp;
        uint256 newExpiry;
        
        if (currentExpiry > block.timestamp) {
            newExpiry = currentExpiry + duration;
        } else {
            newExpiry = block.timestamp + duration;
        }
        
        sub.expiryTimestamp = newExpiry;
        sub.isActive = true;
        
        emit SubscriptionPurchased(user, featureId, newExpiry, planName);
        
        // Refund excess payment to the sender (the app's wallet)
        if (msg.value > price) {
            payable(msg.sender).transfer(msg.value - price);
        }
    }
    
    function cancelSubscriptionFor(address user, uint256 featureId) public {
        require(msg.sender == owner || msg.sender == user, "Not authorized");
        subscriptions[user][featureId].expiryTimestamp = block.timestamp;
        subscriptions[user][featureId].isActive = false;
        emit SubscriptionCancelled(user, featureId);
    }
    
    function isSubscribed(address user, uint256 featureId) public view returns (bool) {
        return subscriptions[user][featureId].expiryTimestamp > block.timestamp;
    }
    
    function getSubscriptionDetails(address user, uint256 featureId) public view returns (bool, uint256) {
        return (isSubscribed(user, featureId), subscriptions[user][featureId].expiryTimestamp);
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Only owner can withdraw");
        payable(owner).transfer(address(this).balance);
    }
    
    function updatePrices(uint256 _weekly, uint256 _monthly, uint256 _yearly) public {
        require(msg.sender == owner, "Only owner can update prices");
        weeklyPrice = _weekly;
        monthlyPrice = _monthly;
        yearlyPrice = _yearly;
    }
}