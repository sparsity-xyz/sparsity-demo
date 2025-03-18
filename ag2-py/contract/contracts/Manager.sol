// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./util.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";


struct RegisterSession {
    string endpoint;
    address publicKey;
}

struct ERSession {
    string endpoint;
    address publicKey;
    SessionStatus status;
    string dockerURI;
    string dockerHash;
    bytes initialData;
}


contract Manager is Initializable, OwnableUpgradeable {
    mapping(string => bool) public _erRegistered;
    ERSession[] public _erSessions;
    mapping(address => mapping(uint256 => ERSession[])) public _appSessionBinding;
    mapping(address => mapping(uint256 => bool)) public _appSessionDone;
    mapping(address => bool) public bridgeAddress;

    event NewSession(address indexed appAddress, uint256 indexed sessionId, ERSession[] session);

    function initialize(address _owner) public initializer {
        __Ownable_init(_owner);
    }

    modifier onlyBridge() {
        require(bridgeAddress[msg.sender], "not allowed");
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
            session.publicKey,
            SessionStatus.Init,
            "",
            "",
            new bytes(0)
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

    function unregisterSession() public {
        // TODO
    }

    function clear() public onlyOwner {
        for (uint i = 0; i < _erSessions.length; i++) {
            delete _erRegistered[_erSessions[i].endpoint];
        }
        delete _erSessions;
    }

    function setBridge(address bridge, bool status) public onlyOwner {
        bridgeAddress[bridge] = status;
    }

    // brige call
    function newSession(address appAddress, uint256 sessionId, string memory dockerURI, string memory dockerHash, bytes memory initialData) public onlyBridge {
        uint256 amount = 1;
        require(amount < 10 && _erSessions.length >= amount, "Amount must be less than 1");
        require(_appSessionBinding[appAddress][sessionId].length == 0, "Session already exists");

        ERSession[] memory selectedSession = _getRandomSession(amount);
        for (uint i = 0; i < selectedSession.length; i++) {
            selectedSession[i].dockerURI = dockerURI;
            selectedSession[i].dockerHash = dockerHash;
            selectedSession[i].initialData = initialData;
            _appSessionBinding[appAddress][sessionId].push(selectedSession[i]);
        }
        emit NewSession(appAddress, sessionId, selectedSession);
    }

    function availableER() public view returns (uint) {
        return _erSessions.length;
    }

    function releaseER(address appAddress, uint256 sessionId) public onlyBridge {
        require(_appSessionDone[appAddress][sessionId] == false, "Session already gone");
        for (
            uint i = 0;
            i < _appSessionBinding[appAddress][sessionId].length;
            i++
        ) {
            _erSessions.push(_appSessionBinding[appAddress][sessionId][i]);
        }
        _appSessionDone[appAddress][sessionId] = true;
    }

    function getSessionBinding(address appAddress, uint256 sessionId) public view returns (ERSession[] memory) {
        return _appSessionBinding[appAddress][sessionId];
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
