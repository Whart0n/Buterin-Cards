import json
import base64
import urllib.parse
import os
from dotenv import load_dotenv
from web3 import Web3
import time
import re
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Configuration
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
if not INFURA_PROJECT_ID:
    raise ValueError("INFURA_PROJECT_ID environment variable is not set")

INFURA_URL = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
CONTRACT_ADDRESS = Web3.to_checksum_address("0x5726c14663a1ead4a7d320e8a653c9710b2a2e89")
OUTPUT_FILE = "token_quote_mapping.json"
BATCH_SIZE = 50  # Process 50 tokens at a time to manage Infura limits

# Full ABI
CONTRACT_ABI = [
    {"inputs":[{"internalType":"bytes32","name":"root","type":"bytes32"},{"internalType":"string","name":"jpegHeader","type":"string"},{"internalType":"uint256","name":"tokenIdFirstBlueChrominance","type":"uint256"},{"internalType":"uint256","name":"tokenIdFirstRedChrominance","type":"uint256"},{"internalType":"uint256","name":"NemptyBlueColorChunks","type":"uint256"},{"internalType":"uint256","name":"NemptyRedColorChunks","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"minerAddress","type":"address"},{"indexed":True,"internalType":"uint256","name":"uploadedKB","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":False,"internalType":"uint8","name":"phaseId","type":"uint8"},{"indexed":False,"internalType":"uint16","name":"tokenIdWithinPhase","type":"uint16"},{"indexed":False,"internalType":"uint8","name":"quoteId","type":"uint8"},{"indexed":False,"internalType":"uint8","name":"bgDirectionId","type":"uint8"},{"indexed":False,"internalType":"uint8","name":"bgPaletteId","type":"uint8"},{"indexed":False,"internalType":"uint16","name":"lastTokenIdInScan","type":"uint16"},{"indexed":False,"internalType":"uint32","name":"Nbytes","type":"uint32"},{"indexed":False,"internalType":"uint8","name":"Nicons","type":"uint8"},{"indexed":False,"internalType":"uint32","name":"seed","type":"uint32"}],"name":"Mined","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},
    {"inputs":[],"name":"JPEG_HEADER_POINTER","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"N_EMPTY_BLUE_COLOR_CHUNKS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"N_EMPTY_RED_COLOR_CHUNKS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"Nmined","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"TOKEN_ID_FIRST_BLUE_CHROMINANCE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"TOKEN_ID_FIRST_RED_CHROMINANCE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"baseURLAnimation","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"chunks","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"htmlHeader","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"pure","type":"function"},
    {"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"jpegFooter","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"pure","type":"function"},
    {"inputs":[{"internalType":"string","name":"dataChunk","type":"string"},{"internalType":"uint8","name":"phaseId","type":"uint8"},{"internalType":"uint16","name":"tokenIdWithinPhase","type":"uint16"},{"internalType":"uint16","name":"lastTokenIdInScan","type":"uint16"},{"internalType":"bytes32[]","name":"proof","type":"bytes32[]"}],"name":"mine","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"onchainAnimation","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"string","name":"newBaseURLAnimation","type":"string"}],"name":"setBaseURLAnimation","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"unpackChunk","outputs":[{"components":[{"internalType":"address","name":"dataPointer","type":"address"},{"internalType":"uint8","name":"phaseId","type":"uint8"},{"internalType":"uint16","name":"tokenIdWithinPhase","type":"uint16"},{"internalType":"uint16","name":"lastTokenIdInScan","type":"uint16"},{"internalType":"uint8","name":"quoteId","type":"uint8"},{"internalType":"uint8","name":"bgDirectionId","type":"uint8"},{"internalType":"uint8","name":"bgPaletteId","type":"uint8"},{"internalType":"uint8","name":"Nicons","type":"uint8"},{"internalType":"uint32","name":"Nbytes","type":"uint32"},{"internalType":"uint32","name":"seed","type":"uint32"}],"internalType":"struct ButerinCardsLib.ChunkUnpacked","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}
]

# Initialize Web3 and contract
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def process_tokens(start_id, end_id, token_quote_mapping=None):
    results = {}
    if token_quote_mapping is None:
        token_quote_mapping = {}  # Map quoteId to list of token IDs

    # Try to load existing results if file exists
    try:
        with open(OUTPUT_FILE, 'r') as f:
            results = json.load(f)
            print(f"Loaded {len(results)} existing results from {OUTPUT_FILE}")
    except (FileNotFoundError, json.JSONDecodeError):
        print("No existing results found, starting fresh")

    # Process tokens in batches
    for token_id in tqdm(range(start_id, end_id + 1), desc="Processing tokens"):
        if str(token_id) in results and token_id != 0:  # Always process token 0 to ensure it's included
            continue

        try:
            # Add delay to avoid Infura rate limits
            time.sleep(0.1)

            token_id, result = get_token_metadata(token_id)
            results[str(token_id)] = result

            # Extract quote title and build mapping
            if "attributes" in result and isinstance(result["attributes"], dict):
                quote_title = result["attributes"].get("Quote Title")
                if quote_title is not None:
                    if quote_title not in token_quote_mapping:
                        token_quote_mapping[quote_title] = []
                    if token_id not in token_quote_mapping[quote_title]:
                        token_quote_mapping[quote_title].append(token_id)
                        print(f"Mapped quote '{quote_title}' to token {token_id}")
                        # Save the mapping after each new quote is found
                        with open("quote_token_mapping.json", 'w') as f:
                            json.dump(token_quote_mapping, f, indent=2)
                elif token_id % 10 == 0:  # Log some missing quotes for debugging
                    print(f"Warning: No quote title found for token {token_id}")
                    print(f"Available attributes: {list(result['attributes'].keys())}")

            # Save progress every batch
            if token_id % BATCH_SIZE == 0 or token_id == end_id:
                with open(OUTPUT_FILE, 'w') as f:
                    json.dump(results, f, indent=2)
                if token_id % 100 == 0 or token_id == end_id:
                    print(f"\nSaved progress after token {token_id}")

        except Exception as e:
            print(f"\nError processing token {token_id}: {e}")
            results[str(token_id)] = {"error": str(e)}

    # Save the current state of the mapping
    with open("quote_token_mapping.json", 'w') as f:
        json.dump(token_quote_mapping, f, indent=2)
    print(f"\nProcessing complete! Results saved to {OUTPUT_FILE} and quote mapping to quote_token_mapping.json")
    print(f"Current quote mapping size: {len(token_quote_mapping)}")
    return results, token_quote_mapping

def get_token_metadata(token_id):
    try:
        debug = (token_id % 10 == 0 or token_id == 1)
        if debug:
            print(f"\n--- Processing token {token_id} ---")

        token_uri = contract.functions.tokenURI(token_id).call()

        if token_uri.startswith("data:application/json;base64,"):
            if token_id % 10 == 0 or token_id == 1:
                print("Detected base64 encoded JSON data")
            base64_data = token_uri.split("data:application/json;base64,")[1]
            json_data = base64.b64decode(base64_data).decode('utf-8')
            metadata = json.loads(json_data)

        elif token_uri.startswith("data:application/json;charset=UTF-8,"):
            if token_id % 10 == 0 or token_id == 1:
                print("Detected URL-encoded JSON data")
            url_encoded_json = token_uri.split("data:application/json;charset=UTF-8,")[1]
            json_str = urllib.parse.unquote(url_encoded_json)
            metadata = json.loads(json_str)

        elif "<svg" in token_uri:
            if token_id % 10 == 0 or token_id == 1:
                print("Detected SVG data directly in tokenURI")
            return token_id, {
                "name": f"Token {token_id} (SVG)",
                "type": "svg",
                "data": token_uri[:200] + "..."
            }
        else:
            if token_id % 10 == 0 or token_id == 1:
                print(f"Unexpected tokenURI format: {token_uri[:100]}...")
            return token_id, {
                "error": "Unhandled format",
                "preview": token_uri[:100] + "..."
            }

        # Extract relevant information
        result = {
            "token_id": token_id,
            "name": metadata.get("name", f"Token {token_id}"),
            "description": metadata.get("description", "")[:200] + ("..." if len(metadata.get("description", "")) > 200 else ""),
            "image": metadata.get("image", "")[:100] + ("..." if len(metadata.get("image", "")) > 100 else ""),
            "attributes": {}
        }

        if debug:
            print(f"Raw metadata keys: {list(metadata.keys())}")

        if "attributes" in metadata:
            for attr in metadata["attributes"]:
                trait_type = attr.get("trait_type", "unknown")
                result["attributes"][trait_type] = attr.get("value")

        return token_id, result

    except Exception as e:
        print(f"\nError processing token {token_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return token_id, {"token_id": token_id, "error": str(e)}

def build_quote_mapping_from_results():
    """Build quote-to-token mapping from existing results file."""
    try:
        with open(OUTPUT_FILE, 'r') as f:
            results = json.load(f)
        
        quote_mapping = {}
        for token_id, data in results.items():
            if not isinstance(data, dict) or 'attributes' not in data:
                continue
                
            quote_title = data['attributes'].get('Quote Title')
            if quote_title:
                if quote_title not in quote_mapping:
                    quote_mapping[quote_title] = []
                quote_mapping[quote_title].append(int(token_id))
        
        # Save the mapping
        with open("quote_token_mapping.json", 'w') as f:
            json.dump(quote_mapping, f, indent=2)
            
        print(f"\nBuilt quote mapping with {len(quote_mapping)} unique quotes")
        print("\nSample of the mapping (first 5 quotes):")
        for quote, tokens in list(quote_mapping.items())[:5]:
            print(f"- {quote}: {len(tokens)} tokens")
            
        return quote_mapping
        
    except Exception as e:
        print(f"Error building quote mapping: {e}")
        return {}

if __name__ == "__main__":
    # First, process all tokens to ensure we have the latest data
    MIN_TOKEN_ID = 0
    MAX_TOKEN_ID = 2014  # 2,015 cards total (0-2014 inclusive)
    
    print(f"Processing tokens {MIN_TOKEN_ID} to {MAX_TOKEN_ID} (total: {MAX_TOKEN_ID - MIN_TOKEN_ID + 1} cards)")
    
    # Process tokens in batches
    for start in range(MIN_TOKEN_ID, MAX_TOKEN_ID + 1, BATCH_SIZE):
        end = min(start + BATCH_SIZE - 1, MAX_TOKEN_ID)
        print(f"\nProcessing tokens {start} to {end}")
        process_tokens(start, end)
    
    # Now build the quote mapping from the results
    quote_mapping = build_quote_mapping_from_results()