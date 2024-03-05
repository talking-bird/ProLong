import os
import sqlite3
import pandas as pd

DATA_HASH = 'data_hash'
TX_HASH = 'tx_hash'
ACCOUNT_ADDRESS = 'account_address'
SHORT_DESCRIPTION = 'short_description'
IV = 'iv'
PRICE = 'price'

PUBLIC_KEY = 'public_key'

ENCRYPTED_KEY = 'encrypted_key'

DATABASE_FILE = 'database.db'
REGISTRY_FILE = 'registry.csv'
CUSTOMERS_FILE = 'customers.csv'
TRANSACTIONS = 'transactions.csv'

FILES_TABLE_STATEMENT = "CREATE TABLE IF NOT EXISTS files (" \
                        "   id integer PRIMARY KEY," \
                        "	data_hash text NOT NULL," \
                        "	account_address text NOT NULL," \
                        "	short_description text NOT NULL," \
                        "	iv text NOT NULL," \
                        "	price integer NOT NULL" \
                        ")"

INSERT_FILES_STATEMENT = "INSERT OR IGNORE INTO" \
                               " files(data_hash, account_address, short_description, iv, price)" \
                               " VALUES(?, ?, ?, ?, ?)"

SELECT_FILES_STATEMENT = "SELECT * from files"


class Storage:

    def __init__(self, path_to_data_storage):
        self.path_to_data_storage = path_to_data_storage
        self.database_path = os.path.join(self.path_to_data_storage, DATABASE_FILE)

    def add_file_to_storage(self, encrypted_data, encrypted_data_hash,
                            user_address):
        path_to_user_data_storage = os.path.join(self.path_to_data_storage, user_address)

        if not os.path.exists(path_to_user_data_storage):
            os.makedirs(path_to_user_data_storage)

        path_to_user_encrypted_data = os.path.join(path_to_user_data_storage, f"{encrypted_data_hash}.enc")

        with open(path_to_user_encrypted_data, "wb") as file:
            file.write(encrypted_data)

    def add_file(self, encrypted_data_hash, owner_address, short_description, iv, price):
        conn = open_database(self.database_path)

        create_records_table(conn)

        insert_to_table(conn,
                        encrypted_data_hash, owner_address, short_description, iv, price)

        conn.close()

    def add_transaction(self, customer_address, data_hash, encrypted_key):
        if not os.path.exists(self.transactions_path):
            data_frame = pd.DataFrame(columns=[ACCOUNT_ADDRESS,
                                               DATA_HASH,
                                               ENCRYPTED_KEY])

        else:
            data_frame = pd.read_csv(self.transactions_path, index_col=[0])

        if customer_address in data_frame[ACCOUNT_ADDRESS].values and \
                data_hash in data_frame[DATA_HASH].values:
            data_frame = data_frame.drop(data_frame[(data_frame[ACCOUNT_ADDRESS] == customer_address) &
                                                    (data_frame[DATA_HASH] == data_hash)].index)

        data_frame = data_frame.append({ACCOUNT_ADDRESS: customer_address,
                                        DATA_HASH: data_hash,
                                        ENCRYPTED_KEY: encrypted_key},
                                       ignore_index=True)

        data_frame.to_csv(self.transactions_path)

    def get_registry_record_by_idx(self, record_idx):
        return pd.read_csv(self.registry_path, index_col=[0]).iloc[record_idx]

    def get_files(self):
        conn = open_database(self.database_path)

        records = select_from_table(conn)

        conn.close()

        return records

    def get_registry_records_by_user_address(self, user_address):
        registry = pd.read_csv(self.registry_path, index_col=[0])

        return registry[registry[ACCOUNT_ADDRESS] == user_address]

    def get_public_key(self, customer_address):
        customers = pd.read_csv(self.customers_path, index_col=[0])

        return customers[customers[ACCOUNT_ADDRESS] == customer_address][[PUBLIC_KEY]].values[0][0]

    def get_encrypted_key(self, customer_address, data_hash):
        transactions = pd.read_csv(self.transactions_path, index_col=[0])

        return transactions[(transactions[ACCOUNT_ADDRESS] == customer_address) &
                            (transactions[DATA_HASH] == data_hash)][[ENCRYPTED_KEY]].values[0][0]

    def get_path_to_encrypted_file(self, account_address, data_hash):
        return os.path.join(self.path_to_data_storage, account_address, f"{data_hash}.enc")


