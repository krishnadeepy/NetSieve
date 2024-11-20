import time
from  dnserver import DNSServer 

srv = DNSServer.from_toml('./zone.toml',port=5053)
srv.start()

time.sleep(100000)
srv.stop()