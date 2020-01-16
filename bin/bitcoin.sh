#!/bin/bash
if [ "$1" = "stop" ]; then
	/usr/bin/bitcoin-cli -datadir=/media/datos/Bitcoin/ stop
elif [ "$1" = "start" ]; then
	/usr/bin/bitcoind -daemon -datadir=/media/datos/Bitcoin/ -walletdir=/home/aorith/.bitcoin/wallets/
elif [ "$1" = "reindex" ]; then
	/usr/bin/bitcoind -reindex -daemon -datadir=/media/datos/Bitcoin/ -walletdir=/home/aorith/.bitcoin/wallets/
fi
