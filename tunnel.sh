#!/bin/sh

# Obtener direccion de la instancia blockchain con el istatus
ADDRESS=$1

ssh -v ubuntu@${ADDRESS} -L8545:localhost:8545 -L8333:localhost:8333 -N
