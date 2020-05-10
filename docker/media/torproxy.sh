#!/usr/bin/env bash

echo "
user-manual /usr/share/doc/privoxy/user-manual/
confdir /etc/privoxy
logdir /var/log/privoxy
filterfile default.filter
listen-address  :8118
toggle  1
enable-remote-toggle  0
enable-remote-http-toggle  0
enable-edit-actions 0
enforce-blocks 0
buffer-limit 4096
enable-proxy-authentication-forwarding 0
trusted-cgi-referer http://www.example.org/
forward-socks5t / 127.0.0.1:9050 .
forward 172.16.*.*/ .
forward 172.17.*.*/ .
forward 172.18.*.*/ .
forward 172.19.*.*/ .
forward 172.20.*.*/ .
forward 172.21.*.*/ .
forward 172.22.*.*/ .
forward 172.23.*.*/ .
forward 172.24.*.*/ .
forward 172.25.*.*/ .
forward 172.26.*.*/ .
forward 172.27.*.*/ .
forward 172.28.*.*/ .
forward 172.29.*.*/ .
forward 172.30.*.*/ .
forward 172.31.*.*/ .
forward 10.*.*.*/ .
forward 192.168.*.*/ .
forward 127.*.*.*/ .
forward localhost/ .
forwarded-connect-retries  0
accept-intercepted-requests 1
allow-cgi-request-crunching 0
split-large-forms 0
keep-alive-timeout 5
tolerate-pipelining 1
socket-timeout 300
log-messages   1
log-highlight-messages 1
" > /etc/privoxy/config

echo "
User tor
RunAsDaemon 0
ControlPort 9051
DataDirectory /var/lib/tor
ControlSocket /etc/tor/run/control
ControlSocketsGroupWritable 1
CookieAuthentication 1
CookieAuthFileGroupReadable 1
ExtORPortCookieAuthFileGroupReadable 1
CookieAuthFile /etc/tor/run/control.authcookie
AutomapHostsOnResolve 1
ExitPolicy reject *:*
VirtualAddrNetworkIPv4 10.192.0.0/10
SocksPort 0.0.0.0:9050 IsolateDestAddr
TransPort 0.0.0.0:9040
DNSPort 5353

# Configure a service to run under TOR
#HiddenServiceDir /var/lib/tor/bitcoin-service/
#HiddenServicePort 8333 127.0.0.1:8333
" > /etc/tor/torrc

mkdir -p /etc/tor/run
chmod 0750 /etc/tor/run
chown -R tor /etc/tor /var/lib/tor /var/log/tor /etc/tor/run
chown -R privoxy:privoxy /etc/privoxy

if ps -ef | egrep -v 'grep|torproxy.sh' | grep -q tor
then
    echo "Tor service is already running"
else
    /usr/sbin/privoxy --user privoxy /etc/privoxy/config
    exec /usr/bin/tor
fi
