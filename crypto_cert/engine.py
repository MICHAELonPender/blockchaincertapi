#!/usr/bin/env python

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from web3 import Web3, HTTPProvider, IPCProvider
from crypto_cert.engine import *
import decimal
import binascii
import time
from abc import ABC, abstractmethod


DATA_PREFIX = "LEGALPIN:"

STATUS_CONFIRMED = 0
STATUS_NOT_FOUND = 10
STATUS_IN_MEMPOOL = 20
STATUS_PARTIALLY_CONFIRMED = 30


class CryptoEngine(ABC):
    @abstractmethod
    def __init__(self, url=None, path=None):
        pass

    @abstractmethod
    def certify(self, data: bytes) -> str:
        pass

    @abstractmethod
    def cert_status(self, txid: str):
        pass

    @abstractmethod
    def check_cert(self, data: bytes):
        pass

    @abstractmethod
    def unlock(self, password = None, timeout = None) -> bool:
        pass

    @abstractmethod
    def is_locked(self) -> bool:
        pass

    def generate_result(self, status = None, msg = None, confirmations = None):
        if status is None:
            raise ValueError("Status cannot be None")

        result = {"status": status}

        if msg is not None:
            result["msg"] = msg

        if confirmations is not None:
            result["confirmations"] = confirmations

        return result

    @staticmethod
    def minify_tx(txid: str) ->str:
        if len(txid) > 14:
            return txid[:6]+".."+txid[-6:]

        return txid

    def show_status_until_confirm(self, obj, txid: str) -> str:
        while True:
            result = obj.cert_status(txid)

            ts = time.time()
            if result is None:
                print("Result is none")
            else:
                print("Status: TS: %d: %s: %s" % (ts, obj.minify_tx(txid), result["msg"]))

            if result is None or result['status'] == STATUS_CONFIRMED:
                break

            time.sleep(1)

        if result is not None:
            print("Final result for: %s: %s" % (txid, result["msg"]))



class CryptoEngineBitcoin(CryptoEngine):
    BITCOIN_FEE = 0.0001
    BITCOIN_FINAL_CONFIRMATIONS = 6

    def __init__(self, url=None, path=None):
        super().__init__()
        self.rpc = AuthServiceProxy(url)

    def certify(self, data: bytes) -> str:
        if len(data) <1 or len(data) > 32:
            raise ValueError("data length must be > 0 and <= 32")

        blockchain_payload = DATA_PREFIX.encode() + data

        avail_coin = self.__get_available_coin()
        if avail_coin is None:
            raise ValueError("No coin available")

        inputs = [{'txid': avail_coin['txid'], 'vout': avail_coin['vout']}]
        outputs = {'data': binascii.hexlify(blockchain_payload).decode(), avail_coin['address']: avail_coin['amount'] - decimal.Decimal(self.BITCOIN_FEE)}
        rawtrans = self.rpc.createrawtransaction(inputs, outputs)
        #print("RAW Transaction: %s" % rawtrans)

        signedtrans = self.rpc.signrawtransaction(rawtrans)
        #print("Signed transaction: %s" % signedtrans)

        if not signedtrans['complete']:
            raise RuntimeError("Error signing transaction: %s" % (signedtrans))

        txid = self.rpc.sendrawtransaction(signedtrans['hex'])
        #print("Transaction sent, TXID: %s" % txid)

        return txid

    def __get_available_coin(self):
        unspent = self.rpc.listunspent()
        target = None;
        #print("# of unspent entries: %d" % len(unspent))
        for i in range(0, len(unspent)):
            ue = unspent[i]
            #print("UE: %s" % ue)
            if ue['spendable'] and ue['amount'] >= self.BITCOIN_FEE:
                #print("Spendable entry found: %s" % ue)
                target = ue
                break

        return target

    def __get_fee(self):
        pass

    def check_cert(self, data: bytes):
        return True

    def cert_status(self, txid: str):
        tx = self.rpc.gettransaction(txid)
        if tx is None:
            return self.generate_result(STATUS_NOT_FOUND, "TX not found")

        confirmations = tx['confirmations']

        status = -1
        msg = None

        if confirmations == 0:
            status = STATUS_IN_MEMPOOL
            msg = "In mempool"
        elif confirmations < self.BITCOIN_FINAL_CONFIRMATIONS:
            status = STATUS_PARTIALLY_CONFIRMED
            msg = "Partially confirmed: %d" % confirmations
        else:
            status = STATUS_CONFIRMED
            msg = "Confirmed: %d" % confirmations

        result = super().generate_result(status, msg, confirmations)

        return result

    def unlock(self, password = None, timeout = None) -> bool:
        return self.rpc.walletpassphrase(password, timeout)

    def lock(self):
        return self.rpc.walletlock()

    def is_locked(self) -> bool:
        code = None
        try:
            self.rpc.signmessage("", "")
        except JSONRPCException as err:
            code = err.code

        if code is None or code == -3:
            return False

        return True


class CryptoEngineEthereum(CryptoEngine):
    ETHEREUM_FINAL_CONFIRMATIONS = 10

    def __init__(self, url=None, path=None):
        super().__init__()
        if path is not None:
            self.web3 = Web3(IPCProvider(path))
        elif url is not None:
            self.web3 = Web3(HTTPProvider(url))

    def __get_account(self):
        accounts = self.web3.eth.accounts
        return accounts[0]

    def certify(self, data: bytes):
        if len(data) <1 or len(data) > 32:
            raise ValueError("data length must be > 0 and <= 32")

        addr = self.__get_account()
        blockchain_payload = DATA_PREFIX.encode() + data
        tx = {'from': addr, 'to': addr, 'data': blockchain_payload}
        txid = self.web3.eth.sendTransaction(tx)
        txidStr = binascii.hexlify(txid).decode()
        return txidStr

    def cert_status(self, txid: str):
        status = -1
        msg = None
        tx = self.web3.eth.getTransaction(txid)
        #print("TX:",tx)
        tx_block_number = tx['blockNumber']
        latest_block_number = self.web3.eth.blockNumber

        #print("Latest block number",latest_block_number)
        #print("TX block number",tx_block_number)

        if tx_block_number is None:
            confirmations = 0
        else:
            confirmations = latest_block_number - tx_block_number + 1

        if confirmations == 0:
            status = STATUS_IN_MEMPOOL
            msg = "In mempool"
        elif confirmations < self.ETHEREUM_FINAL_CONFIRMATIONS:
            status = STATUS_PARTIALLY_CONFIRMED
            msg = "Partially confirmed: %d" % confirmations
        else:
            status = STATUS_CONFIRMED
            msg = "Confirmed: %d" % confirmations

        result = super().generate_result(status, msg, confirmations)

        return result

    def check_cert(self, data: bytes):
        return True

    def unlock(self, password = None, timeout=None) -> bool:
        return self.web3.personal.unlockAccount(self.__get_account(), password)

    def lock(self):
        return self.rpc.walletlock()

    def is_locked(self) -> bool:
        self.web3.eth.sign("", self.__get_account())