"""
Support utils
"""


def open_database(database_path):
    try:
        conn = sqlite3.connect(database_path)

        return conn

    except Exception as e:
        print(e)


def create_records_table(conn):
    cursor = conn.cursor()
    cursor.execute(FILES_TABLE_STATEMENT)
    cursor.close()


def insert_to_table(conn,
                    data_hash, account_address, short_description, iv, price):
    cursor = conn.cursor()
    cursor.execute(INSERT_FILES_STATEMENT,
                   (data_hash, account_address, short_description, iv, price))
    conn.commit()
    cursor.close()


def select_from_table(conn):
    cursor = conn.cursor()

    cursor.execute(SELECT_FILES_STATEMENT)

    records = cursor.fetchall()

    cursor.close()

    return records


# def add_record(self, encrypted_data_hash, tx_hash, user_address, short_description, iv,
#                price):
#     if not os.path.exists(self.registry_path):
#         data_frame = pd.DataFrame(columns=[DATA_HASH,
#                                            TX_HASH,
#                                            ACCOUNT_ADDRESS,
#                                            SHORT_DESCRIPTION,
#                                            IV,
#                                            PRICE])
#
#     else:
#         data_frame = pd.read_csv(self.registry_path, index_col=[0])
#
#     if encrypted_data_hash in data_frame[DATA_HASH].values:
#         data_frame = data_frame.drop(data_frame[data_frame[DATA_HASH] == encrypted_data_hash].index)
#
#     data_frame = data_frame.append({DATA_HASH: encrypted_data_hash,
#                                     TX_HASH: tx_hash,
#                                     ACCOUNT_ADDRESS: user_address,
#                                     SHORT_DESCRIPTION: short_description,
#                                     IV: iv.hex(),
#                                     PRICE: price},
#                                    ignore_index=True)
#
#     data_frame.to_csv(self.registry_path)
# def add_customer(self, customer_address, public_key):
#     if not os.path.exists(self.customers_path):
#         data_frame = pd.DataFrame(columns=[ACCOUNT_ADDRESS,
#                                            PUBLIC_KEY])
#
#     else:
#         data_frame = pd.read_csv(self.customers_path, index_col=[0])
#
#     if customer_address in data_frame[ACCOUNT_ADDRESS].values:
#         data_frame = data_frame.drop(data_frame[data_frame[ACCOUNT_ADDRESS] == customer_address].index)
#
#     data_frame = data_frame.append({ACCOUNT_ADDRESS: customer_address,
#                                     PUBLIC_KEY: public_key},
#                                    ignore_index=True)
#
#     data_frame.to_csv(self.customers_path)
  # if not os.path.exists(self.registry_path):
        #     data_frame = pd.DataFrame(columns=[DATA_HASH,
        #                                        ACCOUNT_ADDRESS,
        #                                        SHORT_DESCRIPTION,
        #                                        IV,
        #                                        PRICE])
        #
        # else:
        #     data_frame = pd.read_csv(self.registry_path, index_col=[0])

        # if encrypted_data_hash in data_frame[DATA_HASH].values:
        #     data_frame = data_frame.drop(data_frame[data_frame[DATA_HASH] == encrypted_data_hash].index)
        #
        # data_frame = data_frame.append({DATA_HASH: encrypted_data_hash,
        #                                 ACCOUNT_ADDRESS: user_address,
        #                                 SHORT_DESCRIPTION: short_description,
        #                                 IV: iv.hex(),
        #                                 PRICE: price},
        #                                ignore_index=True)
        #
        # data_frame.to_csv(self.registry_path)