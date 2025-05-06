// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./util.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";


struct RegisterSession {
    string endpoint;
    address pubKeyAddress;
    bytes validatorPubKey;
    string nodeId;
}

struct ERSession {
    string endpoint;
    address pubKeyAddress;
    bytes validatorPubKey;
    string nodeId;
    string dockerURI;
    string dockerHash;
    bytes initialData;
    SessionStatus status;
}


contract Manager is Initializable, OwnableUpgradeable {
    mapping(string => bool) public _erRegistered;
    ERSession[] public _erSessions;
    mapping(uint256 => mapping(address => mapping(uint256 => ERSession[]))) public _appSessionBinding;  // chain_id => app_address => session_id => sessions
    mapping(uint256 => mapping(address => mapping(uint256 => bool))) public _appSessionDone;  // chain_id => app_address => session_id => done
    mapping(uint256 => mapping(address => bool)) public bridgeAddress;  // chain_id => address => bool

    event NewSession(uint256 indexed chainId, address indexed appAddress, uint256 indexed sessionId, ERSession[] session);
    event BridgeStatusChanged(uint256 indexed chainId, address indexed bridge, bool status);

    function initialize(address _owner) public initializer {
        __Ownable_init(_owner);
    }

    modifier onlyBridge(uint256 chainId) {
        require(bridgeAddress[chainId][msg.sender], "not allowed");
        _;
    }

    // TODO: fleet -> []ER
    // TODO: app in the target fleet, sepecified fleet
    function registerSession(RegisterSession memory session) public {
        if (_erRegistered[session.endpoint]) {
            // didn't revert if the session already registered
            return;
        }
        // todo: staking
        ERSession memory newAppSession = ERSession(
            session.endpoint,
            session.pubKeyAddress,
            session.validatorPubKey,
            session.nodeId,
            "",
            "",
            new bytes(0),
            SessionStatus.Init
        );
        _erSessions.push(newAppSession);
        _erRegistered[session.endpoint] = true;
    }

    function registerSessions(RegisterSession[] memory sessions) public {
        for (uint i = 0; i < sessions.length; i++) {
            registerSession(sessions[i]);
        }
    }

    function isRegistered(string memory endpoint) public view returns (bool) {
        return _erRegistered[endpoint];
    }

    function unregisterSession(string[] memory endpoints) public onlyOwner {
        for (uint i = 0; i < endpoints.length; i++) {
            delete _erRegistered[endpoints[i]];
        }
    }

    function clear() public onlyOwner {
        for (uint i = 0; i < _erSessions.length; i++) {
            delete _erRegistered[_erSessions[i].endpoint];
        }
        delete _erSessions;
    }

    function setBridge(uint256 chainId, address bridge, bool status) public onlyOwner {
        bridgeAddress[chainId][bridge] = status;
        emit BridgeStatusChanged(chainId, bridge, status);
    }

    // bridge call
    function newSession(uint256 chainId, address appAddress, uint256 sessionId, uint count, string memory dockerURI, string memory dockerHash, bytes memory initialData) public onlyBridge(chainId) {
        require(count < 10 && _erSessions.length >= count, "Amount must be less than 1");
        require(_appSessionBinding[chainId][appAddress][sessionId].length == 0, "Session already exists");

        ERSession[] memory selectedSession = _getRandomSession(count);
        for (uint i = 0; i < selectedSession.length; i++) {
            selectedSession[i].dockerURI = dockerURI;
            selectedSession[i].dockerHash = dockerHash;
            selectedSession[i].initialData = initialData;
            _appSessionBinding[chainId][appAddress][sessionId].push(selectedSession[i]);
        }
        emit NewSession(chainId, appAddress, sessionId, selectedSession);
    }

    function availableER() public view returns (uint) {
        return _erSessions.length;
    }

    function releaseER(uint256 chainId, address appAddress, uint256 sessionId) public onlyBridge(chainId) {
        require(_appSessionDone[chainId][appAddress][sessionId] == false, "Session already gone");
        for (
            uint i = 0;
            i < _appSessionBinding[chainId][appAddress][sessionId].length;
            i++
        ) {
            _erSessions.push(_appSessionBinding[chainId][appAddress][sessionId][i]);
        }
        _appSessionDone[chainId][appAddress][sessionId] = true;
    }

    function getSessionBinding(uint256 chainId, address appAddress, uint256 sessionId) public view returns (ERSession[] memory) {
        return _appSessionBinding[chainId][appAddress][sessionId];
    }

    // TODO: avoid the same session on same fleet
    function _getRandomSession(uint amount) internal returns (ERSession[] memory selectedSession) {
        require(_erSessions.length >= amount, "Not enough ER available");
        selectedSession = new ERSession[](amount);
        for (uint i = 0; i < amount; i++) {
            uint randomIndex = uint(
                keccak256(
                    abi.encodePacked(block.timestamp, block.prevrandao, i)
                )
            ) % _erSessions.length;
            selectedSession[i] = _erSessions[randomIndex];
            _erSessions[randomIndex] = _erSessions[
                _erSessions.length - 1
            ];
            _erSessions.pop();
        }
    }
}
