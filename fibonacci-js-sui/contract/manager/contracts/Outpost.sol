// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

// Uncomment this line to use console.log
import "hardhat/console.sol";
import "./util.sol";
import {APPInterface} from "./APP.sol";
import {INitroValidator} from "./interfaces/INitroValidator.sol";
import {PubKeyUtils} from "./libraries/PubKeyUtils.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";


struct APPSetting {
    string dockerURI;
    string dockerHash;
    uint count;
    // execution type 0=TEE, 1=ER
    ExecType execType;
}


contract Outpost is Initializable, OwnableUpgradeable {
    uint256 _id;
    mapping(address => uint256) public _appId;
    mapping(address => bool) public _appApproval;
    mapping(address => APPSetting) public _appSetting;
    mapping(address => mapping(uint256 => CallbackSession)) public _appSession;
    mapping(address => bool) public _approver;
    mapping(address => bool) public _bridgeAddress;
    mapping(address => mapping(uint256 => bool)) public _execVerified;
    INitroValidator public nitroValidator;
    bool public _approvalCheck;

    event NewSession(uint256 indexed chainId, address indexed appAddress, 
        uint indexed sessionId, uint count, string dockerURI, string dockerHash, 
        bytes initialData, ExecType execType);
    event Settle(uint256 indexed chainId, address indexed appAddress, 
        uint indexed sessionId, bool end, address validator);
    event CallFailedWithReason(address indexed appAddress, uint256 indexed sessionId, bytes reason);


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
    
    function checkAuth(address appAddress, uint256 sessionId, address account) public view returns (bool, bytes memory) {
        return APPInterface(appAddress).checkAuth(sessionId, account);
    }

    function registerAPP(address appAddress, uint count, uint8 execType, string memory dockerURI, string memory dockerHash) public {
        require(_appApproval[appAddress] == false, "APP already registered");
        _appSetting[appAddress] = APPSetting(dockerURI, dockerHash, count, ExecType(execType));
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

    function newSession(uint sessionId, bytes memory initialData, ExecType execType) public {
        if (_approvalCheck) {
            require(_appApproval[msg.sender], "APP not exists");
        }
        require(_appSession[msg.sender][sessionId].status == SessionStatus.Init, "SessionId exists");
        require(bytes(_appSetting[msg.sender].dockerURI).length != 0, "DockerURI does not exist");
        _appSession[msg.sender][sessionId].status = SessionStatus.Pending;
        emit NewSession(
            block.chainid, 
            msg.sender, 
            sessionId, 
            _appSetting[msg.sender].count, 
            _appSetting[msg.sender].dockerURI, 
            _appSetting[msg.sender].dockerHash, 
            initialData, 
            execType
        );
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
        try APPInterface(appAddress).callbackSession(sessionId, session){
            
        } 
        catch (bytes memory reason) {
            emit CallFailedWithReason(appAddress, sessionId, reason);
        }
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
            try APPInterface(appAddress).callbackSettlement(sessionId, allRevert, slash, allResult){
            }
            catch (bytes memory reason) {
                emit CallFailedWithReason(appAddress, sessionId, reason);
            }
        }

        emit Settle(block.chainid, appAddress, sessionId, end, msg.sender);
    }

    // tee functionalities

    function settleTEE(address appAddress, uint256 sessionId, bool isRevert, bytes memory data, bytes memory signature) public {
        Node[] memory nodes = _appSession[appAddress][sessionId].nodes;

        require(_appSession[appAddress][sessionId].status == SessionStatus.Running, "Invalid session");
        bytes memory sessionPubKey = _appSession[appAddress][sessionId].nodes[0].pubKey;
        
        // Calculate message hash directly from the data bytes
        bytes32 messageHash = keccak256(data);
        require(PubKeyUtils.verifySignature(messageHash, signature, sessionPubKey), "Invalid signature");

        nodes = _appSession[appAddress][sessionId].nodes;
        // allow only the first node in the registered session to settle for now
        Node memory node = nodes[0];
        node.isRevert = isRevert;
        node.result = data;
        node.settled = true;

        if (isRevert) {
            _appSession[appAddress][sessionId].status = SessionStatus.Revert;
        } else {
            _appSession[appAddress][sessionId].status = SessionStatus.Finished;
        }

        // TEE doesn't have immediate slashing on settlement
        try APPInterface(appAddress).callbackSettlement(sessionId, node.isRevert, false, node.result){
        } catch (bytes memory reason) {
            emit CallFailedWithReason(appAddress, sessionId, reason);
        }

        emit Settle(block.chainid, appAddress, sessionId, true, msg.sender);
    }

    function registerNitroValidator(address validator) public onlyOwner {
        nitroValidator = INitroValidator(validator);
    }

    function decodeAndValidateAttestation(bytes memory attestation) public returns (INitroValidator.Ptrs memory) {
        (bytes memory attestationTbs, bytes memory signature) = nitroValidator.decodeAttestationTbs(attestation);
        return nitroValidator.validateAttestation(attestationTbs, signature);
    }

    function verifyExec(address appAddress, uint256 sessionId, bytes memory attestation) public {
        // require app is registered as TEE app
        require(_appSetting[appAddress].execType == ExecType.TEE || 
        _appSetting[appAddress].execType == ExecType.TEESim, "App is not a TEE app");

        // validate attestation: no error will mean valid certificates
        // TODO: should use validateAttestation instead for efficiency
        INitroValidator.Ptrs memory ptrs = decodeAndValidateAttestation(attestation);

        _appSession[appAddress][sessionId].nodes[0].pubKey = PubKeyUtils.extractPublicKeyFromCbor(attestation, ptrs.publicKey);

        // TODO: validate PCR values after attestation validation

        // set verified flag for the app session
        _execVerified[appAddress][sessionId] = true;
    }

    function verifySignatureTest(bytes memory data, bytes memory signature, bytes memory attestation) public returns (bool) {
        // Calculate the message hash from the data
        bytes32 messageHash = keccak256(data);
        
        // Get the public key from the attestation
        INitroValidator.Ptrs memory ptrs = decodeAndValidateAttestation(attestation);
        bytes memory publicKey = PubKeyUtils.extractPublicKeyFromCbor(attestation, ptrs.publicKey);
        
        // Verify the signature using PubKeyUtils
        require(PubKeyUtils.verifySignature(messageHash, signature, publicKey), "Invalid signature");
        
        return true;
    }
}