import time
from  dns import DNSServer 

srv = DNSServer.from_toml('./refs.toml',port=53)
srv.start()

time.sleep(100000)
srv.stop()