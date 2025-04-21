// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

struct CallbackSession {
    Node[] nodes;
    SessionStatus status;
}

struct Node {
    string endpoint;
    address pubKeyAddress;
    bytes result;
    bytes pubKey;
    bool isRevert;
    bool settled;
    
}

enum SessionStatus {
    Init,
    Pending,
    Running,
    Finished,
    Revert,
    Slash
}

// app is TEE-sim agnostic, so we don't need to specify TEE-sim
// the outpost is tied to a single cert manager, so we can't use both sim and nitro
enum ExecType {
    ER,
    TEESim,
    TEE
}