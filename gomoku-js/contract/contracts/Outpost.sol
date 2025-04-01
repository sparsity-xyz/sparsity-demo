// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

// Uncomment this line to use console.log
// import "hardhat/console.sol";
import "./util.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";


struct APPSetting {
    uint count;
    string dockerURI;
    string dockerHash;
}


contract Outpost is Initializable, OwnableUpgradeable {
    uint256 _id;
    mapping(address => uint256) public _appId;
    mapping(address => bool) public _appApproval;
    mapping(address => APPSetting) public _appSetting;
    mapping(address => mapping(uint256 => CallbackSession)) public _appSession;
    mapping(address => bool) public _approver;
    mapping(address => bool) public _bridgeAddress;
    bool public _approvalCheck;

    event NewSession(uint256 indexed chainId, address indexed appAddress, uint indexed sessionId, uint count, string dockerURI, string dockerHash, bytes initialData);
    event Settle(uint256 indexed chainId, address indexed appAddress, uint indexed sessionId, bool end, address validator);

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
    
    function checkAuth(address appAddress, uint256 sessionId, address account) public pure returns (bool, bytes memory) {
        return APPInterface(appAddress).checkAuth(sessionId, account);
    }

    function registerAPP(address appAddress, uint count, string memory dockerURI, string memory dockerHash) public {
        require(_appApproval[appAddress] == false, "APP exists");
        _appSetting[appAddress] = APPSetting(count, dockerURI, dockerHash);
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

    function setApproveCheck(bool status) public onlyOwner {
        _approvalCheck = status;
    }

    function newSession(uint sessionId, bytes memory initialData) public {
        if (_approvalCheck) {
            require(_appApproval[msg.sender], "APP not exists");
        }
        require(_appSession[msg.sender][sessionId].status == SessionStatus.Init, "SessionId exists");
        require(bytes(_appSetting[msg.sender].dockerURI).length != 0, "DockerURI does not exist");
        _appSession[msg.sender][sessionId].status = SessionStatus.Pending;
        emit NewSession(block.chainid, msg.sender, sessionId, _appSetting[msg.sender].count, _appSetting[msg.sender].dockerURI, _appSetting[msg.sender].dockerHash, initialData);
    }

    // callback by bridge
    function setAPPSession(address appAddress, uint256 sessionId, CallbackSession memory session) public onlyBridge {
        require(_appSession[appAddress][sessionId].status == SessionStatus.Pending, "Invalid session");
        session.status = SessionStatus.Running;
        _appSession[appAddress][sessionId].status = session.status;
        for (uint i = 0; i < session.nodes.length; i++) {
            _appSession[appAddress][sessionId].nodes.push(session.nodes[i]);
        }
        // just return if the app not exists
        // avoid when turning on the approvalCheck to fail the running session
        if (_approvalCheck && !_appApproval[appAddress]) {
            return;
        }
        // callback to app
        (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSession(uint256,((string,address,bytes,bool,bool)[],uint8))", sessionId, session));
        require(success, "Session callback to app failed");
    }

    function getAPPSession(address appAddress, uint256 sessionId) public view returns (CallbackSession memory) {
        return _appSession[appAddress][sessionId];
    }

    function settle(address appAddress, uint256 sessionId, bool isRevert, bytes memory data) public {
        bool allow = false;
        uint256 settleCount = 0;
        bool end = false;
        Node[] memory nodes = _appSession[appAddress][sessionId].nodes;

        for (uint256 i = 0; i < nodes.length; i++) {
            if (nodes[i].pubKeyAddress == msg.sender && !nodes[i].settled) {
                allow = true;
                _appSession[appAddress][sessionId].nodes[i].isRevert = isRevert;
                _appSession[appAddress][sessionId].nodes[i].result = data;
                _appSession[appAddress][sessionId].nodes[i].settled = true;
                break;
            }
        }

        require(allow, "Invalid pubkey");
        require(_appSession[appAddress][sessionId].status == SessionStatus.Running, "Invalid session");

        nodes = _appSession[appAddress][sessionId].nodes;

        for (uint256 i = 0; i < nodes.length; i++) {
            if (nodes[i].settled) {
                settleCount++;
            }
        }

        if (settleCount == nodes.length) {
            bool allRevert = nodes[0].isRevert;
            bool slash = false;
            bytes memory allResult = nodes[0].result;
            end = true;

            for (uint256 i = 1; i < nodes.length; i++) {
                if (allRevert != nodes[i].isRevert || keccak256(allResult) != keccak256(nodes[i].result)) {
                    slash = true;
                    break;
                }
            }

            if (slash) {
                _appSession[appAddress][sessionId].status = SessionStatus.Slash;
            } else if (allRevert) {
                _appSession[appAddress][sessionId].status = SessionStatus.Revert;
            } else {
                _appSession[appAddress][sessionId].status = SessionStatus.Finished;
            }

            if (_approvalCheck && !_appApproval[appAddress]) {
                return;
            }

            (bool success, ) = appAddress.call(abi.encodeWithSignature("callbackSettlement(uint256,bool,bool,bytes)", sessionId, allRevert, slash, allResult));
            require(success, "Session callback to app failed");
        }

        emit Settle(block.chainid, appAddress, sessionId, end, msg.sender);
    }
}

interface APPInterface {
    function callbackSession(uint256 sessionId, CallbackSession memory session) external;
    function checkAuth(uint256 sessionId, address account) external pure returns (bool, bytes memory);
    function settle(uint256 sessionId, bytes memory data) external;
}
