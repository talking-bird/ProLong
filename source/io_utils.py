import os
import sqlite3


DATABASE_FILE = 'database.db'
KEY_DATABASE_FILE = 'keys.db'


class Storage:

    def __init__(self, path_to_data_storage):
        self.path_to_data_storage = path_to_data_storage
        self.database_path = os.path.join(self.path_to_data_storage, DATABASE_FILE)

        conn = open_database(self.database_path)

        create_files_table(conn)
        create_consumers_table(conn)
        create_transactions_table(conn)

        conn.close()

    def add_file_to_storage(self, encrypted_data, data_hash,
                            user_address):
        path_to_user_data_storage = os.path.join(self.path_to_data_storage, user_address)

        if not os.path.exists(path_to_user_data_storage):
            os.makedirs(path_to_user_data_storage)

        path_to_user_encrypted_data = os.path.join(path_to_user_data_storage, f"{data_hash}.enc")

        with open(path_to_user_encrypted_data, "wb") as file:
            file.write(encrypted_data)

    def add_file(self, data_hash, owner_address, short_description, iv, price):
        conn = open_database(self.database_path)

        insert_to_files(conn,
                        data_hash, owner_address, short_description, iv, price)

        conn.close()

    def add_consumer(self, consumer_address, consumer_public_key):
        conn = open_database(self.database_path)

        insert_to_consumers(conn,
                            consumer_address, consumer_public_key)

        conn.close()

    def add_transaction(self, consumer_address, owner_address, data_hash, encrypted_key):
        conn = open_database(self.database_path)

        insert_to_transactions(conn,
                               consumer_address, owner_address, data_hash, encrypted_key)

        conn.close()

    def get_files(self):
        conn = open_database(self.database_path)

        records = select_files(conn)

        conn.close()

        return records

    def has_file(self, data_hash):
        conn = open_database(self.database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id from files WHERE data_hash = ?",
                       (data_hash,))

        records = cursor.fetchall()

        cursor.close()
        conn.close()

        return len(records) != 0

    def get_public_key(self, consumer_address):
        conn = open_database(self.database_path)

        records = select_public_key(conn,
                                    consumer_address)

        conn.close()

        return records

    def get_encrypted_key(self, consumer_address, data_hash):
        conn = open_database(self.database_path)

        records = select_encrypted_key(conn,
                                       consumer_address, data_hash)

        conn.close()

        return records

    def get_iv(self, data_hash):
        conn = open_database(self.database_path)

        records = select_files(conn,
                               data_hash=data_hash)

        conn.close()

        return records

    def get_path_to_encrypted_file(self, account_address, data_hash):
        return os.path.join(self.path_to_data_storage, account_address, f"{data_hash}.enc")


class KeyStorage:

    def __init__(self):
        self.database_path = os.path.join(os.path.abspath(os.getcwd()), KEY_DATABASE_FILE)

        conn = open_database(self.database_path)

        create_keys_table(conn)

        conn.close()

    def add_key(self, data_hash, key):
        conn = open_database(self.database_path)

        insert_to_keys(conn, data_hash, key)

        conn.close()

    def get_key(self, data_hash):
        conn = open_database(self.database_path)

        records = select_key(conn, data_hash)

        conn.close()

        return records


"""
Support utils
"""


def open_database(database_path):
    try:
        conn = sqlite3.connect(database_path)

        return conn

    except Exception as e:
        print(e)


def create_files_table(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS files ("
                   " id integer PRIMARY KEY,"
                   " data_hash text UNIQUE NOT NULL,"
                   " account_address text NOT NULL,"
                   " short_description text NOT NULL,"
                   " iv text NOT NULL,"
                   " price integer NOT NULL"
                   ")")
    cursor.close()


def create_consumers_table(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS consumers("
                   " id integer PRIMARY KEY,"
                   " account_address text UNIQUE NOT NULL,"
                   " public_key blob NOT NULL"
                   ")")
    cursor.close()


def create_transactions_table(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions("
                   " id integer PRIMARY KEY,"
                   " consumer_address text UNIQUE NOT NULL,"
                   " owner_address text UNIQUE NOT NULL,"
                   " data_hash text UNIQUE NOT NULL,"
                   " encrypted_key blob NOT NULL"
                   ")")
    cursor.close()


def insert_to_files(conn,
                    data_hash, account_address, short_description, iv, price):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO"
                   " files(data_hash, account_address, short_description, iv, price)"
                   " VALUES(?, ?, ?, ?, ?)",
                   (data_hash, account_address, short_description, iv, price))
    conn.commit()
    cursor.close()


def insert_to_consumers(conn,
                        account_address, public_key):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO"
                   " consumers(account_address, public_key)"
                   " VALUES(?, ?)",
                   (account_address, public_key))

    conn.commit()
    cursor.close()


def insert_to_transactions(conn,
                           consumer_address, owner_address, data_hash, encrypted_key):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO"
                   " transactions(consumer_address, owner_address, data_hash, encrypted_key)"
                   " VALUES(?, ?, ?, ?)",
                   (consumer_address, owner_address, data_hash, encrypted_key))
    conn.commit()
    cursor.close()


