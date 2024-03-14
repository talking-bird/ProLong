import yaml
import streamlit as st
import streamlit_authenticator as stauth
import asyncio
import os

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from omegaconf import OmegaConf
from yaml.loader import SafeLoader
from source.blockchain import ProLongBlockchain
from source.io_utils import Storage, KeyStorage
from source.cryptography import generate_key_and_iv, encrypt_data, public_key2bytes, private_key2bytes, \
    generate_public_and_private_keys


HOST_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
HOST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


def owner_dashboard_view(prolong_blockchain, storage,
                         owner_address, owner_private_key):
    st.write(f'Welcome *{name}* to your ProLong dashboard.')
    st.title('Dashboard')

    # TODO. Here we need to set price as well as short description

    uploaded_file = st.file_uploader("Choose your data file")
    short_description = 'step_by_step_encrypt.drawio'
    price = 20

    if uploaded_file is not None:
        key, iv = generate_key_and_iv()

        encrypted_data, data_hash = encrypt_data(uploaded_file.getvalue(), key, iv)

        if not storage.has_file(data_hash):
            key_storage = KeyStorage()
            key_storage.add_key(data_hash, key)

            storage.add_file_to_storage(encrypted_data, data_hash, owner_address)
            storage.add_file(data_hash, owner_address, short_description, iv, price)

            prolong_blockchain.upload(owner_address, owner_private_key,
                                      data_hash, price)

        else:
            st.warning('This file has already been uploaded')


def marketplace_view(prolong_blockchain, storage,
                     consumer_address, consumer_private_key):
    st.write(f'Welcome *{name}* to the ProLong marketplace.')
    st.title('Marketplace')

    if len(storage.get_public_key(consumer_address)) == 0:
        consumer_rsa_private_key, consumer_rsa_public_key = generate_public_and_private_keys()

        consumer_rsa_public_key_bytes = public_key2bytes(consumer_rsa_public_key)

        with open("rsa_pub.pem", "wb") as rsa_pub:
            rsa_pub.write(consumer_rsa_public_key_bytes)

        with open("rsa_priv.pem", "wb") as rsa_priv:
            rsa_priv.write(private_key2bytes(consumer_rsa_private_key))

        storage.add_consumer(consumer_address, consumer_rsa_public_key_bytes)

    files_list = storage.get_files()

    for file in files_list:
        c1, c2, c3, c4 = st.columns([3, 3, 1, 1])
        with st.container():
            c1.write(f"{file[2]}")
            c2.write(f"{file[3]}")
            c3.write(f"{file[5]}")

            buy_button = c4.button(label="Buy", use_container_width=True)

            if buy_button:
                prolong_blockchain.transfer(HOST_ADDRESS, HOST_PRIVATE_KEY,
                                            consumer_address,
                                            file[5])

                prolong_blockchain.buy(consumer_address, consumer_private_key,
                                       file[1], file[5])
                
        st.write('')


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

    path_to_data_storage = "/Users/Konstantin/Desktop/BCEI/data"
    storage = Storage(path_to_data_storage)

    name, authentication_status, username = authenticator.login('main')

    if authentication_status:
        user_config = config['credentials']['usernames'][username]

        if username == 'web3owner':
            owner_dashboard_view(prolong_blockchain, storage,
                                 user_config['address'], user_config['private_key'])

        elif username == 'web3consumer':
            marketplace_view(prolong_blockchain, storage,
                             user_config['address'], user_config['private_key'])

        authenticator.logout('LogOut')

    elif not authentication_status:
        st.error('Username/password is incorrect')

    elif authentication_status is None:
        st.warning('Please enter your username and password')
