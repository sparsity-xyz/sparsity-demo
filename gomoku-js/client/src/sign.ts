import nacl from 'tweetnacl';

export function loadKeys() {
  const storedKeys = localStorage.getItem('keyPair');

  if (storedKeys) {
    const parsedKeys = JSON.parse(storedKeys);
    console.log("🔐 Loaded keys from localStorage");

    const publicKey = new Uint8Array(parsedKeys.publicKey);
    const secretKey = new Uint8Array(parsedKeys.secretKey);

    return { publicKey, secretKey };
  } else {
    const newKeyPair = nacl.sign.keyPair();

    localStorage.setItem('keyPair', JSON.stringify({
      publicKey: Array.from(newKeyPair.publicKey),
      secretKey: Array.from(newKeyPair.secretKey),
    }));

    console.log("🔐 Generated new key pair");
    return newKeyPair;
  }
}