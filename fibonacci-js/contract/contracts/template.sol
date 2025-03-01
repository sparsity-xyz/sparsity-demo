// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;


interface OutpostInterface {
    function newSession(uint256 sessionId, bytes memory initialData) external;
    function authIn(address account, uint256 sessionId) external;
    function authOut(address account, uint256 sessionId)  external;
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
    // outpost will call the function when the session create success
    function callbackSession(uint256 sessionId, CallbackSession memory session) external; 
    // outpost will call the function when the session end
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) external;
}


contract Template {
    OutpostInterface public _outpostContract;
    CallbackSession[] public _sessions;
    uint256 public nextSessionId;

    constructor(address outpostAddress) {  
        _outpostContract = OutpostInterface(outpostAddress);
    }
    
    // initalData is the encoded data for ABCI inital
    function newSession(bytes memory initalData) internal {
        _sessions.push(CallbackSession("", address(0), SessionStatus.Init));

        // call outpost contract to create a new session
        _outpostContract.newSession(nextSessionId, initalData);

        nextSessionId++;
    }

    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        require(sessionId < nextSessionId, "Session not exists");
        _sessions[sessionId] = session;
    }

    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        require(sessionId < nextSessionId, "sessionId not found");

        if (isRevert == true) {
            _sessions[sessionId].status = SessionStatus.Revert;
        } else {
            _sessions[sessionId].status = SessionStatus.Finished;
            processSettlementData(sessionId, data);        
        }
    }
    
    // user want to auth in/out, they need to call this function
    function authIn(uint256 sessionId) internal {
        require(sessionId < nextSessionId, "Session not exists");
        _outpostContract.authIn(msg.sender, sessionId);
    }

    // user want to auth in/out, they need to call this function
    function authOut(uint256 sessionId) internal {
        require(sessionId < nextSessionId, "Session not exists");
        _outpostContract.authOut(msg.sender, sessionId);
    }

    function processSettlementData(uint256 sessionId, bytes memory data) internal virtual {
        // TODO: add customised logic for settlement
    }
}
