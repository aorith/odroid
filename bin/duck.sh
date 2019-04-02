TOKEN="$(sed -n '1p' /home/aorith/secret/duckdns.txt)"
DOM1="$(sed -n '2p' /home/aorith/secret/duckdns.txt)"
DOM2="$(sed -n '3p' /home/aorith/secret/duckdns.txt)"

output=$(curl -k -s "https://www.duckdns.org/update?domains=$DOM1&token=$TOKEN&ip=")
if [ "$output" != "OK" ]; then
    /home/aorith/bin/telmsg.sh "$(date +'%Y%m%d %H:%M:%S') -> duckdns failed on $DOM1"
fi

output=$(curl -k -s "https://www.duckdns.org/update?domains=$DOM2&token=$TOKEN&ip=")
if [ "$output" != "OK" ]; then
    /home/aorith/bin/telmsg.sh "$(date +'%Y%m%d %H:%M:%S') -> duckdns failed on $DOM2"
fi
