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
    function checkAuth(uint256 sessionId, address account) external view returns (bool, bytes memory);
}

contract APP is APPInterface {
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
    mapping(address => bytes) public playerPubKey;

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
    function joinOrCreateRoom(bytes memory pubKey) public returns (uint256) {
        require(playerRoom[msg.sender] == 0, "Player already in a room");

        if (currentRoomId > 0 && 
            rooms[currentRoomId].isActive && 
            rooms[currentRoomId].player2 == address(0)) {
            rooms[currentRoomId].player2 = msg.sender;
            playerRoom[msg.sender] = currentRoomId;
            playerPubKey[msg.sender] = pubKey;

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
        playerPubKey[msg.sender] = pubKey;
        
        _sessions.push();
        // call outpost contract to create a new session
        _outpostContract.newSession(currentRoomId, abi.encode(room));

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

    function updatePubKey(bytes memory pubKey) public {
        playerPubKey[msg.sender] = pubKey;
    }

    /**
     * @dev Outpost callback function: session creation completed
     */
    function callbackSession(uint256 sessionId, CallbackSession memory session) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        // the sessionId starts from 1
        _sessions[sessionId-1].status = session.status;
        for (uint i = 0; i < session.nodes.length; i++) {
            _sessions[sessionId-1].nodes.push(session.nodes[i]);
        }
    }

    /**
     * @dev Outpost callback function: session settlement
     */
    function callbackSettlement(uint256 sessionId, bool isRevert, bytes memory data) public {
        require(msg.sender == address(_outpostContract), "Only outpost contract can call this function");
        uint256 roomId = sessionId;

        if (isRevert) {
            // the sessionId starts from 1
            _sessions[sessionId-1].status = SessionStatus.Revert;
        } else {
            // the sessionId starts from 1
            _sessions[sessionId-1].status = SessionStatus.Finished;

            (address black, address white, address winner) = abi.decode(data, (address, address, address));
            rooms[roomId].black = black;
            rooms[roomId].white = white;
            rooms[roomId].winner = winner;
            rooms[roomId].isActive = false;
        }
        
        // release player
        playerRoom[rooms[roomId].black] = 0;
        playerRoom[rooms[roomId].white] = 0;
    }

    // check if the account is in the room
    function checkAuth(uint256 sessionId, address account) public view returns (bool, bytes memory) {
        return (rooms[sessionId].player1 == account || rooms[sessionId].player2 == account, playerPubKey[account]);
    }
}
