import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import axios from 'axios';

function App() {
  const [address, setAddress] = useState(null);
  const [signature, setSignature] = useState(null);
  const [transferTo, setTransferTo] = useState("");
  const [transferAmount, setTransferAmount] = useState("");
  const [transferResult, setTransferResult] = useState(null);
  const [balance, setBalance] = useState(null);

  useEffect(() => {
    // Check for session token, address, and signature in localStorage on mount
    const token = localStorage.getItem('sessionToken');
    const savedAddress = localStorage.getItem('address');
    const savedSignature = localStorage.getItem('signature');
    if (token && savedAddress && savedSignature) {
      setAddress(savedAddress);
      setSignature(savedSignature);
    }
    // Listen for MetaMask account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (!accounts.length || accounts[0].toLowerCase() !== savedAddress?.toLowerCase()) {
          logout();
        }
      });
    }
    // Cleanup listener on unmount
    return () => {
      if (window.ethereum && window.ethereum.removeListener) {
        window.ethereum.removeListener('accountsChanged', logout);
      }
    };
  }, []);

  // Fetch balance when address changes or after transfer
  useEffect(() => {
    const fetchBalance = async () => {
      if (address) {
        try {
          const res = await axios.get(`${API}/balance`, { withCredentials: true });
          setBalance(res.data.balance);
        } catch (err) {
          setBalance(null);
        }
      } else {
        setBalance(null);
      }
    };
    fetchBalance();
  }, [address, transferResult]);

  const toHex = (str) =>
    '0x' + Array.from(str, c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('');

  const loginWithMetaMask = async () => {
    if (!window.ethereum) {
      alert('MetaMask is required!');
      return;
    }
    try {
      // Prompt user to select the correct MetaMask account
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      if (!accounts.length) {
        alert('No MetaMask account found. Please unlock MetaMask.');
        return;
      }
      const account = accounts[0];
      // Fetch a unique nonce from the backend
      const nonceRes = await axios.get(`${API}/nonce`, { withCredentials: true });
      const nonce = nonceRes.data.nonce;
      // Sign the nonce as a hex string
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [toHex(nonce), account],
      });
      // Debug logging
      console.log('Login address:', account);
      console.log('Login signature:', signature);
      console.log('Login nonce:', nonce);
      // Actually log in with backend to set session cookie
      const res = await axios.post(
        `${API}/login`,
        { address: account, signature },
        { withCredentials: true }
      );
      if (res.data.success) {
        localStorage.setItem('address', account);
        localStorage.setItem('signature', signature);
        setAddress(account);
        setSignature(signature);
      } else {
        alert('Login failed: ' + (res.data.error || 'Unknown error'));
      }
    } catch (err) {
      alert('Login failed: ' + (err.response?.data?.error || err.message));
    }
  };

  const logout = () => {
    localStorage.removeItem('sessionToken');
    localStorage.removeItem('address');
    localStorage.removeItem('signature');
    setAddress(null);
    setSignature(null);
  };

  const API = "http://localhost:8000";

  const handleTransfer = async (e) => {
    e.preventDefault();
    setTransferResult(null);
    try {
      const res = await axios.post(
        `${API}/transfer`,
        { to: transferTo, amount: transferAmount },
        { withCredentials: true }
      );
      setTransferResult({ success: true, ...res.data });
    } catch (err) {
      setTransferResult({ success: false, error: err.response?.data?.error || err.message });
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React MetaMask Login Demo</h1>
        {address ? (
          <>
            <div>Logged in as: {address}</div>
            <div>Signature: <code style={{wordBreak: 'break-all'}}>{signature}</code></div>
            <div style={{marginTop: 20, marginBottom: 20}}>
              <strong>Current Balance:</strong> {balance === null ? 'Loading...' : `${balance} USDC`}
            </div>
            {/* Deposit & Withdraw Buttons */}
            <div style={{ marginBottom: 20 }}>
              <button
                onClick={async () => {
                  const amount = window.prompt('Enter deposit amount:');
                  if (!amount || isNaN(amount) || Number(amount) <= 0) return;
                  try {
                    const res = await axios.post(
                      `${API}/deposit`,
                      { amount },
                      { withCredentials: true }
                    );
                    setBalance(res.data.balance);
                    setTransferResult({ success: true, message: `Deposited ${amount} USDC! New balance: ${res.data.balance}` });
                  } catch (err) {
                    setTransferResult({ success: false, error: err.response?.data?.detail || err.message });
                  }
                }}
                style={{ marginRight: 10 }}
              >
                Deposit
              </button>
              <button
                onClick={async () => {
                  const amount = window.prompt('Enter withdraw amount:');
                  if (!amount || isNaN(amount) || Number(amount) <= 0) return;
                  try {
                    const res = await axios.post(
                      `${API}/withdraw`,
                      { amount },
                      { withCredentials: true }
                    );
                    setBalance(res.data.balance);
                    setTransferResult({ success: true, message: `Withdrew ${amount} USDC! New balance: ${res.data.balance}` });
                  } catch (err) {
                    setTransferResult({ success: false, error: err.response?.data?.detail || err.message });
                  }
                }}
              >
                Withdraw
              </button>
            </div>
            <form onSubmit={handleTransfer} style={{marginTop: 20}}>
              <h3>Transfer USDC</h3>
              <input
                type="text"
                placeholder="Recipient address"
                value={transferTo}
                onChange={e => setTransferTo(e.target.value)}
                style={{width: 320}}
                required
              />
              <input
                type="number"
                placeholder="Amount"
                value={transferAmount}
                onChange={e => setTransferAmount(e.target.value)}
                min="0.01"
                step="0.01"
                style={{width: 120, marginLeft: 8}}
                required
              />
              <button type="submit" style={{marginLeft: 8}}>Transfer</button>
            </form>
            {transferResult && (
              <div style={{marginTop: 10, color: transferResult.success ? 'limegreen' : 'red'}}>
                {transferResult.success
                  ? transferResult.message || `Transferred! New balance: ${transferResult.from_balance}`
                  : `Error: ${transferResult.error}`}
              </div>
            )}
            <button onClick={logout} style={{marginTop: 20}}>Logout</button>
          </>
        ) : (
          <button onClick={loginWithMetaMask}>Login with MetaMask</button>
        )}
      </header>
    </div>
  );
}

export default App;
