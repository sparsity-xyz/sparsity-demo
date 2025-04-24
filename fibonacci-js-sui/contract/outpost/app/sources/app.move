module app::app {
    use sui::tx_context::{Self, TxContext, sender};
    use sui::table::{Self, Table};
    use sparsity::outpost::{
        Self, 
        AppRegistry, 
        AppSession,  
        create_session as outpost_create_session, 
        get_session_info as outpost_get_session_info,
        get_session_status as outpost_get_session_status
    };

    // --- Constants ---
    // Import constants locally to avoid scoping issues
    const SESSION_IDLE: u8 = 0;
    const SESSION_ACTIVE: u8 = 1;
    const SESSION_SETTLED: u8 = 2;
    const SESSION_EXPIRED: u8 = 3;

    // --- Error Codes ---
    const ESessionNotFound: u64 = 1;
    const EUserNotInRegistry: u64 = 2;

    // Represents a session and its current status
    // Note: self defined session struct instead of outpost session struct
    public struct Session has key, store { 
        id: UID,
        status: u8,
        initial_data: vector<u8>,
        result_data: vector<u8>   
    }

    // --- Capability Structs ---
    // Admin capability to control privileged operations
    public struct AdminCap has key, store {
        id: UID
    }

    // Settle capability to control session settlement operations
    public struct SettleCap has key, store {
        id: UID
    }

    // --- State Structs ---
    // TODO: evaluate if we want to split user table and session table 
    public struct State has key, store {
        id: UID,
        users: Table<address, u64>,
        sessions: Table<u64, Session>,
        next_session_id: u64
    }

    // --- Initialization ---
    // Initialize the contract
    fun init(ctx: &mut TxContext) {
        let admin_cap = AdminCap {
            id: object::new(ctx)
        };
        
        let settle_cap = SettleCap {
            id: object::new(ctx)
        };
        
        let state = State {
            id: object::new(ctx),
            users: table::new(ctx),
            sessions: table::new(ctx),
            next_session_id: 0
        }; 

        // Transfer capabilities to the deployer
        transfer::transfer(admin_cap, tx_context::sender(ctx));
        transfer::transfer(settle_cap, tx_context::sender(ctx));
        // Share the state object
        transfer::share_object(state); 
    }

    // --- Admin Functions ---
    // Update the settle capability owner
    public entry fun update_settle_cap(
        _: &AdminCap,
        settle_cap: SettleCap,
        settle_cap_address: address,
        _ctx: &mut TxContext
    ){
        transfer::transfer(settle_cap, settle_cap_address);
    }

    // --- Session Management Functions ---
    // Start/Create a new session
    public entry fun create_session( 
        registry: &AppRegistry,
        app_session: &mut AppSession,
        app_address: address,
        app_state: &mut State, 
        initial_data: vector<u8>,
        ctx: &mut TxContext
    ) {
        // TODO: check if user can start a session session_id 
        
        // 1. Create local session record
        let session = Session {
            id: object::new(ctx),
            status: SESSION_IDLE,
            initial_data: initial_data,
            result_data: vector[]
        };
        table::add(&mut app_state.sessions, app_state.next_session_id, session);

        // 2. Create session in outpost
        outpost_create_session(
            registry,
            app_session,
            app_address,
            app_state.next_session_id, 
            initial_data,
            ctx
        );
        app_state.next_session_id = app_state.next_session_id + 1;
    }

    // Allow a user to join an existing session
    public entry fun join_session(
        app_state: &mut State,
        app_session: &AppSession,
        app_address: address,
        session_id: u64,
        ctx: &mut TxContext
    ){
        // TODO: check if user can join a session session_id 
        // TODO: check if session exists in app_session
        
        let sender_addr = sender(ctx);
        
        // Add user to the session if they're not already in the registry
        if (table::contains(&app_state.users, sender_addr)) {
            let current_session_ref = table::borrow_mut(&mut app_state.users, sender_addr);
            *current_session_ref = session_id;
        } else {
            // If user doesn't exist in the table, add them
            table::add(&mut app_state.users, sender_addr, session_id);
        }
    }

    // Settle a session with result data (requires SettleCap)
    public entry fun settle_session(
        _: &SettleCap,
        app_state: &mut State,    
        session_id: u64,          
        data: vector<u8>
    ){
        assert!(table::contains(&app_state.sessions, session_id), ESessionNotFound);
        
        let session = table::borrow_mut(&mut app_state.sessions, session_id);
        session.status = SESSION_SETTLED;
        session.result_data = data;
        
        // TODO: Consider also updating the outpost session status, but need to pass app address as parameter, which is a bit wired
    }

    // --- View Functions ---
    // Get session info from outpost
    public fun get_session_info(
        app_session: &AppSession, 
        app_address: address,     
        session_id: u64
    ): (u8, vector<u8>) {
        outpost_get_session_info(
            app_session, 
            app_address,      
            session_id         
        )
    }

    // Check if a user is in a specific session
    public fun is_user_in_session(   
        app_state: &State,
        session_id_to_check: u64,
        ctx: &TxContext
    ): bool {
        let sender_addr = sender(ctx);
        
        if (table::contains(&app_state.users, sender_addr)) {
            let registered_session_id = *table::borrow(&app_state.users, sender_addr);
            registered_session_id == session_id_to_check
        } else {
            false 
        }
    }
}