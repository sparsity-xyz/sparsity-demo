import requests
import base64
import argparse

def fetch_and_decode_settlement_data(url):
    # Fetch the settlement data from the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Assuming the response is JSON and contains 'signature' and 'result' keys
    data = response.json()
    signature_base64 = data.get('signature')
    result_base64 = data.get('result')

    # Decode the base64 encoded signature to hex
    if signature_base64:
        signature_bytes = base64.b64decode(signature_base64)
        signature_hex = '0x' + signature_bytes.hex()
        with open('signature.txt', 'w') as sig_file:
            sig_file.write(signature_hex)

    # Decode the base64 encoded result to hex
    if result_base64:
        result_bytes = base64.b64decode(result_base64)
        result_hex = '0x' + result_bytes.hex()
        with open('result.txt', 'w') as res_file:
            res_file.write(result_hex)

if __name__ == "__main__":
    DEFAULT_URL = "http://43.201.52.244:8001/settlement"
    
    parser = argparse.ArgumentParser(description='Fetch and decode settlement data')
    parser.add_argument('--url', default=DEFAULT_URL,
                      help=f'Settlement URL (default: {DEFAULT_URL})')
    
    args = parser.parse_args()
    fetch_and_decode_settlement_data(args.url)