#!/usr/bin/env python

from crypto_cert.engine import CryptoEngineEthereum
import sys

if __name__ == "__main__":
    engine = CryptoEngineEthereum(url="http://localhost:8545/")

    if not engine.unlock(password = "clave"):
        print("Account is not unlockable")
        sys.exit(1)

    hash = "PRUEBA PAYLOAD BLOCKCHAIN 123456".encode()

    txid = engine.certify(hash)

    print("Sent to blockchain with txid:",txid)
    print("Waiting confirmations")

    engine.show_status_until_confirm(engine, txid)
