import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
RPC_URL = "https://forno.celo-sepolia.celo-testnet.org"
CHAIN_ID = 11142220
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("BLOCKCHAIN_WALLET_ADDRESS")

if not PRIVATE_KEY or not WALLET_ADDRESS:
    print("Error: BLOCKCHAIN_PRIVATE_KEY or BLOCKCHAIN_WALLET_ADDRESS not found in .env")
    exit(1)

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("Error: Failed to connect to Celo Sepolia")
    exit(1)

print(f"Connected to Celo Sepolia. Deploying from: {WALLET_ADDRESS}")

# Install and compile contract
print("Installing solc 0.8.0...")
install_solc("0.8.0")

with open("contracts/contracts/VillageSubscriptionV2.sol", "r") as f:
    contract_source = f.read()

print("Compiling contract...")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"VillageSubscriptionV2.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

# Get bytecode and ABI
bytecode = compiled_sol["contracts"]["VillageSubscriptionV2.sol"]["VillageSubscriptionV2"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["VillageSubscriptionV2.sol"]["VillageSubscriptionV2"]["abi"]

# Deploy contract
print("Deploying contract...")
VillageSubscription = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get nonce
nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)

# Build transaction
transaction = VillageSubscription.constructor().build_transaction(
    {
        "chainId": CHAIN_ID,
        "gasPrice": w3.eth.gas_price,
        "from": WALLET_ADDRESS,
        "nonce": nonce,
    }
)

# Sign transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)

# Send transaction
print("Sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# Wait for receipt
print(f"Waiting for transaction to be mined... (Hash: {tx_hash.hex()})")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print(f"Contract deployed successfully at: {contract_address}")

# Save configuration
config_data = {
    "contract_address": contract_address,
    "abi": abi
}

with open("contract_config.json", "w") as f:
    json.dump(config_data, f, indent=4)

print("Updated contract_config.json with new address and ABI.")