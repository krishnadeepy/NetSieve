from dnserver import DNSServer

server = DNSServer.from_toml('zones.toml', port=5053)
server.start()
assert server.is_running

# now you can do some requests with your favorite dns library

# server.stop()