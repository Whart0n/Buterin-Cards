import os
from dotenv import load_dotenv
from web3 import Web3
import json
import base64

# Load environment variables from .env file
load_dotenv()

# Get Infura Project ID from environment variables
infura_project_id = os.getenv('INFURA_PROJECT_ID')
if not infura_project_id:
    raise ValueError("INFURA_PROJECT_ID environment variable is not set")

# Connect to Ethereum mainnet using Infura
infura_url = f'https://mainnet.infura.io/v3/{infura_project_id}'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Contract address and ABI
# Using Web3 to ensure proper checksum address
contract_address = Web3.to_checksum_address('0x5726c14663a1ead4a7d320e8a653c9710b2a2e89')
# Minimal ABI for tokenURI function
abi = '''[{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]'''

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

import urllib.parse

def get_token_uri(token_id):
    try:
        print(f"\n--- Fetching tokenURI for token ID: {token_id} ---")
        token_uri = contract.functions.tokenURI(token_id).call()
        print(f"Raw tokenURI: {token_uri[:200]}...")
        
        if token_uri.startswith("data:application/json;base64,"):
            print("Detected base64 encoded JSON data")
            base64_data = token_uri.split("data:application/json;base64,")[1]
            json_data = base64.b64decode(base64_data).decode('utf-8')
            print(f"Decoded JSON: {json_data[:200]}...")
            return json.loads(json_data)
        elif token_uri.startswith("data:application/json;charset=UTF-8,"):
            print("Detected URL-encoded JSON data")
            # Extract the URL-encoded JSON part after the comma
            url_encoded_json = token_uri.split("data:application/json;charset=UTF-8,")[1]
            # URL decode the JSON string
            json_str = urllib.parse.unquote(url_encoded_json)
            print(f"URL-decoded JSON: {json_str[:200]}...")
            return json.loads(json_str)
        elif "<svg" in token_uri:
            print("Detected SVG data directly in tokenURI")
            return {"svg_data": token_uri[:200] + "..."}
        else:
            print("Unknown tokenURI format")
            return {"raw_data": token_uri[:200] + "..."}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def print_token_metadata(token_id, metadata):
    print(f"\n=== Token ID: {token_id} ===")
    if not metadata:
        print("No metadata found")
        return
        
    print(f"Name: {metadata.get('name', 'N/A')}")
    print(f"Description: {metadata.get('description', 'N/A')[:200]}...")
    
    # Print attributes if they exist
    if 'attributes' in metadata:
        print("\nAttributes:")
        for attr in metadata['attributes']:
            print(f"- {attr.get('trait_type', 'Unknown')}: {attr.get('value', 'N/A')}")
    
    # Print image URL if it exists
    if 'image' in metadata:
        print(f"\nImage URL: {metadata['image'][:100]}...")

if __name__ == "__main__":
    # Test with multiple token IDs
    test_token_ids = [1, 2, 3, 10, 100]
    
    for token_id in test_token_ids:
        try:
            metadata = get_token_uri(token_id)
            print_token_metadata(token_id, metadata)
            print("\n" + "="*50 + "\n")  # Separator between tokens
        except Exception as e:
            print(f"Error processing token {token_id}: {str(e)}")
            print("\n" + "="*50 + "\n")