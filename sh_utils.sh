### change DNS server for a network service
networksetup -listallnetworkservices
sudo networksetup -setdnsservers "Wi-Fi" 8.8.8.8 8.8.4.4
networksetup -getdnsservers "Wi-Fi"

### clear dns cache
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder


### check dns traffic
sudo tcpdump -i any port 53 -n 

### dns resolution
dig @localhost www.google.com +trace +short