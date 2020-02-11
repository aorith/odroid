#!/bin/bash
re='^[0-9]+$'
[[ "$1" =~ $re ]] && delay=$1 || delay=30
echo "Rules will be active for $delay seconds."
sudo -- sh -c "./bin/nftables.ruleset; sleep $delay; nft flush ruleset"
