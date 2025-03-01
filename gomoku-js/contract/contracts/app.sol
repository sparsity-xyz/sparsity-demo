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
    struct Room {
        uint256 sessionId;
        address player1;
        address player2;
        bool isActive;
        address winner;
        address black;
        address white;
    }

    // Store all room information
    mapping(uint256 => Room) public rooms;
    // Track the room each player is in
    mapping(address => uint256) public playerRoom;
    // The current latest room ID
    uint256 public currentRoomId;

    OutpostInterface public _outpostContract;
    CallbackSession[] public _sessions;

    constructor(address outpostAddress) {
        _outpostContract = OutpostInterface(outpostAddress);
        currentRoomId = 0;
    }

    /**
     * @dev Join an existing room or create a new room
     * @return Returns the room ID
     */
    function joinOrCreateRoom() public returns (uint256) {
        require(playerRoom[msg.sender] == 0, "Player already in a room");

        if (currentRoomId > 0 && 
            rooms[currentRoomId].isActive && 
            rooms[currentRoomId].player2 == address(0)) {
            rooms[currentRoomId].player2 = msg.sender;
            playerRoom[msg.sender] = currentRoomId;
            authIn(currentRoomId);
            return currentRoomId;
        }
        
        currentRoomId++;
        Room memory room = Room({
            sessionId: currentRoomId,
            player1: msg.sender,
            player2: address(0),
            isActive: true,
            winner: address(0),
            black: address(0),
            white: address(0)
        });
        rooms[currentRoomId] = room;
        playerRoom[msg.sender] = currentRoomId;
        
        newSession(currentRoomId, abi.encode(room));
        authIn(currentRoomId);
        
        return currentRoomId;
    }

    /**
     * @dev Query the room a player is in
     * @param player The address of the player
     * @return The room ID (0 means the player is not in any room)
     */
    function getPlayerRoom(address player) public view returns (uint256) {
        return playerRoom[player];
    }

    /**
     * @dev Leave the current room
     */
    function leaveRoom() public {
        // leave is not allow for now
    }

    function getSession() public view returns (CallbackSession memory) {
        uint256 roomId = playerRoom[msg.sender];
        Room memory room = rooms[roomId];
        return _sessions[room.sessionId-1];
    }

    function getRoom(uint256 roomId) public view returns (Room memory) {
        return rooms[roomId];
    }

    /**
     * @dev Create a new game session
     */
    function newSession(uint256 sessionId, bytes memory initalData) internal {
        _sessions.push(CallbackSession("", address(0), SessionStatus.Init));
        _outpostContract.newSession(sessionId, initalData);
    }

    /**
     * @dev Outpost callback function: session creation completed
     */
    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        // the sessionId starts from 1
        _sessions[sessionId-1] = session;
    }

    /**
     * @dev Outpost callback function: session settlement
     */
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");

        if (isRevert) {
            // the sessionId starts from 1
            _sessions[sessionId-1].status = SessionStatus.Revert;
        } else {
            // the sessionId starts from 1
            _sessions[sessionId-1].status = SessionStatus.Finished;
            processSettlementData(sessionId, data);
        }
    }

    /**
     * @dev Player authentication to join the game
     */
    function authIn(uint256 sessionId) internal {
        _outpostContract.authIn(msg.sender, sessionId);
    }

    /**
     * @dev Player authentication to leave the game
     */
    function authOut(uint256 sessionId) internal {
        _outpostContract.authOut(msg.sender, sessionId);
    }

    /**
     * @dev Process settlement data
     */
    function processSettlementData(uint256 sessionId, bytes memory data) internal virtual {
        (address black, address white, address winner) = abi.decode(data, (address, address, address));
        uint256 roomId = sessionId;
        rooms[roomId].black = black;
        rooms[roomId].white = white;
        rooms[roomId].winner = winner;
        rooms[roomId].isActive = false;
        
        playerRoom[black] = 0;
        playerRoom[white] = 0;
    }
}
