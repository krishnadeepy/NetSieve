import logging
from dnslib import DNSRecord, QTYPE, RR, DNSLabel, dns
from dnslib.server import DNSRecord, BaseResolver as LibBaseResolver, DNSServer
from dnslib.server import DNSServer
from typing import Optional, Dict, Any
import socket
import time
from config import DNS_PORT, CLOUDFLARE_DNS, GOOGLE_DNS 
from models import HostEntry, SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cloudflare and Google DNS Servers
CLOUDFLARE_DNS = "1.1.1.1"
GOOGLE_DNS = "8.8.8.8"
DNS_PORT = 53


class DBBlockZone:
    """A class that checks if domains are blocked in the database."""
    def __init__(self):
        # No need to call parent class init since we're only using the database
        self._cache: Dict[str, bool] = {}

    def match(self, q) -> bool:
        """Match a query against blocked hostnames in the database."""
        hostname = str(q).rstrip('.')
        
        # Check cache first
        if hostname in self._cache:
            return self._cache[hostname]
            
        # Query database
        with SessionLocal() as db_session:
            is_blocked = db_session.query(HostEntry).filter(HostEntry.hostname == hostname).first() is not None
            self._cache[hostname] = is_blocked
            return is_blocked

    def sub_match(self, q) -> Optional[Any]:
        """Check subdomains of blocked domains."""
        hostname = str(q).rstrip('.')
        parts = hostname.split('.')
        
        # Try each subdomain level
        for i in range(len(parts) - 1):
            domain = '.'.join(parts[i:])
            if self.match(domain):
                return True
                
        return None

class CustomDNSResolver(LibBaseResolver):
    def __init__(self, upstream_dns: str = CLOUDFLARE_DNS):
        """Initialize resolver with block checker and upstream DNS."""
        super().__init__()
        self.block_checker = DBBlockZone()
        self.upstream_dns = upstream_dns

    def resolve(self, request, handler):
        """Resolve DNS requests, blocking listed domains."""
        hostname = str(request.q.qname).rstrip('.')
        
        # First check if hostname is blocked in database
        if self.block_checker.match(request.q.qname):
            logger.info(f"Blocking access to {hostname}")
            reply = request.reply()
            if request.q.qtype == QTYPE.A:
                reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=dns.A("0.0.0.0"), ttl=300))
            return reply

        # If not blocked, forward to upstream DNS
        logger.info(f"Forwarding query for {hostname}")
        try:
            # Create a new socket for upstream DNS query
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)  # 3 second timeout
            # Forward the raw query
            sock.sendto(request.pack(), (self.upstream_dns, 53))
            # Get the response
            data, _ = sock.recvfrom(4096)
            response = DNSRecord.parse(data)
            return response
        except Exception as e:
            logger.error(f"Error resolving DNS query: {e}")
            reply = request.reply()
            reply.header.rcode = 2  # SERVFAIL
            return reply
        finally:
            sock.close()
  


def start_dns_server(port: int = DNS_PORT):
    """Start the DNS server on the specified port.
    
    If port 53 requires elevated privileges, will automatically try port 10053.
    """
    dns_server = None
    try:
        # Create resolver
        resolver = CustomDNSResolver(upstream_dns=CLOUDFLARE_DNS)
        
        # Create and configure server
        dns_server = DNSServer(
            resolver=resolver,
            port=port,
            address="0.0.0.0"
        )
        
        logger.info(f"Starting DNS server on port {port}...")
        dns_server.start_thread()
        
        # Keep the server running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down DNS server...")
            
    except PermissionError:
        if port == DNS_PORT:
            alt_port = 10053
            logger.warning(f"Permission denied. Trying alternate port {alt_port}")
            start_dns_server(port=alt_port)
            return
        raise
        
    finally:
        if dns_server:
            dns_server.stop()


if __name__ == "__main__":
    start_dns_server()
