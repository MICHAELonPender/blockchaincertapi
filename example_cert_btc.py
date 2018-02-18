#!/usr/bin/env python

from crypto_cert.engine import CryptoEngineBitcoin
import sys

if __name__ == "__main__":
    engine = CryptoEngineBitcoin(url="http://test:test@localhost:8333")

    if engine.is_locked():
        print("Wallet is locked, trying to unlock it")
        result = engine.unlock(password = "clave", timeout = 120)
        if result:
            print("Wallet unlocked successfully")
        else:
            print("Cannot unlock the wallet, exiting")
            sys.exit(1)

    hash = "PRUEBA PAYLOAD BLOCKCHAIN 123456".encode()

    txid = engine.certify(hash)

    print("Sent to blockchain with txid:",txid)
    print("Check it out in explorer: https://live.blockcypher.com/btc-testnet/tx/%s" % txid)
    print("Waiting confirmations")

    engine.show_status_until_confirm(engine, txid)

    print("Result: https://live.blockcypher.com/btc-testnet/tx/%s" % txid)
