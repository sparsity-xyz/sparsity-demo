module sparsity::outpost {
    use sui::table::{Self, Table};
    use sui::event; // Import the event module

    // --- Error Codes ---
    const EAppNotApproved: u64 = 1; // Define the error code here
    const EAppNotFound: u64 = 2; // Add error for app not found
    const ESessionNotFound: u64 = 3; // Add error for session not found

    // --- Constants ---
    // Application status constants
    const PENDING: u8 = 0;
    const APPROVED: u8 = 1;
    const REJECTED: u8 = 2;

    // Session status constants
    const SESSION_IDLE: u8 = 0;
    const SESSION_ACTIVE: u8 = 1;
    const SESSION_SETTLED: u8 = 2;
    const SESSION_EXPIRED: u8 = 3;

    // Represents an application with its status
    public struct App has key, store { 
        id: UID,
        app_address: address,  // Store the application address
        app_state: address, // Store the application user registry
        count: u64,
        docker_uri: vector<u8>, 
        docker_hash: vector<u8>,
        status: u8,
    }

    // Represents a session and its current status
    public struct Session has key, store { 
        id: UID,
        status: u8,
        initial_data: vector<u8>,
        result_data: vector<u8>   
    }

    // Registry to keep track of all applications
    public struct AppRegistry has key, store {
        id: UID,
        apps: Table<address, App>,
        auto_approved: bool // New property: Auto approve apps on registration
    }

    // Registry to manage all sessions
    public struct AppSession has key, store {
        id: UID,
        sessions: Table<address, Table<u64, Session>>
    }

    // Admin capability to control privileged operations
    public struct AdminCap has key, store {
        id: UID
    }

    // --- Event Structs ---
    // Event emitted when an app is registered
    public struct AppRegistered has copy, drop {
        app_address: address,
        app_state: address,
        count: u64,
        docker_uri: vector<u8>,
        docker_hash: vector<u8>,
        initial_status: u8,
        auto_approved: bool
    }

    // Event emitted when an app's status changes
    public struct AppStatusUpdated has copy, drop {
        app_address: address,
        count: u64,
        docker_uri: vector<u8>,
        docker_hash: vector<u8>,
        new_status: u8
    }

    // Event emitted when a session is created
    public struct SessionCreated has copy, drop {
        app_address: address,
        session_id: u64,
        initial_data: vector<u8>,
        count: u64,
        docker_uri: vector<u8>,
        docker_hash: vector<u8>
    }

    // Event emitted when a session's status changes
    public struct SessionStatusUpdated has copy, drop {
        app_address: address,
        session_id: u64,
        new_status: u8
    }

    // Event emitted when the auto_approved flag changes
    public struct AutoApprovedUpdated has copy, drop {
        auto_approved: bool
    }

    // Initialize the contract by creating and sharing registries
    fun init(ctx: &mut TxContext) {
        let admin_cap = AdminCap {
            id: object::new(ctx)
        };
        let appRegistry = AppRegistry {
            id: object::new(ctx),
            apps: table::new(ctx),
            auto_approved: false // Initialize auto_approved to false
        };
        let appSession = AppSession {
            id: object::new(ctx),
            sessions: table::new(ctx)
        };
        
        // Transfer AdminCap to contract deployer
        transfer::transfer(admin_cap, tx_context::sender(ctx));
        transfer::share_object(appRegistry);
        transfer::share_object(appSession);
    }

    // Register a new application
    public entry fun register_app(
        registry: &mut AppRegistry, 
        app_address: address, 
        app_state: address,
        count: u64,
        docker_uri: vector<u8>,
        docker_hash: vector<u8>,
        ctx: &mut TxContext
    ) {
        let initial_status = if (registry.auto_approved) { APPROVED } else { PENDING };
        let app = App {
            id: object::new(ctx),
            app_address: app_address,
            app_state: app_state,   
            count: count,
            docker_uri: docker_uri,
            docker_hash: docker_hash,
            status: initial_status // Set status based on auto_approved flag
        };
        table::add(&mut registry.apps, app_address, app);

        // Emit AppRegistered event
        event::emit(AppRegistered {
            app_address: app_address,   
            app_state: app_state,
            count: count,
            docker_uri: docker_uri,
            docker_hash: docker_hash,
            initial_status: initial_status,
            auto_approved: registry.auto_approved
        });

        // If auto-approved, also emit the status update event for consistency
        if (registry.auto_approved) {
            event::emit(AppStatusUpdated {
                app_address: app_address,
                count: count,
                docker_uri: docker_uri,
                docker_hash: docker_hash,
                new_status: APPROVED
            });
        }
    }

    // Private helper function to update app status
    fun update_app_status(registry: &mut AppRegistry, address: address, new_status: u8) {
        assert!(table::contains(&registry.apps, address), EAppNotFound);
        let app = table::borrow_mut(&mut registry.apps, address);
        app.status = new_status;
        // Emit AppStatusUpdated event
        event::emit(AppStatusUpdated {
            app_address: address,       
            count: app.count,
            docker_uri: app.docker_uri,
            docker_hash: app.docker_hash,
            new_status: new_status
        });
    }

    // Extract core logic for updating a session instance
    fun update_session_instance(
        session: &mut Session,
        new_status: u8,
        result_data: vector<u8>
    ) {
        session.status = new_status;
        session.result_data = result_data;
    }

    // Update session status and emit event
    fun update_session_status(
        app_session: &mut AppSession, 
        app_address: address,
        session_id: u64,
        new_status: u8,
        result_data: vector<u8>
    ) {
        assert!(table::contains(&app_session.sessions, app_address), EAppNotFound);
        let sessions = table::borrow_mut(&mut app_session.sessions, app_address);
        assert!(table::contains(sessions, session_id), ESessionNotFound);

        let session = table::borrow_mut(sessions, session_id);
        update_session_instance(session, new_status, result_data);

        // Emit SessionStatusUpdated event
        event::emit(SessionStatusUpdated {
            app_address: app_address,
            session_id: session_id,
            new_status: new_status
        });
    }

    public entry fun approve_app(
        _: &AdminCap,
        registry: &mut AppRegistry, 
        address: address
    ) {
        update_app_status(registry, address, APPROVED)
    }

    public entry fun reject_app(
        _: &AdminCap,
        registry: &mut AppRegistry, 
        address: address
    ) {
        update_app_status(registry, address, REJECTED)
    }
    
    // Helper function to create a new Session instance
    fun create_session_instance(
        initial_status: u8,
        initial_data: vector<u8>,
        ctx: &mut TxContext
    ): Session {
        Session {
            id: object::new(ctx),
            status: initial_status,
            initial_data: initial_data,
            result_data: vector[] // Initialize empty vector for result_data
        }
    }

    // Create a new session for an application
    public entry fun create_session(
        registry: &AppRegistry,
        app_session: &mut AppSession, 
        app_address: address,
        session_id: u64,
        initial_data: vector<u8>,
        ctx: &mut TxContext
    ) {
        // Verify application exists and is approved
        assert!(table::contains(&registry.apps, app_address), EAppNotFound);
        let app = table::borrow(&registry.apps, app_address); 
        assert!(app.status == APPROVED, EAppNotApproved); 

        // Verify session doesn't already exist
        if (table::contains(&app_session.sessions, app_address)) {
            let sessions = table::borrow(&app_session.sessions, app_address);
            assert!(!table::contains(sessions, session_id), ESessionNotFound);
        };

        // Create the session instance using our helper function
        let session = create_session_instance(SESSION_IDLE, initial_data, ctx);
        
        // Create sessions table for the app if it doesn't exist
        if (!table::contains(&app_session.sessions, app_address)) {
            table::add(&mut app_session.sessions, app_address, table::new(ctx));
        };
        
        // Add session to the table
        let sessions = table::borrow_mut(&mut app_session.sessions, app_address);
        table::add(sessions, session_id, session);

        // Emit SessionCreated event
        event::emit(SessionCreated {
            app_address: app_address,
            session_id: session_id,
            initial_data: initial_data,
            count: app.count,
            docker_uri: app.docker_uri,
            docker_hash: app.docker_hash,
        });
    }

    public entry fun activate_session(
        _: &AdminCap,
        app_session: &mut AppSession, 
        app_address: address,      // Outer key
        session_id: u64          // Inner key
    ) {
        update_session_status(app_session, app_address, session_id, SESSION_ACTIVE, vector[])
    }   

    public entry fun settle_session(
        _: &AdminCap,
        app_session: &mut AppSession, 
        app_address: address,      // Outer key
        session_id: u64,         // Inner key
        data: vector<u8>
    ) {
        update_session_status(app_session, app_address, session_id, SESSION_SETTLED, data)
    }

    public entry fun expire_session(
        _: &AdminCap,
        app_session: &mut AppSession, 
        app_address: address,      // Outer key
        session_id: u64          // Inner key
    ) {
        update_session_status(app_session, app_address, session_id, SESSION_EXPIRED, vector[])
    }

    // Instead of returning a reference, return the actual values
    public fun get_app_info(registry: &AppRegistry, address: address): (address, u8) {
        assert!(table::contains(&registry.apps, address), EAppNotFound);
        let app = table::borrow(&registry.apps, address);
        (app.app_address, app.status)
    }

    // Return session info as values instead of reference
    public fun get_session_info(
        app_session: &AppSession, 
        app_address: address,      // Outer key
        session_id: u64          // Inner key
    ): (u8, vector<u8>) {
        assert!(table::contains(&app_session.sessions, app_address), EAppNotFound);
        let sessions = table::borrow(&app_session.sessions, app_address);
        assert!(table::contains(sessions, session_id), ESessionNotFound);
        let session = table::borrow(sessions, session_id);
        (session.status, *&session.result_data)
    }

    // Get just the status of an app
    public fun get_app_status(registry: &AppRegistry, address: address): u8 {
        assert!(table::contains(&registry.apps, address), EAppNotFound);
        let app = table::borrow(&registry.apps, address);
        app.status
    }

    // Get just the status of a session
    public fun get_session_status(
        app_session: &AppSession, 
        app_address: address,      // Outer key
        session_id: u64          // Inner key
    ): u8 {
        assert!(table::contains(&app_session.sessions, app_address), EAppNotFound);
        let sessions = table::borrow(&app_session.sessions, app_address);
        assert!(table::contains(sessions, session_id), ESessionNotFound);
        let session = table::borrow(sessions, session_id);
        session.status
    } 

    // Get the auto_approved status
    public fun get_auto_approved_status(registry: &AppRegistry): bool {
        registry.auto_approved
    }

    // Get the session result_data vector
    public fun get_session_result(
        app_session: &AppSession, 
        app_address: address,      // Outer key
        session_id: u64          // Inner key
    ): vector<u8> {
        assert!(table::contains(&app_session.sessions, app_address), EAppNotFound);
        let sessions = table::borrow(&app_session.sessions, app_address);
        assert!(table::contains(sessions, session_id), ESessionNotFound);
        let session = table::borrow(sessions, session_id);
        *&session.result_data // Return a copy of the result_data vector
    }

    // Set the auto_approved flag (Admin only)
    public entry fun set_auto_approved(
        _: &AdminCap,
        registry: &mut AppRegistry, 
        value: bool
    ) {
        registry.auto_approved = value;
        event::emit(AutoApprovedUpdated { auto_approved: value });
    }
}