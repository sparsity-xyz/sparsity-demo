// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./util.sol";

interface OutpostInterface {
    function newSession(uint256 sessionId, bytes memory initialData) external;
}


interface APPInterface {
    // outpost will call the function when the session create success
    function callbackSession(uint256 sessionId, CallbackSession memory session) external; 
    // outpost will call the function when the session end
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) external;
    // outpost will call the function to check if the account is join the session
    function checkAuth(uint256 sessionId, address account) external view returns (bool);
}


contract APP is APPInterface {
        // for session management
    OutpostInterface public _outpostContract;
    CallbackSession[] public _sessions;
    uint256 public nextSessionId;

    // for customised logic
    // num => result
    mapping (uint256 => uint256) public fibonacci;
    // sessionId => num
    mapping (uint256 => uint256) public request;
    // num => bytes
    mapping (uint256 => bytes) public initialData;
    // num => sessionId
    mapping (uint256 => uint256) public sessionNum;

    constructor(address outpostAddress) {  
        _outpostContract = OutpostInterface(outpostAddress);
    }

    function requestFib(uint256 num) public {
        request[nextSessionId] = num;

        bytes memory fibNumData = abi.encode(num);
        initialData[num] = fibNumData;
        sessionNum[num] = nextSessionId;

        _sessions.push(CallbackSession("", address(0), SessionStatus.Init));

        // call outpost contract to create a new session
        _outpostContract.newSession(nextSessionId, fibNumData);

        nextSessionId++;
    }

    function getFibonacci(uint256 num) public view returns (uint256) {
        return fibonacci[num];
    }

        // implement function
    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        require(sessionId < nextSessionId, "Session not exists");
        _sessions[sessionId] = session;
    }

    // implement function
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        require(sessionId < nextSessionId, "sessionId not found");

        if (isRevert == true) {
            _sessions[sessionId].status = SessionStatus.Revert;
        } else {
            _sessions[sessionId].status = SessionStatus.Finished;
            uint256 num = request[sessionId];
            fibonacci[num] = abi.decode(data, (uint256));
        }
    }

    // implement function
    // we don't need to check the auth for this APP
    function checkAuth(uint256 sessionId, address account) public view returns (bool) {
        return true;
    }
}
