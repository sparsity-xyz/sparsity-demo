// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./util.sol";


interface OutpostInterface {
    function newSession(uint256 sessionId, bytes memory initialData, ExecType execType) external;
}


interface APPInterface {
    // outpost will call the function when the session create success
    function callbackSession(uint256 sessionId, CallbackSession memory session) external; 
    // outpost will call the function when the session end
    function callbackSettlement(uint256 sessionId, bool isRevert, bool isSlash, bytes memory data) external;
    // outpost will call the function to check if the account is join the session and get the public key to verify the message
    function checkAuth(uint256 sessionId, address account) external view returns (bool, bytes memory);
}


contract APP is APPInterface {
    // for session management
    OutpostInterface public _outpostContract;
    CallbackSession[] public _sessions;
    uint256 public nextSessionId;

    // for customised logic
    mapping (uint256 => uint256) public fibonacci;
    mapping (uint256 => uint256) public request;

    constructor(address outpostAddress) {  
        _outpostContract = OutpostInterface(outpostAddress);
    }

    // entry point for the APP
    function requestFib(uint256 num, ExecType execType) public {
        request[nextSessionId] = num;

        bytes memory fibNumData = abi.encode(num);

        _sessions.push();

        // call outpost contract to create a new session
        _outpostContract.newSession(nextSessionId, fibNumData, execType);

        nextSessionId++;
    }

    // get the result of the fibonacci number
    function getFibonacci(uint256 num) public view returns (uint256) {
        return fibonacci[num];
    }

    // implement function
    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        require(sessionId < nextSessionId, "Session not exists");
        _sessions[sessionId].status = session.status;
        for (uint i = 0; i < session.nodes.length; i++) {
            _sessions[sessionId].nodes.push(session.nodes[i]);
        }
    }

    // implement function
    function callbackSettlement(uint256 sessionId, bool isRevert, bool isSlash, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        require(sessionId < nextSessionId, "sessionId not found");

        if (isRevert == true) {
            _sessions[sessionId].status = SessionStatus.Revert;
        } else {
            _sessions[sessionId].status = SessionStatus.Finished;
            uint256 num = request[sessionId];
            fibonacci[num] = abi.decode(data, (uint256));
        }

        if (isSlash == true) {
            _sessions[sessionId].status = SessionStatus.Slash;
        }
    }

    // implement function
    // we don't need to check the auth for this APP
    function checkAuth(uint256, address) public pure returns (bool, bytes memory) {
        return (true, new bytes(0));
    }
}
