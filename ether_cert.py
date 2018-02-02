#!/usr/bin/env python

from web3 import Web3, HTTPProvider, IPCProvider
from functools import reduce
import sys
import time
import binascii

class LegalEther:
    def __init__(self):
        self.accounts = None
        self.block = None
        self.syncStatus = None
        self.peers = None
        self.accounts = None
        self.balance = None
        #self.web3 = Web3(HTTPProvider(endpoint_uri='http://192.168.1.5:8545'))
        #self.web3 = Web3(HTTPProvider(endpoint_uri='https://mainnet.infura.io'))
        #self.web3 = Web3(IPCProvider("/home/freemind/.ethereum/testnet/geth.ipc"))
        self.web3 = Web3(IPCProvider("/home/freemind/.local/share/io.parity.ethereum/jsonrpc.ipc"))

    def new_block_callback(self, block_hash):
        sys.stdout.write("New Block: {0}".format(block_hash))

    def updateCounters(self):
        self.accounts = self.web3.eth.accounts
        self.block = self.web3.eth.getBlock('latest')
        #self.syncStatus =self. web3.eth.syncing
        #self.peers = self.web3.admin.peers
        self.accounts = self.web3.eth.accounts
        if len(self.accounts)>0:
            self.balance = self.web3.eth.getBalance(self.accounts[0])
        else:
            self.balance = 0


        #self.hashrate = web3.eth.hashrate
        #self.nodeInfo = web3.admin.nodeInfo

    def unlockAccount(self):
        addr = self.accounts[0]
        print("Address:",addr)
        result = self.web3.personal.unlockAccount('0x004D17C3dDB92Df703466728720068592D5A6288', 'clave')
        print("Unlock Account:",result)

    def showProgress(self):
        self.updateCounters()
        syncStatusStr = "Sync status..: {0} / {1} ({2:.2f}%)"
        currentBlockBalance = "Current block: {0} / Balance: {1}"
        # print("Peers........:", len(self.peers))

        print("Accounts.....:", self.accounts)

        #while self.syncStatus == False or self.syncStatus.currentBlock <= self.syncStatus.highestBlock:
        print()
        while True:
            #print("Current block / Balance:", self.block.number)
            #print("Balance......:", self.balance)
            #if self.syncStatus == False:
            #    print("Sync status..: Not syncing", end="")
            #else:
            #    print(syncStatusStr.format(self.syncStatus.currentBlock, self.syncStatus.highestBlock, (self.syncStatus.currentBlock/self.syncStatus.highestBlock) * 100 ), end="")

            fmtCB = currentBlockBalance.format(self.block.number, self.balance/1000000000000000000)
            print(fmtCB, end='\r')
            #print(fmtCB)
            time.sleep(1)
            self.updateCounters()
        print("Sync finished")

    def getTransaction(self):
        tx = self.web3.eth.getTransaction("5a2c5117cf32e743fc3b71c7445ca99c3cb76e27a61de46c9d520eb015422106");
        print("TX:",tx)


    def createTransaction(self):
        addr = self.accounts[0]
        print("Default account:",addr)
        tx = {'from': addr, 'to': addr, 'data': b'LEGALCERT * MENSAJE EN TRANSACCION *'};
        txid = self.web3.eth.sendTransaction(tx)
        txidStr = binascii.hexlify(txid).decode()
        print("Resultado:", txidStr)
        return tx


    def toHex(s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0' + hv
            lst.append(hv)

        return reduce(lambda x, y: x + y, lst)

if __name__ == '__main__':
    legalEther = LegalEther()
    legalEther.updateCounters()
    legalEther.unlockAccount()
    #legalEther.getTransaction()
    legalEther.createTransaction()
    legalEther.showProgress()