def select_files(conn,
                 data_hash=None):
    cursor = conn.cursor()

    if data_hash is None:
        cursor.execute("SELECT * from files")

    else:
        cursor.execute("SELECT iv from files WHERE data_hash = ?", (data_hash,))

    records = cursor.fetchall()

    cursor.close()

    return records


def select_public_key(conn,
                      consumer_address):
    cursor = conn.cursor()

    cursor.execute("SELECT public_key from consumers WHERE account_address = ?", (consumer_address,))

    records = cursor.fetchall()

    cursor.close()

    return records


def select_encrypted_key(conn,
                         consumer_address, data_hash):
    cursor = conn.cursor()

    cursor.execute("SELECT encrypted_key from transactions WHERE consumer_address = ? and data_hash = ?",
                   (consumer_address, data_hash))

    records = cursor.fetchall()

    cursor.close()

    return records


def create_keys_table(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS keys("
                   " id integer PRIMARY KEY,"
                   " data_hash text UNIQUE NOT NULL,"
                   " key blob UNIQUE NOT NULL"
                   ")")
    cursor.close()


def insert_to_keys(conn,
                   data_hash, key):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO"
                   " keys(data_hash, key)"
                   " VALUES(?, ?)",
                   (data_hash, key))

    conn.commit()
    cursor.close()


def select_key(conn,
               data_hash):
    cursor = conn.cursor()

    cursor.execute("SELECT key from keys WHERE data_hash = ?",
                   (data_hash,))

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
# def add_transaction(self, customer_address, data_hash, encrypted_key):
#     if not os.path.exists(self.transactions_path):
#         data_frame = pd.DataFrame(columns=[ACCOUNT_ADDRESS,
#                                            DATA_HASH,
#                                            ENCRYPTED_KEY])
#
#     else:
#         data_frame = pd.read_csv(self.transactions_path, index_col=[0])
#
#     if customer_address in data_frame[ACCOUNT_ADDRESS].values and \
#             data_hash in data_frame[DATA_HASH].values:
#         data_frame = data_frame.drop(data_frame[(data_frame[ACCOUNT_ADDRESS] == customer_address) &
#                                                 (data_frame[DATA_HASH] == data_hash)].index)
#
#     data_frame = data_frame.append({ACCOUNT_ADDRESS: customer_address,
#                                     DATA_HASH: data_hash,
#                                     ENCRYPTED_KEY: encrypted_key},
#                                    ignore_index=True)
#
#     data_frame.to_csv(self.transactions_path)
# def get_registry_record_by_idx(self, record_idx):
#     return pd.read_csv(self.registry_path, index_col=[0]).iloc[record_idx]
# def get_files_by_owner_address(self, owner_address):
#     conn = open_database(self.database_path)
#
#     cursor = conn.cursor()
#
#     cursor.execute("select * from files where account_address = ?", (owner_address,))
#     records = cursor.fetchall()
#
#     cursor.close()
#
#     conn.close()
#
#     return records
# def get_public_key(self, customer_address):
#     customers = pd.read_csv(self.customers_path, index_col=[0])
#
#     return customers[customers[ACCOUNT_ADDRESS] == customer_address][[PUBLIC_KEY]].values[0][0]
#
# def get_encrypted_key(self, customer_address, data_hash):
#     transactions = pd.read_csv(self.transactions_path, index_col=[0])
#
#     return transactions[(transactions[ACCOUNT_ADDRESS] == customer_address) &
#                         (transactions[DATA_HASH] == data_hash)][[ENCRYPTED_KEY]].values[0][0]
#
