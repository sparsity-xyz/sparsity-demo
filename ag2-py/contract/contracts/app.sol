// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

interface OutpostInterface {
    function newSession(uint256 sessionId, bytes memory initialData) external;
    function authIn(address account, uint256 sessionId) external;
    function authOut(address account, uint256 sessionId) external;
}

enum SessionStatus {
    Init,
    Pending,
    Running,
    Finished,
    Revert
}

struct CallbackSession {
    string endpoint;
    address publicKey;
    SessionStatus status;
}

interface APPInterface {
    function callbackSession(uint256 sessionId, CallbackSession memory session) external;
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) external;
}


contract APP {
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
        newSession(sessionId, new bytes(0));
        _outpostContract.authIn(msg.sender, sessionId);
        nextSessionId ++;
    }

    function processSettlementData(uint256 sessionId, SessionStatus status, bytes memory data) internal {
        if (status == SessionStatus.Finished) {
            hashes[sessionId] = data;
        }
        playerInChat[sessionPlayer[sessionId]] = false;
    }

    function getSession(uint256 sessionId) public view returns (CallbackSession memory) {
        return _sessions[sessionId];
    }
    
    function newSession(uint256 sessionId, bytes memory initalData) internal {
        _sessions.push(CallbackSession("", address(0), SessionStatus.Init));
        _outpostContract.newSession(sessionId, initalData);
    }

    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        _sessions[sessionId] = session;
    }

    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");

        if (isRevert) {
            _sessions[sessionId].status = SessionStatus.Revert;
        } else {
            _sessions[sessionId].status = SessionStatus.Finished;
        }
        processSettlementData(sessionId, _sessions[sessionId].status, data);
    }
}

