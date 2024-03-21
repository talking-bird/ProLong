import os.path

import yaml
import streamlit as st
import streamlit_authenticator as stauth
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from omegaconf import OmegaConf
from yaml.loader import SafeLoader
from cryptography.hazmat.primitives import serialization

from source.blockchain import ProLongBlockchain
from source.io_utils import Storage, KeyStorage
from source.cryptography import generate_key_and_iv, encrypt_data, public_key2bytes, private_key2bytes, \
    generate_public_and_private_keys, encrypt_data_via_public_key, decrypt_data_via_private_key, decrypt_data


HOST_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
HOST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


def owner_dashboard_view(prolong_blockchain, storage,
                         owner_address, owner_private_key):
    st.write(f'Welcome *{name}* to your ProLong dashboard.')
    balance = prolong_blockchain.pl_token.functions.balanceOf(owner_address).call()
    st.write(f'Your current balance is: **{balance} PLT**')
    
    # DASHBOARD ZONE
    st.divider()
    st.title('Dashboard')

    current_transactions = storage.get_transactions_owner(owner_address)
    if len(current_transactions) ==0:
        st.info('There are currently no purchase orders.', icon="ℹ️")
    else:
        for transaction in current_transactions:
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            with st.container():
                tr_id, consumer_address, _, file_hash, _, _ = transaction
                c1.write(f"{consumer_address}")
                c2.write(f"{file_hash}")

                confirm_button = c3.button(label="Confirm",
                                           key=f'confirm_key_{tr_id}',
                                           use_container_width=True)

                if confirm_button:
                    event = prolong_blockchain.get_data_market_events()[0]['args']

                    aes_key = KeyStorage().get_key(event['hash'].hex())[0][0]

                    encrypted_key = encrypt_data_via_public_key(serialization.load_pem_public_key(event['publicKey']),
                                                                aes_key)

                    storage.update_confirm_transaction(tr_id, encrypted_key)

    # FILE UPLOAD ZONE
    st.divider()
    st.title('Upload a new file')
    uploaded_file = st.file_uploader("Choose your data file")
    if uploaded_file is not None:
        key, iv = generate_key_and_iv()
        encrypted_data, data_hash = encrypt_data(uploaded_file.getvalue(), key, iv)
        
        short_description = st.text_input("Please, enter short description of your file, e.g. `Glucose in blood`",
                                          value="")
        price = st.number_input('Set the desired price (PLT) for your analysis',
                                min_value=0, max_value=1000000, 
                                value=10)
        sell_decision = st.button(label="Put on market")

        if sell_decision:
            if not storage.has_file(data_hash):
                key_storage = KeyStorage()
                key_storage.add_key(data_hash, key)

                storage.add_file_to_storage(encrypted_data, data_hash, owner_address)
                storage.add_file(data_hash, owner_address, short_description, iv, price)

                print(key, iv)

                prolong_blockchain.upload(owner_address, owner_private_key,
                                          data_hash, price)
                st.info('The file was succesfully placed on the datamarket!', icon="ℹ️")
            else:
                st.warning('This file has already been uploaded!')

    # UPLOADED FILES ZONE
    st.divider()
    st.title('My files')

    files_list = storage.get_files()
    for file in files_list:
        c1, c2, c3  = st.columns([1.5, 3, 1])
        with st.container():
            file_id, file_hash, owner_id, short_description, _, price = file
            if owner_id == owner_address:
                c1.write(f"{owner_id}")
                c2.write(f"{short_description}")
                c3.write(f"{price} PLT")
            else:
                pass


def marketplace_view(prolong_blockchain, storage,
                     consumer_address, consumer_private_key):
    st.write(f'Welcome *{name}* to the ProLong marketplace.')
    balance = prolong_blockchain.pl_token.functions.balanceOf(consumer_address).call()
    st.write(f'Your current balance is: {balance} PLT')
    st.title('Marketplace')

    if not os.path.exists('./rsa_pub.pem'):
        consumer_rsa_private_key, consumer_rsa_public_key = generate_public_and_private_keys()

        consumer_rsa_public_key_bytes = public_key2bytes(consumer_rsa_public_key)

        with open("rsa_pub.pem", "wb") as rsa_pub:
            rsa_pub.write(consumer_rsa_public_key_bytes)

        with open("rsa_priv.pem", "wb") as rsa_priv:
            rsa_priv.write(private_key2bytes(consumer_rsa_private_key))

    files_list = storage.get_files()

    for file in files_list:
        c1, c2, c3, c4 = st.columns([1.5, 3, 1, 1])
        with st.container():
            file_id, file_hash, owner_id, short_description, _, price = file
            c1.write(f"{owner_id}")
            c2.write(f"{short_description}")
            c3.write(f"{price} PLT")

            buy_button = c4.button(label="Buy", 
                                   key=f'buy_key_{file_id}',  
                                   use_container_width=True)

            if buy_button:
                prolong_blockchain.transfer(HOST_ADDRESS, HOST_PRIVATE_KEY,
                                            consumer_address,
                                            price)

                with open("rsa_pub.pem", "rb") as rsa_pub:
                    prolong_blockchain.buy(consumer_address, consumer_private_key,
                                           file_hash, price, rsa_pub.read())

                storage.add_transaction(consumer_address, owner_id, file_hash)
                
        st.write('')
    
    # FILE DOWNLOADING ZONE
    st.divider()
    st.title('Purchased files')

    current_transactions = storage.get_transactions_consumer(consumer_address)
    if len(current_transactions) ==0:
        st.info('There are currently no purchased files.', icon="ℹ️")
    else:
        for transaction in current_transactions:
            tr_id, consumer_address, owner_address, file_hash, encrypted_key, is_confirmed = transaction
            if is_confirmed == 1:
                c1, c2, c3 = st.columns([1.5, 1.5, 1])
                with st.container():
                    
                    c1.write(f"{owner_address}")
                    c2.write(f"{file_hash}")

                    with open("rsa_priv.pem", "rb") as rsa_priv:
                        decrypted_key = \
                            decrypt_data_via_private_key(serialization.load_pem_private_key(rsa_priv.read(), None),
                                                         encrypted_key)

                    decrypted_data = decrypt_data(storage.get_path_to_encrypted_file(owner_address, file_hash),
                                                  decrypted_key,
                                                  storage.get_iv(file_hash)[0][0])

                    st.download_button("Download", decrypted_data, file_name=f'{file_hash}.pdf')


if __name__ == "__main__":
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    st.title('ProLong')

    contracts_config = OmegaConf.create(
        {'plt': {'path': 'artifacts/contracts/ProLongToken.sol/ProLongToken.json',
                 'address': '0x5FbDB2315678afecb367f032d93F642f64180aa3'},
         'dm': {'path': 'artifacts/contracts/DataMarket.sol/DataMarket.json',
                'address': '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512'}
         }
    )
    prolong_blockchain = ProLongBlockchain(contracts_config)

    path_to_data_storage = "./data"
    storage = Storage(path_to_data_storage)

    name, authentication_status, username = authenticator.login('main')
    authenticator.logout('LogOut')

    if authentication_status:
        user_config = config['credentials']['usernames'][username]

        if username == 'web3owner':
            owner_dashboard_view(prolong_blockchain, storage,
                                 user_config['address'], 
                                 user_config['private_key'])

        elif username == 'web3consumer':
            marketplace_view(prolong_blockchain, storage,
                             user_config['address'], 
                             user_config['private_key'])

        

    elif not authentication_status:
        st.error('Username/password is incorrect')

    elif authentication_status is None:
        st.warning('Please enter your username and password')
