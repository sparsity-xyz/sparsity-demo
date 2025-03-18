import React, { useState, useEffect, useRef } from "react";
import { createAppKit } from '@reown/appkit/react'
import { networks, projectId, metadata, ethersAdapter } from './config'
import { Message, BatchState, MessageType } from './websocket';
import {
    useAppKitEvents,
    useAppKitAccount,
    useAppKitProvider,
} from '@reown/appkit/react'
import { BrowserProvider, Contract } from 'ethers'
import ABI from './abi.json';


const contractAddress = import.meta.env.VITE_APP_ADDRESS;
const WEBSOCKET_INITIAL_RETRY_INTERVAL = 500;

var contract: any = null;
var ethersProvider: BrowserProvider;
var signer: any;

createAppKit({
    debug: true,
    adapters: [ethersAdapter],
    networks,
    metadata,
    projectId,
    features: {
        analytics: true // Optional - defaults to your Cloud configuration
    }
})

interface ShowMessage {
    sender: "User" | "Assistant";
    content: string;
}

const AG2Chat: React.FC = () => {
    const [messages, setMessages] = useState<ShowMessage[]>([]);
    const [input, setInput] = useState<string>("");
    const [socket, setSocket] = useState<WebSocket | null>(null);

    const walletAcc = useAppKitAccount();
    const events = useAppKitEvents()
    const { walletProvider } = useAppKitProvider('eip155')

    const chatContainerRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        if (walletAcc.address != null) {
            console.log(walletAcc.address);
            initWallet();
        }
    }, [events, walletAcc.address]);

    async function checkUser() {
        const playerInChat = await contract.playerInChat(walletAcc.address);
        console.log("playerInChat", playerInChat);
        if (playerInChat) {
            waitForSession();
            return;
        }
    }

    async function initWallet() {
        ethersProvider = new BrowserProvider(walletProvider as any);
        signer = await ethersProvider.getSigner();
        contract = new Contract(contractAddress, ABI, signer);

        checkUser();
    }

    const startChat = async () => {
        console.log(walletAcc.address);
        if (walletAcc.address == undefined) {
            alert("please connect wallet");
            return;
        }
        
        const playerInChat = await contract.playerInChat(walletAcc.address);
        console.log("playerInChat", playerInChat);
        if (playerInChat) {
            return;
        }

        const tx = await contract.startChat();
        const receipt = await tx.wait()
        if (receipt.status == 1) {
            console.log("join success", receipt.status);
        } else {
            console.log("Failed to join", receipt);
            return
        }
        waitForSession();

    }
    async function waitForSession() {
        // wait for the session to be ready
        const playerSession = await contract.playerSession(walletAcc.address);
        while (1) {
            const session = await contract.getSession(playerSession);
            console.log("session", session)
            if (session.status == 2) {
                await loginServer(session.endpoint)
                break;
            } else if (session.status >= 3) {
                break;
            }
            console.log("wait for the session to be ready", session.status);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    function randomString(length: number) {
        const chars =
          'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        let result = ''
        const charactersLength = chars.length
        for (let i = 0; i < length; i++) {
          result += chars.charAt(Math.floor(Math.random() * charactersLength))
        }
        return result
    }

    async function sign(message: string) {
        const signer = await ethersProvider.getSigner()
        return signer.signMessage(message)
    }

    async function loginServer(endpoint: string) {
        try {
          // sign the message
          const message = 'LOGIN-AG2-' + randomString(16)
          const signature = await sign(message)
    
          console.log(walletAcc.address, message, signature);
        //   const response = await fetch(`http://127.0.0.1:9981/login`, {
          const response = await fetch(`http://${endpoint}/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              address: walletAcc.address,
              message: message,
              signature: signature,
            }),
          })
    
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${await response.text()}`)
          }
    
          const data = await response.json()
          console.log('Server response:', data)
          connectServer(endpoint)
        } catch (error) {
          console.error('Error connecting to server:', error)
        }
    }

    async function connectServer(endpoint: string) {
        initWebsocket(endpoint);
    }

    async function waitForSessionSettlement() {
        const playerSession = await contract.playerSession(walletAcc.address);
        while (1) {
            const session = await contract.getSession(playerSession);
            if (session.status == 3) {
                const data = await contract.hashes(playerSession);
                console.log(data);
                alert("session settled!" + data);
                break;
            }
            if (session.status == 4) {
                console.log("settlement revert");
                break;
            }
            console.log("wait for the session to be settled", session.status);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    const initWebsocket = (endpoint: string) => {
        let newSocket: WebSocket;
        let retryCount = 0;

        const connectWebSocket = () => {
            newSocket = new WebSocket(`http://${endpoint}/ws`);

            newSocket.onopen = () => {
                console.log('WebSocket connect success');
                retryCount = 0;
            };

            newSocket.onmessage = (event) => {
                event.data.arrayBuffer().then((buffer: any) => {
                    const message = Message.decode(new Uint8Array(buffer));
                    if (message.type === MessageType.RESPONSE) {
                        const responseArr = BatchState.decode(message.data);
                        responseArr.states.forEach((x) => {
                            if (x.attributes[0].key == "data") {
                                // query the result
                                waitForSessionSettlement();
                                return;
                            }
                            const chatMessage = JSON.parse(x.attributes[0].value);
                            if (chatMessage?.messages) {
                                // add AI message
                                setMessages((prev) => [
                                    ...prev,
                                    ...chatMessage.messages.map((msg: { agent: string; content: string }) => ({
                                        sender: "Assistant",
                                        content: `${msg.agent}: ${msg.content}`,
                                    })),
                                ]);
                            } else {
                                setMessages((prev) => [...prev, { sender: "Assistant", content: "Sorry, I couldn't process that request." }]);
                            }
                        });
                    }
                });
            };

            newSocket.onerror = (error) => {
                console.error('WebSocket connect failed:', error);
                newSocket.close();
            };

            newSocket.onclose = (event) => {
                console.log('WebSocket connection closed:', event);
                retryCount++;
                const retryDelay = Math.min(
                    5000,
                    Math.pow(2, retryCount) * WEBSOCKET_INITIAL_RETRY_INTERVAL,
                );
                setTimeout(() => {
                    // console.log(`retry WebSocket... (retry count: ${retryCount})`);
                    // comment retry
                    // connectWebSocket();
                }, retryDelay);
            };

            setSocket(newSocket);
        };

        connectWebSocket();
    };

    // send message
    const sendMessage = async () => {
        if (!input.trim()) return;

        // check if user in the session
        const playerInChat = await contract.playerInChat(walletAcc.address);
        if (!playerInChat) {
            alert("please start chat");
            return;
        }

        // check session
        const playerSession = await contract.playerSession(walletAcc.address);
        console.log("player session", playerSession);
        const session = await contract.getSession(playerSession);
        if (session.status != 2) {
            alert("please wai for session start");
            return;
        }

        // add user message
        setMessages((prev) => [...prev, { sender: "User", content: input }]);
        setInput("");
        console.log(input);

        const content = {
            requestType: 'CHAT',
            address: walletAcc.address,
            message: input,
        };
        const data = new TextEncoder().encode(JSON.stringify(content));
        const message = {
            type: 0,
            address: walletAcc.address,
            timestamp: Date.now(),
            data: data,
            signature: new Uint8Array(),
        };
        const wsMsg = Message.encode(message).finish();
        socket?.send(wsMsg);
    };

    const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    };

    return (
        <div style={{ fontFamily: "Arial, sans-serif", maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
            <appkit-button />
            <h1>AG2 Chat Interface</h1>
            <div
                ref={chatContainerRef}
                style={{
                    border: "1px solid #ccc",
                    height: "400px",
                    overflowY: "auto",
                    padding: "10px",
                    marginBottom: "10px",
                }}
            >
                {messages.map((msg, index) => (
                    <div key={index} style={{ textAlign: msg.sender === "User" ? "right" : "left", marginBottom: "10px" }}>
                        <strong>{msg.sender}</strong>: {msg.content}
                    </div>
                ))}
            </div>
            <div>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    style={{ width: "75%", padding: "8px" }}
                />
                <span>   </span>
                <button onClick={sendMessage} style={{ padding: "8px 15px", background: "#4CAF50", color: "white", border: "none", cursor: "pointer" }}>
                    Send
                </button>
                <span>   </span>
                <button onClick={startChat} style={{ padding: "8px 15px", background: "#4CAF50", color: "white", border: "none", cursor: "pointer" }}>
                    Start Chat
                </button>
            </div>
        </div>
    );
};

export default AG2Chat;