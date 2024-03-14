import json
from web3 import Web3


class ProLongBlockchain:

    def __init__(self, contracts_config,
                 ip="http://127.0.0.1:8545", chain_id=31337):
        self.w3 = Web3(Web3.HTTPProvider(ip))

        self.chain_id = chain_id

        self.plt_config = contracts_config.plt
        self.dm_config = contracts_config.dm

        self.pl_token = self._get_w3_contract(self.plt_config.address, self.plt_config.path)
        self.data_market = self._get_w3_contract(self.dm_config.address, self.dm_config.path)

    def _get_w3_contract(self, contract_address, json_path):
        with open(json_path) as file:
            contract = json.load(file)

        return self.w3.eth.contract(address=contract_address, abi=contract['abi'])

    def _build_and_send_transaction(self, contract, function_name: str,
                                    addr_from: str, private_key: str,
                                    *args, **kwargs):
        """ Template for all transactions (functions that modify blockchain state).
        This includes transfer, upload, buy functions

        Args:
            contract (web3._utils.datatypes.Contract): PLToken or DataMarket
            function_name (str): function name from blockchain
            addr_from (str): address of the sender
            private_key (str): private key of the sender. It is used to sign the transaction
        """
        # Get the latest transaction nonce
        nonce = self.w3.eth.get_transaction_count(addr_from)

        # Dynamically access the function based on the provided function name
        function_to_call = getattr(contract.functions, function_name)

        # Build the transaction object
        transaction = function_to_call(*args).build_transaction(
            {
                "chainId": self.chain_id,
                "gasPrice": self.w3.eth.gas_price,
                "from": addr_from,
                "nonce": nonce,
                **kwargs,
            }
        )

        # Sign the transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=private_key)

        # Send the transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined and get the transaction receipt
        # print("Waiting for transaction to finish...")
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def transfer(self, from_address, from_private_key,
                 to_address,
                 n_tokens):
        """transfer PLTokens from one address to another.
        It's needed after deploying contract to share tokens from one account to another

        Args:
            from_address (str): sender address
            from_private_key (str): sender private key
            to_address (str): receiver address
            n_tokens (int): number of tokens to send
        """
        self._build_and_send_transaction(self.pl_token, "transfer",
                                         from_address, from_private_key,
                                         to_address,
                                         n_tokens)

    def upload(self, owner_address, owner_private_key,
               data_hash, price):
        """uploads file info on blockchain

           Args:
               owner_address (str): sellers address
               owner_private_key (str): sellers private key
               data_hash (str): file hash
               price (int): file cost
        """
        self._build_and_send_transaction(self.data_market, "uploadFile",
                                         owner_address, owner_private_key,
                                         price, bytes.fromhex(data_hash))

    def buy(self, consumer_address, consumer_private_key,
            data_hash, price):
        self._build_and_send_transaction(self.pl_token, "approve",
                                         consumer_address, consumer_private_key,
                                         self.dm_config.address, price)

        self._build_and_send_transaction(self.data_market, "buyFile",
                                         consumer_address, consumer_private_key,
                                         bytes.fromhex(data_hash))

    def get_data_market_events(self):
        return self.data_market.events.FileSold.get_logs(fromBlock=self.w3.eth.block_number)
