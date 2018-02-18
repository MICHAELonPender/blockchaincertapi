#!/usr/bin/env python

from crypto_cert.engine import CryptoEngineEthereum
import sys

if __name__ == "__main__":
    engine = CryptoEngineEthereum(url="http://localhost:8545/")

    if engine.is_locked():
        print("Wallet is locked, trying to unlock it")
        result = engine.unlock(password = "clave")
        if result:
            print("Wallet unlocked successfully")
        else:
            print("Cannot unlock the wallet, exiting")
            sys.exit(1)

    hash = "PRUEBA PAYLOAD BLOCKCHAIN 123456".encode()

    txid = engine.certify(hash)

    print("Sent to blockchain with txid:",txid)
    print("Check it out in explorer: https://ropsten.etherscan.io/tx/%s" % txid)
    print("Waiting confirmations")

    engine.show_status_until_confirm(engine, txid)

    print("Result: https://ropsten.etherscan.io/tx/%s" % txid)