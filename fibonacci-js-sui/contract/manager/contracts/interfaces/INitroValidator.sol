// SPDX-License-Identifier: MIT
pragma solidity ^0.8.15;

import {ICertManager} from "./ICertManager.sol";
import {CborElement} from "../libraries/CborDecode.sol";

interface INitroValidator {
    struct Ptrs {
        CborElement moduleID;
        uint64 timestamp;
        CborElement digest;
        CborElement[] pcrs;
        CborElement cert;
        CborElement[] cabundle;
        CborElement publicKey;
        CborElement userData;
        CborElement nonce;
    }

    /**
     * @notice Decodes the attestation TBS (To Be Signed) data and signature from a raw attestation
     * @param attestation The raw attestation data
     * @return attestationTbs The decoded attestation TBS data
     * @return signature The extracted signature
     */
    function decodeAttestationTbs(bytes memory attestation)
        external
        pure
        returns (bytes memory attestationTbs, bytes memory signature);

    /**
     * @notice Validates an attestation by verifying its signature and certificate chain
     * @param attestationTbs The attestation TBS data
     * @param signature The signature to verify
     * @return Parsed attestation data in the form of Ptrs struct
     */
    function validateAttestation(bytes memory attestationTbs, bytes memory signature) external returns (Ptrs memory);

    /**
     * @notice Returns the certificate manager contract address
     * @return The ICertManager implementation address
     */
    function certManager() external view returns (ICertManager);

}