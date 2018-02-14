#!/usr/bin/env python

from bitcoinrpc.authproxy import AuthServiceProxy
import decimal
from web3 import Web3, HTTPProvider, IPCProvider
import binascii


DATA_PREFIX = "LEGALPIN:"

STATUS_CONFIRMED = 0
STATUS_NOT_FOUND = 10
STATUS_IN_MEMPOOL = 20
STATUS_PARTIALLY_CONFIRMED = 30

class CryptoEngine:
    def __init__(self, engine_params: dict):
        raise NotImplementedError("Should have implemented this")

    def certify(self, data: bytes) -> str:
        raise NotImplementedError("Should have implemented this")

    def cert_status(self, txid: str):
        raise NotImplementedError("Should have implemented this")

    def check_cert(self, data: bytes):
        raise NotImplementedError("Should have implemented this")

    def generate_result(self, status=None, msg=None):
        if status is None:
            raise ValueError("Status cannot be None")

        result = {"status": status}

        if msg is not None:
            result["msg"] = msg

        return result

class CryptoEngineBitcoin(CryptoEngine):
    BITCOIN_FEE = 0.0001
    BITCOIN_FINAL_CONFIRMATIONS = 6

    def __init__(self, engine_params: dict):
        self.rpc = AuthServiceProxy(engine_params['url'])

    def certify(self, data: bytes) -> str:
        if len(data) != 32:
            raise ValueError("data length must be 32")

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
        print("# of unspent entries: %d" % len(unspent))
        for i in range(0, len(unspent)):
            ue = unspent[i]
            print("UE: %s" % ue)
            if ue['spendable'] and ue['amount'] >= self.BITCOIN_FEE:
                print("Spendable entry found: %s" % ue)
                target = ue
                break

        return target

    def __get_fee(self):
        pass

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

        result = super().generate_result(status, msg)

        return result

    def check_cert(self, data: bytes):
        pass


class CryptoEngineEthereum(CryptoEngine):
    def __init__(self, engine_params: dict):
        self.web3 = Web3(IPCProvider(engine_params.path))

    def __update_info(self):
        self.accounts = self.web3.eth.accounts
        self.block = self.web3.eth.getBlock('latest')
        self.accounts = self.web3.eth.accounts
        if len(self.accounts)>0:
            self.balance = self.web3.eth.getBalance(self.accounts[0])
        else:
            self.balance = 0

    def certify(self, data: bytes):
        self.__update_info()
        addr = self.accounts[0]
        tx = {'from': addr, 'to': addr, 'data': data}
        txid = self.web3.eth.sendTransaction(tx)
        txidStr = binascii.hexlify(txid).decode()
        return txidStr

    def check_cert(self, hash: bytes):
        pass





