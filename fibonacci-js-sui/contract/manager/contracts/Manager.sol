// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "./util.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

struct RegisterProvider {
    string endpoint;
    address pubKeyAddress;
    bytes validatorPubKey;
    string nodeId;
    ExecType execType;
}

struct Provider {
    string endpoint;
    address pubKeyAddress;
    bytes validatorPubKey;
    string nodeId;
    string dockerURI;
    string dockerHash;
    bytes initialData;
    SessionStatus status;
    ExecType execType;
}


contract Manager is Initializable, OwnableUpgradeable {
    mapping(string => bool) public _erRegistered;
    mapping(string => bool) public _teeRegistered;
    Provider[] public _erProviders;
    Provider[] public _teeProviders;
    mapping(uint256 => mapping(string => mapping(uint256 => Provider[]))) public _appSessionBinding;  // chain_id => app_address => session_id => providers
    mapping(uint256 => mapping(string => mapping(uint256 => bool))) public _appSessionDone;  // chain_id => app_address => session_id => done
    mapping(address => bool) public bridgeAddress;  // address => bool

    event NewSession(uint256 indexed chainId, string appAddress, uint256 indexed sessionId, Provider[] providers);
    event BridgeStatusChanged(address indexed bridge, bool status);


    function initialize(address _owner) public initializer {
        __Ownable_init(_owner);
    }

    modifier onlyBridge() {
        require(bridgeAddress[msg.sender], "not allowed");
        _;
    }

    // TODO: fleet -> []ER
    // TODO: app in the target fleet, sepecified fleet
    function registerProvider(RegisterProvider memory provider) public {
        if (_erRegistered[provider.endpoint]) {
            // didn't revert if the provider already registered
            return;
        }
        
        // todo: staking
        Provider memory newAppProvider = Provider(
            provider.endpoint,
            provider.pubKeyAddress,
            provider.validatorPubKey,
            provider.nodeId,
            "",
            "",
            new bytes(0),
            SessionStatus.Init,
            provider.execType
        );
        Provider[] storage providers = _getProviderArray(provider.execType);
        providers.push(newAppProvider);
        mapping(string => bool) storage registered = _getRegisteredArray(provider.execType);
        registered[provider.endpoint] = true;
    }

    function registerProviders(RegisterProvider[] memory providers) public {
        for (uint i = 0; i < providers.length; i++) {
            registerProvider(providers[i]);
        }
    }

    function isRegistered(ExecType execType, string memory endpoint) public view returns (bool) {
        if (execType == ExecType.ER) {
            return _erRegistered[endpoint];
        } else {
            return _teeRegistered[endpoint];
        }
    }

    function unregisterProvider(ExecType execType, string[] memory endpoints) public onlyOwner {
        for (uint i = 0; i < endpoints.length; i++) {
            if (execType == ExecType.ER) {
                delete _erRegistered[endpoints[i]];
            } else if (execType == ExecType.TEE) {
                delete _teeRegistered[endpoints[i]];
            }
        }
    }

    function clear() public onlyOwner {
        for (uint i = 0; i < _erProviders.length; i++) {
            delete _erRegistered[_erProviders[i].endpoint];
        }
        delete _erProviders;
    }

    function setBridge(address bridge, bool status) public onlyOwner {
        bridgeAddress[bridge] = status;
        emit BridgeStatusChanged(bridge, status);
    }

    // bridge call to start a new session
    function newSession(uint256 chainId, string memory appAddress, uint256 sessionId, uint count, 
        string memory dockerURI, string memory dockerHash, bytes memory initialData, ExecType execType) public onlyBridge() {
        require(count < 10, "Max count is 10");
        require(_appSessionBinding[chainId][appAddress][sessionId].length == 0, "Session already exists");

        Provider[] memory selectedProviders = _getRandomProviders(count, execType);
        for (uint i = 0; i < selectedProviders.length; i++) {
            selectedProviders[i].dockerURI = dockerURI;
            selectedProviders[i].dockerHash = dockerHash;
            selectedProviders[i].initialData = initialData;
            _appSessionBinding[chainId][appAddress][sessionId].push(selectedProviders[i]);
        }
        emit NewSession(chainId, appAddress, sessionId, selectedProviders);
    }

    function availableProviders(ExecType execType) public view returns (uint) {
        return _getProviderArray(execType).length;
    }

    function releaseProvider(uint256 chainId, string memory appAddress, uint256 sessionId) public onlyBridge() {

        require(_appSessionDone[chainId][appAddress][sessionId] == false, "Session already gone");
        for (
            uint i = 0;
            i < _appSessionBinding[chainId][appAddress][sessionId].length;
            i++
        ) {
            Provider[] storage providers = _getProviderArray(_appSessionBinding[chainId][appAddress][sessionId][i].execType);
            providers.push(_appSessionBinding[chainId][appAddress][sessionId][i]);
        }
        _appSessionDone[chainId][appAddress][sessionId] = true;
    }

    function getSessionBinding(uint256 chainId, string memory appAddress, uint256 sessionId) public view returns (Provider[] memory) {

        return _appSessionBinding[chainId][appAddress][sessionId];
    }

    function _getProviderArray(ExecType execType) internal view returns (Provider[] storage) {
        return execType == ExecType.ER ? _erProviders : _teeProviders;
    }

    function _getRegisteredArray(ExecType execType) internal view returns (mapping(string => bool) storage) {
        return execType == ExecType.ER ? _erRegistered : _teeRegistered;
    }

    function _getRandomProviders(uint amount, ExecType execType) internal returns (Provider[] memory selectedProviders) {
        Provider[] storage providers = _getProviderArray(execType);
        require(
            providers.length >= amount, 
            string.concat(
                "Not enough providers available. Required: ", 
                Strings.toString(amount), 
                ", Available: ", 
                Strings.toString(providers.length)
            )
        );
        
        selectedProviders = new Provider[](amount);
        uint currentLength = providers.length;
        
        for (uint i = 0; i < amount; i++) {
            uint randomIndex = uint(
                keccak256(
                    abi.encodePacked(block.timestamp, block.prevrandao, i)
                )
            ) % currentLength;
            
            selectedProviders[i] = providers[randomIndex];
            // Move the last element to the selected position
            providers[randomIndex] = providers[currentLength - 1];
            providers.pop();
            currentLength--;
        }
    }
}
