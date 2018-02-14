#!/usr/bin/env python

from crypto_cert.engine import CryptoEngineBitcoin
import time

if __name__ == "__main__":
    params = {
        "url": "http://test:test@127.0.0.1:8383"
    }

    engine = CryptoEngineBitcoin(params)

    hash = "PRUEBA PAYLOAD BLOCKCHAIN 123456".encode()

    txid = engine.certify(hash)

    print("Sent to blockchain with txid:",txid)
    print("Waiting confirmations")

    while True:
        status = engine.cert_status(txid)
        ts = time.time()
        print("Status: %d: %s: %s" % (ts, txid, status["msg"]))
        time.sleep(1)

