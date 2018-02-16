#!/bin/sh

ADDRESS=54.194.41.161

ssh -v ubuntu@${ADDRESS} -L8545:localhost:8545 -L8333:localhost:8333 -N
