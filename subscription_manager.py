import json
import streamlit as st
from web3 import Web3
from datetime import datetime
import os
from config import config

# Celo Sepolia RPC
RPC_URL = "https://forno.celo-sepolia.celo-testnet.org"
EXPLORER_URL = "https://sepolia.celoscan.io"

class SubscriptionManager:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.contract = self._load_contract()
        
    def _load_contract(self):
        try:
            # Try to load from file first
            if os.path.exists("contract_config.json"):
                with open("contract_config.json", "r") as f:
                    config_data = json.load(f)
            else:
                # Fallback contract configuration for deployment
                config_data = {
                    "contract_address": "0x1234567890123456789012345678901234567890",  # Replace with your actual contract address
                    "abi": []  # Add your contract ABI here
                }
                st.warning("Using fallback contract configuration. Please update contract_config.json with your actual contract details.")
            
            return self.w3.eth.contract(address=config_data["contract_address"], abi=config_data["abi"])
        except Exception as e:
            st.error(f"Failed to load contract configuration: {e}")
            return None

    def is_connected(self):
        return self.w3.is_connected()

    def check_subscription(self, wallet_address, feature_id):
        """Check if a wallet has an active subscription for a specific feature"""
        if not self.contract or not wallet_address:
            return False
        
        try:
            checksum_address = Web3.to_checksum_address(wallet_address)
            is_active = self.contract.functions.isSubscribed(checksum_address, feature_id).call()
            return is_active
        except Exception as e:
            print(f"Error checking subscription: {e}")
            return False

    def get_subscription_details(self, wallet_address, feature_id):
        """Get expiry timestamp and status"""
        if not self.contract or not wallet_address:
            return False, 0
            
        try:
            checksum_address = Web3.to_checksum_address(wallet_address)
            is_active, expiry = self.contract.functions.getSubscriptionDetails(checksum_address, feature_id).call()
            return is_active, expiry
        except Exception as e:
            print(f"Error getting details: {e}")
            return False, 0

    def get_prices(self):
        """Get current plan prices in CELO"""
        if not self.contract:
            return None
            
        try:
            weekly = self.w3.from_wei(self.contract.functions.weeklyPrice().call(), 'ether')
            monthly = self.w3.from_wei(self.contract.functions.monthlyPrice().call(), 'ether')
            yearly = self.w3.from_wei(self.contract.functions.yearlyPrice().call(), 'ether')
            
            return {
                "Weekly": float(weekly),
                "Monthly": float(monthly),
                "Yearly": float(yearly)
            }
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return None

    def purchase_subscription(self, user_wallet, feature_id, plan_type, price_eth):
        """Purchase subscription for a user using the app's wallet (Server-side)"""
        try:
            # Get credentials from environment variables
            PRIVATE_KEY = config.BLOCKCHAIN_PRIVATE_KEY
            WALLET_ADDRESS = config.BLOCKCHAIN_WALLET_ADDRESS
            
            if not PRIVATE_KEY or not WALLET_ADDRESS:
                return False, "Blockchain credentials not configured"
            
            if not self.contract:
                return False, "Contract not loaded"

            nonce = self.w3.eth.get_transaction_count(WALLET_ADDRESS)
            price_wei = self.w3.to_wei(price_eth, 'ether')
            
            # Build transaction using the new purchaseSubscriptionFor function
            txn = self.contract.functions.purchaseSubscriptionFor(
                Web3.to_checksum_address(user_wallet), 
                feature_id, 
                plan_type
            ).build_transaction({
                'chainId': 11142220, # Celo Sepolia
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'from': WALLET_ADDRESS,
                'nonce': nonce,
                'value': price_wei
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return True, tx_hash.hex()
            
        except Exception as e:
            return False, str(e)

    def cancel_subscription(self, user_wallet, feature_id):
        """Cancel subscription for a user using the app's wallet (Server-side)"""
        try:
            # Get credentials from environment variables
            PRIVATE_KEY = config.BLOCKCHAIN_PRIVATE_KEY
            WALLET_ADDRESS = config.BLOCKCHAIN_WALLET_ADDRESS
            
            if not PRIVATE_KEY or not WALLET_ADDRESS:
                return False, "Blockchain credentials not configured"
            
            if not self.contract:
                return False, "Contract not loaded"

            nonce = self.w3.eth.get_transaction_count(WALLET_ADDRESS)
            
            # Build transaction using the new cancelSubscriptionFor function
            txn = self.contract.functions.cancelSubscriptionFor(
                Web3.to_checksum_address(user_wallet), 
                feature_id
            ).build_transaction({
                'chainId': 11142220, # Celo Sepolia
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'from': WALLET_ADDRESS,
                'nonce': nonce
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return True, tx_hash.hex()
            
        except Exception as e:
            return False, str(e)

# Singleton instance
subscription_manager = SubscriptionManager()

def render_subscription_ui(feature_name, feature_id):
    """Render the subscription purchase UI for a specific feature using server-side signing"""
    
    # Check if blockchain is enabled
    if not config.BLOCKCHAIN_ENABLED:
        st.info(f"🎉 {feature_name} is available for free in this demo!")
        st.markdown("*In production, this would require a blockchain subscription.*")
        return True  # Allow access for demo
    
    st.markdown(f"## 💎 {feature_name} - Premium Feature")
    
    # Wallet Input
    default_wallet = st.session_state.get("user_wallet", "")
    wallet_address = st.text_input("Enter your Celo Wallet Address:", value=default_wallet, key=f"sub_wallet_{feature_id}")
    
    if wallet_address:
        st.session_state.user_wallet = wallet_address
        is_subscribed = subscription_manager.check_subscription(wallet_address, feature_id)
        
        if is_subscribed:
            st.success(f"✅ Active Subscription for {feature_name}!")
            
            # Show cancellation option
            with st.expander("⚙️ Subscription Settings"):
                st.warning("⚠️ Cancelling will immediately revoke access.")
                if st.button(f"Cancel {feature_name} Subscription", key=f"cancel_{feature_id}", type="secondary"):
                    with st.spinner("Processing cancellation on Celo Blockchain..."):
                        success, result = subscription_manager.cancel_subscription(wallet_address, feature_id)
                        if success:
                            st.success(f"🎉 Cancellation Successful!")
                            st.markdown(f"[View on Celo Explorer]({EXPLORER_URL}/tx/{result})")
                            st.rerun()
                        else:
                            st.error(f"Cancellation failed: {result}")
            return True
        else:
            st.warning(f"🔒 This feature requires an active subscription.")
            
            st.markdown("### 🛒 Purchase Subscription")
            st.info("The app's wallet will pay for your subscription on Celo Sepolia.")
            
            prices = subscription_manager.get_prices()
            
            if prices:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info(f"**Weekly**\n\n{prices['Weekly']} CELO")
                    if st.button("Select Weekly", key=f"wk_{feature_id}"):
                        st.session_state[f"plan_{feature_id}"] = 1
                        st.session_state[f"price_{feature_id}"] = prices['Weekly']
                
                with col2:
                    st.info(f"**Monthly**\n\n{prices['Monthly']} CELO")
                    if st.button("Select Monthly", key=f"mo_{feature_id}"):
                        st.session_state[f"plan_{feature_id}"] = 2
                        st.session_state[f"price_{feature_id}"] = prices['Monthly']
                        
                with col3:
                    st.info(f"**Yearly**\n\n{prices['Yearly']} CELO")
                    if st.button("Select Yearly", key=f"yr_{feature_id}"):
                        st.session_state[f"plan_{feature_id}"] = 3
                        st.session_state[f"price_{feature_id}"] = prices['Yearly']
                
                if f"plan_{feature_id}" in st.session_state:
                    plan_map = {1: "Weekly", 2: "Monthly", 3: "Yearly"}
                    selected_plan = st.session_state[f"plan_{feature_id}"]
                    plan_price = st.session_state[f"price_{feature_id}"]
                    
                    st.markdown("---")
                    st.markdown(f"### 💳 Complete Purchase ({plan_map[selected_plan]})")
                    st.write(f"**Amount:** {plan_price} CELO")
                    
                    # Purchase Button
                    if st.button(f"⚡ Purchase Subscription", key=f"pay_{feature_id}", type="primary"):
                        with st.spinner("Processing transaction on Celo Blockchain..."):
                            success, result = subscription_manager.purchase_subscription(
                                wallet_address,
                                feature_id,
                                selected_plan, 
                                plan_price
                            )
                            
                            if success:
                                st.balloons()
                                st.success(f"🎉 Transaction Successful!")
                                st.markdown(f"[View on Celo Explorer]({EXPLORER_URL}/tx/{result})")
                                st.rerun()
                            else:
                                st.error(f"Transaction Failed: {result}")
            return False
    return False
