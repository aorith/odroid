#!/bin/sh
# https://wiki.archlinux.org/index.php/Simple_stateful_firewall

# Esta maquina ya esta detras de otro firewall...
# solo quiero esto para el portknocking

iptables -F
iptables -X
iptables -Z

# port knocking chain
iptables -N OPEN_SESAME

# we aren't a NAT gateway
iptables -P FORWARD DROP

# default policy for output is accept
iptables -P OUTPUT ACCEPT

# default for input
iptables -P INPUT DROP

# basic rules
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -m conntrack --ctstate INVALID -j DROP

# redirigimos todo el nuevo trafico ssh a OPEN_SESAME
iptables -A INPUT -p tcp --dport 22 --syn -m conntrack --ctstate NEW -j OPEN_SESAME
iptables -A OPEN_SESAME -p tcp -s 192.168.0.0/16 --dport 22 -j ACCEPT
# rechazamos el trafico ssh que salga de la chain
iptables -A INPUT -p tcp --dport 22 -j DROP

# aceptamos el resto
iptables -A INPUT -j ACCEPT

echo "\nTo save the rules, run the following command:\niptables-save > /etc/iptables/rules.v4"
echo "\nTo RESET the rules, run the following command:\niptables -P INPUT ACCEPT && iptables -F"
