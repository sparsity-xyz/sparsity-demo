// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;


struct CallbackSession {
    string endpoint;
    address publicKey;
    SessionStatus status;
}

enum SessionStatus {
    Init,
    Pending,
    Running,
    Finished,
    Revert
}
