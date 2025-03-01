// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./template.sol";


contract APP is Template {
    // num => result
    mapping (uint256 => uint256) public fibonacci;
    // sessionId => num
    mapping (uint256 => uint256) public request;
    // num => bytes
    mapping (uint256 => bytes) public initialData;
    // num => sessionId
    mapping (uint256 => uint256) public sessionNum;

    constructor(address outpostAddress) Template(outpostAddress) {}

    function requestFib(uint256 num) public {
        request[nextSessionId] = num;

        bytes memory fibNumData = abi.encode(num);
        initialData[num] = fibNumData;
        sessionNum[num] = nextSessionId;

        newSession(fibNumData);
    }

    function processSettlementData(uint256 sessionId, bytes memory data) internal override {
        // TODO: add customised logic for settlement
        uint256 num = request[sessionId];
        fibonacci[num] = abi.decode(data, (uint256));
    }

    function getFibonacci(uint256 num) public view returns (uint256) {
        return fibonacci[num];
    }
}
