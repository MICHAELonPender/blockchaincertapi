#!/usr/bin/env python

from bitcoinrpc.authproxy import AuthServiceProxy
import binascii
import decimal
import sys

BITCOIN_FEE = 0.001
DATA = 'LEGALCERT: PRUEBA 12345'
#DATA = 'LEGALCERT: PRUEBA 12345 MAS LARGO AUN'

rpc = AuthServiceProxy("http://test:test@127.0.0.1:8484")
info = rpc.getblockchaininfo()
print("Info: %s" % info)

unspent = rpc.listunspent()
target = None;
print("# of unspent entries: %d" % len(unspent))
for i in range (0, len(unspent)):
    ue = unspent[i]
    print("UE: %s" % ue)
    if ue['spendable'] and ue['amount'] >= BITCOIN_FEE:
        print("Spendable entry found: %s" % ue)
        target = ue
        break

inputs = [{'txid': ue['txid'], 'vout': ue['vout']}]
outputs = {'data': binascii.hexlify(DATA.encode()).decode(), ue['address']: ue['amount'] - decimal.Decimal(BITCOIN_FEE)}

rawtrans = rpc.createrawtransaction(inputs, outputs)
print("RAW Transaction: %s" % rawtrans)

signedtrans = rpc.signrawtransaction(rawtrans)
print("Signed transaction: %s" % signedtrans)

if not signedtrans['complete']:
    print("Error signing transaction: %s" % (signedtrans))
    sys.exit(1)

txid = rpc.sendrawtransaction(signedtrans['hex'])
print("Transaction sent, TXID: %s" % txid)

