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
    mapping(uint256 => bytes) public hashes;
    mapping(address => uint256) public playerSession;
    mapping(address => bool) public playerInChat;
    mapping(uint256 => address) sessionPlayer;
    uint256 nextSessionId;
    OutpostInterface public _outpostContract;
    CallbackSession[] public _sessions;

    constructor(address outpostAddress) {
        _outpostContract = OutpostInterface(outpostAddress);
    }

    function startChat() public {
        require(playerInChat[msg.sender] == false, "already in the session");
        uint256 sessionId = nextSessionId;
        playerSession[msg.sender] = sessionId;
        sessionPlayer[sessionId] = msg.sender;
        playerInChat[msg.sender] = true;
        
        _sessions.push(CallbackSession("", address(0), SessionStatus.Init));
        _outpostContract.newSession(sessionId, new bytes(0));

        nextSessionId ++;
    }

    function getSession(uint256 sessionId) public view returns (CallbackSession memory) {
        return _sessions[sessionId];
    }

    // implement function
    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        _sessions[sessionId] = session;
    }

    // implement function
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");

        if (isRevert) {
            _sessions[sessionId].status = SessionStatus.Revert;
        } else {
            _sessions[sessionId].status = SessionStatus.Finished;
            hashes[sessionId] = data;
        }
        playerInChat[sessionPlayer[sessionId]] = false;
    }

    // implement function
    function checkAuth(uint256 sessionId, address account) public view returns (bool) {
        return playerInChat[account] && sessionPlayer[sessionId] == account;
    }
}

