// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

// Uncomment this line to use console.log
// import "hardhat/console.sol";


contract MockOutpost{

    function newSession(uint sessionId, bytes memory initialData) public {}

    function settle(address appAddress, uint256 sessionId, bool isRevert, bytes memory data) public {
        (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSettlement(uint256,bool,bytes)", sessionId, isRevert, data));
        require(success, "Call to appAddress failed");
    }
}
