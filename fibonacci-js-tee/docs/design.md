# General Overview: Abstractions for Nitro Enclave Development

This project provides a set of abstractions designed to simplify the development of secure applications using AWS Nitro Enclaves. It aims to offer reusable components that handle the complexities of enclave communication and KMS interaction, allowing developers to focus on their core application logic. The key abstractions are:

1.  **Base Enclave Application:**

    *   **Purpose:** Provides a foundation for building enclave applications with built-in support for request handling, KMS operations, and communication with the parent instance.
    *   **Abstraction:** The `BaseEnclaveApp` (in `src/enclave/base_enclave_app.py`) provides:
        *   Automatic service creation and initialization
        *   Request routing and handling
        *   Cryptographic operations (signing, hashing)
        *   AWS credential management
        *   Attestation generation and handling
    *   **Key Features:**
        *   Automatic generation of unique enclave IDs
        *   Built-in support for health checks
        *   Standardized request/response handling
        *   Secure cryptographic operations
        *   AWS credential management
    *   **Developer Usage:**
        1.  Create a subclass of `BaseEnclaveApp`
        2.  Override `get_custom_handler()` to add custom endpoints
        3.  Implement custom request handlers for your endpoints
        4.  Use the built-in methods for cryptographic operations and attestation

2.  **Enclave Connector (Parent and Enclave Side):**

    *   **Purpose:** Manages the communication channel between the parent application (running on the EC2 instance) and the enclave application (running inside the Nitro Enclave).
    *   **Abstraction:** The `EnclaveConnector` (in `src/parent/enclave_connector.py` and `src/enclave/parent_connector.py`) provides an abstract base class with methods for:
        *   `send_request(request_data, timeout)`: Sends a request to the enclave.
        *   `wait_for_enclave(max_retries, retry_interval)`: Checks if the enclave is ready.
        *   `get_attestation()`: (Parent side) Retrieves the attestation document from the enclave.
        *   `start(request_handler)`: (Enclave side) Starts the server and listens for incoming requests.
    *   **Implementations:**
        *   `SimulationConnector`: Uses HTTP for communication, suitable for local development and testing.
        *   `NitroConnector`: Uses VSOCK for communication, designed for deployment to a real Nitro Enclave environment.
    *   **Developer Usage (Parent Side):**
        1.  Import `create_connector` from `src/parent/enclave_connector.py`.
        2.  Call `connector = create_connector()` to get an instance of the appropriate connector based on the `ENV_SETUP` environment variable (SIM or NITRO).
        3.  Use `connector.send_request()` to send requests to the enclave.
        4.  Use `connector.wait_for_enclave()` to ensure the enclave is ready before sending requests.
        5.  Use `connector.get_attestation()` to obtain the enclave's attestation document for verification.
    *   **Developer Usage (Enclave Side):**
        1.  The `BaseEnclaveApp` automatically creates and configures the appropriate connector.
        2.  Define custom request handlers in your subclass.
        3.  The base class handles all the communication setup and routing.

3.  **KMS Service (Enclave Side):**

    *   **Purpose:** Provides an interface for interacting with AWS KMS from within the enclave, abstracting away the complexities of using `kmstool_enclave_cli`.
    *   **Abstraction:** The `KmsService` (in `src/enclave/kms_service.py`) provides an abstract base class with methods for:
        *   `init_crypto()`: Initializes cryptographic components and returns public key information
        *   `decrypt(ciphertext, key_id, region, credentials)`: Decrypts ciphertext using KMS.
        *   `generate_key(key_id, key_spec, region, credentials)`: Generates a data key using KMS.
        *   `generate_random(length, region, credentials)`: Generates random bytes using KMS.
        *   `generate_attestation(nonce, region, credentials)`: Generates an attestation document.
        *   `sign_data(data, region, credentials)`: Signs data using KMS or local cryptographic operations
        *   `update_credentials(credentials)`: Updates the AWS credentials used by the service.
    *   **Implementations:**
        *   `RealKmsService`: Uses `kmstool_enclave_cli` to interact with AWS KMS.
        *   `MockKmsService`: Provides a mock implementation for testing and development without requiring actual AWS credentials or KMS access.
    *   **Developer Usage:**
        1.  The `BaseEnclaveApp` automatically creates and configures the appropriate KMS service.
        2.  Use the built-in methods of `BaseEnclaveApp` for cryptographic operations:
            *   `sign_data()` for signing data
            *   `secure_hash()` for creating secure hashes
            *   `generate_attestation()` for attestation generation
        3.  Access the KMS service directly through `self.kms_service` if needed.

4. **Credential Management:**
    * The `BaseEnclaveApp` includes built-in AWS credential management:
        * `get_aws_credentials()`: Retrieves current AWS credentials
        * `update_aws_credentials()`: Updates credentials in both the app and KMS service
        * Secure logging of credential updates (masked values)
    * The `/set-credentials` endpoint is automatically handled by the base class
    * Credentials are securely stored and managed throughout the application lifecycle

**Overall Workflow for Developers:**

1.  **Enclave Application:**
    *   Create a subclass of `BaseEnclaveApp` in `apps/`
    *   Override `get_custom_handler()` to add custom endpoints
    *   Implement custom request handlers for your endpoints
    *   Use built-in methods for cryptographic operations and attestation
    *   The base class handles all the setup and communication

2.  **Parent Application:**
    *   Use `create_connector()` to get a connector instance.
    *   Use `connector.wait_for_enclave()` to ensure the enclave is ready.
    *   Use `connector.get_attestation()` to retrieve and verify the enclave's attestation document.
    *   Send AWS credentials to the enclave using the `/set-credentials` endpoint.
    *   Use `connector.send_request()` to send requests to the enclave's endpoints.

3.  **Environment Configuration:**
    *   Use the `ENV_SETUP` environment variable to switch between simulation (`SIM`) and Nitro Enclave (`NITRO`) environments.
    *   Provide necessary environment variables (e.g., `VSOCK_PORT`, `ENCLAVE_CID`, `ENCLAVE_HOST`, `ENCLAVE_PORT`, AWS credentials) for both parent and enclave applications.
    *   Set `DEBUG=true` for additional logging and development features.

**Benefits of this Design:**

*   **Modularity:** The connector and KMS service abstractions are independent and can be used separately.
*   **Testability:** The `SimulationConnector` and `MockKmsService` allow for easy testing without requiring a real Nitro Enclave or AWS credentials.
*   **Flexibility:** Developers can easily switch between simulation and Nitro Enclave environments by changing the `ENV_SETUP` variable.
*   **Extensibility:** Developers can create new implementations of the `EnclaveConnector` and `KmsService` interfaces to support different communication methods or KMS providers.
*   **Simplified Development:** The `BaseEnclaveApp` provides a solid foundation for building enclave applications, handling common functionality automatically.
*   **Clear Separation of Concerns**: The design clearly separates the concerns of communication (EnclaveConnector), KMS operations (KmsService), and application logic (BaseEnclaveApp).
*   **Security Best Practices:** Built-in support for secure credential management, cryptographic operations, and attestation.

This design provides a solid foundation for building secure applications with AWS Nitro Enclaves, allowing developers to leverage the security benefits of enclaves while minimizing the development overhead. 