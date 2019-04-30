# Blockchaincert API


This is a set of utilities to certify documents using blockchain

NOTE: This is an unfinished work in early state, you are welcome to
use it and contribute.


To certify a document:
======================

See the ```example_cert_btc``` and ```example_cert_eth```


API description:
================

```certify(data: bytes) -> str:```
----------------------------------

Certify a document


Parameters:
 - data: Document's hash to be certified in byte string, length can be up to 32 bytes

Return value:
Transaction ID



```cert_status(txid: str)```
----------------------------

Check the certification status of a document

Parameters:
 - txid: Transaction ID

Return value:

A dict like object with status fields that can be
 - STATUS_CONFIRMED: Transaction fully confirmed
 - STATUS_NOT_FOUND: Transaction not found
 - STATUS_IN_MEMPOOL: Transaction not yet mined
 - STATUS_PARTIALLY_CONFIRMED: Transaction in blockchain but with insufficient confirmations

```check_cert(data: bytes)```
-----------------------------

Check if specified document is already certified

Return value:
```True``` if it is ```False``` otherwise


```lock():```
-----------------
Locks the wallet



```unlock(self, password = None, timeout = None) -> bool```
-----------------------------------------------------------

Unlock wallet using the specified password

Parameters:
  - password: Unlock password
  - timeout: Amount of seconds it will remain unlocked

Return value:
```True``` if can be unlocked False otherwise


```is_locked(self) -> bool```
-----------------------------


Check if wallet is locked

Return value:
```True``` if it is blocked False otherwise

