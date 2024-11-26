import dns
import time

s = dns.DNSServer.from_toml('zones.toml',port=53)
s.start()

time.sleep(10000000)

