#!/usr/bin/env python

from crypto_cert.engine import CryptoEngineBitcoin
import time

if __name__ == "__main__":
    engine = CryptoEngineBitcoin(url="http://test:test@localhost:8333")

    engine.lock()
    print("Is Locked:",engine.is_locked())
    result = engine.unlock(password = "clave", timeout = 120)
    print("Is Locked:",engine.is_locked())

    hash = "PRUEBA PAYLOAD BLOCKCHAIN 123456".encode()

    txid = engine.certify(hash)

    print("Sent to blockchain with txid:",txid)
    print("Waiting confirmations")

    engine.show_status_until_confirm(engine, txid)
