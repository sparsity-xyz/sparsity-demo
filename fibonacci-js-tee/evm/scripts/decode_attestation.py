import base64
import sys
import json
import requests

OUTPUT_FILE = "attestation_hex.txt"

def fetch_attestation(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Extract attestation_doc from the response
        if 'attestation' not in data or 'attestation_doc' not in data['attestation']:
            raise ValueError("Invalid response format: missing attestation_doc")
        
        return data['attestation']['attestation_doc']
    except requests.RequestException as e:
        print(f"Error fetching attestation: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python decode_attestation.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    
    # Fetch and decode attestation
    base64_string = fetch_attestation(url)

    try:
        # Decode Base64
        decoded_bytes = base64.b64decode(base64_string)
    except base64.binascii.Error as e:
        print(f"Error: Invalid Base64 string in response: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert bytes to hex string
    hex_string = decoded_bytes.hex()

    try:
        with open(OUTPUT_FILE, "w") as outfile:
            outfile.write(hex_string)
    except IOError as e:
        print(f"Error writing to output file {OUTPUT_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully converted attestation to hex and saved as {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
