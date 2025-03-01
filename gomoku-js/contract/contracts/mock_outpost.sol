// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./app.sol";

// Uncomment this line to use console.log
// import "hardhat/console.sol";


contract MockOutpost{

    function newSession(uint sessionId, bytes memory initialData) public {}

    function callbackSession(address appAddress, uint256 sessionId, CallbackSession memory session) public {
        (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSession(uint256,(string,address,uint8))", sessionId, session));
        require(success, "Callback session failed");
    }

    function settle(address appAddress, uint256 sessionId, bool isRevert, bytes memory data) public {
        (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSettlement(uint256,bool,bytes)", sessionId, isRevert, data));
        require(success, "Call to appAddress failed");
    }

    function authIn(address account, uint256 sessionId) public {}

    function authOut(address account, uint256 sessionId) public {}
}