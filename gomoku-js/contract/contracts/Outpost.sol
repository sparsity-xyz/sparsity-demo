// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

// Uncomment this line to use console.log
// import "hardhat/console.sol";
import "./util.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";


struct APPDocker {
    string dockerURI;
    string dockerHash;
}


contract Outpost is Initializable, OwnableUpgradeable {
    uint256 _id;
    mapping(address => uint256) public _appId;
    mapping(address => bool) public _appApproval;
    mapping(address => APPDocker) public _appDocker;
    mapping(address => mapping(uint256 => CallbackSession)) public _appSession;
    mapping(address => bool) public _approver;
    mapping(address => bool) public _bridgeAddress;

    event NewSession(address indexed appAddress, uint indexed sessionId, string dockerURI, string dockerHash, bytes initialData);
    event Settle(address indexed appAddress, uint indexed sessionId, bool indexed end);

    modifier onlyAPP() {
        require(_appApproval[msg.sender], "Caller is not the app");
        _;
    }

    modifier onlyApprover() {
        require(_approver[msg.sender], "not allowed");
        _;
    }

    modifier onlyBridge() {
        require(_bridgeAddress[msg.sender], "not allowed");
        _;
    }

    function initialize(address _owner) public initializer {
        __Ownable_init(_owner);
        _approver[_owner] = true;
    }
    
    function checkAuth(address appAddress, uint256 sessionId, address account) public view returns (bool) {        
        return APPInterface(appAddress).checkAuth(sessionId, account);
    }

    function registerAPP(address appAddress, string memory dockerURI, string memory dockerHash) public {
        require(_appApproval[appAddress] == false, "APP exists");
        _appDocker[appAddress] = APPDocker(dockerURI, dockerHash);
        _appId[appAddress] = _id;
        _id++;
    }

    function approveAPP(address appAddress) public onlyApprover {
        _appApproval[appAddress] = true;
    }

    function disapproveAPP(address appAddress) public onlyApprover {
        _appApproval[appAddress] = false;
    }

    function setApprover(address approver, bool status) public onlyOwner {
        _approver[approver] = status;
    }

    function setBridge(address bridge, bool status) public onlyOwner {
        _bridgeAddress[bridge] = status;
    }

    function newSession(uint sessionId, bytes memory initialData) public onlyAPP {
        require(_appApproval[msg.sender], "APP not exists");
        require(_appSession[msg.sender][sessionId].status == SessionStatus.Init, "SessionId exists");
        _appSession[msg.sender][sessionId].status = SessionStatus.Pending;
        emit NewSession(msg.sender, sessionId, _appDocker[msg.sender].dockerURI, _appDocker[msg.sender].dockerHash, initialData);
    }

    // callback by bridge
    function setAPPSession(address appAddress, uint256 sessionId, CallbackSession memory session) public onlyBridge {
        require(_appApproval[appAddress], "APP not exists");
        require(_appSession[appAddress][sessionId].status == SessionStatus.Pending, "Invalid session");
        session.status = SessionStatus.Running;
        _appSession[appAddress][sessionId] = session;
        // callback to app
        (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSession(uint256,(string,address,uint8))", sessionId, session));
        require(success, "Call to appAddress failed");
    }

    function getAPPSession(address appAddress, uint256 sessionId) public view returns (CallbackSession memory) {
        require(_appApproval[appAddress], "APP not exists");
        return _appSession[appAddress][sessionId];
    }

    function settle(address appAddress, uint256 sessionId, bool isRevert, bytes memory data) public {
        require(_appApproval[appAddress], "APP not exists");
        require(_appSession[appAddress][sessionId].publicKey == msg.sender, "Invalid session");
        require(_appSession[appAddress][sessionId].status == SessionStatus.Running, "Invalid session");
        if (isRevert == true) {
            _appSession[appAddress][sessionId].status = SessionStatus.Revert;
        } else {
            _appSession[appAddress][sessionId].status = SessionStatus.Finished;
        }

        // appAddress.call(abi.encodeWithSignature("callbackSettlement(uint256,bool,bytes)", sessionId, isRevert, data));
        (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSettlement(uint256,bool,bytes)", sessionId, isRevert, data));
        require(success, "Call to appAddress failed");

        emit Settle(appAddress, sessionId, true);
    }
}

interface APPInterface {
    function callbackSession(uint256 sessionId, CallbackSession memory session) external;
    function checkAuth(uint256 sessionId, address account) external view returns (bool);
    function settle(uint256 sessionId, bytes memory data) external;
}
