# DNS Server Usage Guide

This guide shows how to use the custom DNS server package in your project.

## Basic Usage

Here's a simple example of how to set up and run the DNS server:

```python
from dns import DNSServer, Zone
from pathlib import Path

# Method 1: Using TOML configuration
server = DNSServer.from_toml("zones.toml")
server.start()

# Method 2: Manual configuration
# Create a Zone object
zone = Zone.from_raw(1, {
    "domain": "example.com",
    "type": "A",
    "value": "192.168.1.1"
})

# Create server with basic resolver
server = DNSServer()
server.add_record(zone)
server.start()

# To stop the server
server.stop()
```

## TOML Configuration Example

Create a file named `zones.toml` with your DNS records:

```toml
[[zones]]
domain = "example.com"
type = "A"
value = "192.168.1.1"

[[zones]]
domain = "blog.example.com"
type = "CNAME"
value = "example.com"
```

## Advanced Usage

You can also use the proxy resolver to forward requests to an upstream DNS server:

```python
from dns import DNSServer

# Create a proxy resolver that forwards to Google DNS
server = DNSServer.from_toml(
    "zones.toml",
    resolver_type="proxy",
    upstream="8.8.8.8"
)
server.start()
```

## Server Management

```python
# Check if server is running
if server.is_running():
    print("Server is active")

# Update records while running
new_zone = Zone.from_raw(1, {
    "domain": "api.example.com",
    "type": "A",
    "value": "192.168.1.2"
})
server.add_record(new_zone)

# Replace all records
server.set_records([zone1, zone2])
```