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
