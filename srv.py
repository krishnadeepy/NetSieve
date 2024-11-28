import logging
from dnslib import DNSRecord, QTYPE, RR, DNSLabel, dns, RCODE
from dnslib.server import DNSRecord, BaseResolver as LibBaseResolver, DNSServer
from dnslib.server import DNSServer
from typing import Optional, Dict, Any
from models import HostEntry, SessionLocal
import socket, os, time
from config import DNS_PORT,EXPOSE_FLAG
from dotenv import load_dotenv

load_dotenv('.env.port')
DNS_PORT = int(os.getenv("PORT"))


if EXPOSE_FLAG:
    os.system('ufw allow 53/udp')
    os.system('ufw allow 53/tcp')


# Use well-known public DNS servers
DEFAULT_DNS = "1.1.1.1"  # Cloudflare
FALLBACK_DNS = "8.8.8.8"  # Google 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cloudflare and Google DNS Servers
CLOUDFLARE_DNS = "1.1.1.1"
GOOGLE_DNS = "8.8.8.8"

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
    def __init__(self, upstream_dns: str = DEFAULT_DNS):
        """Initialize resolver with block checker and upstream DNS."""
        super().__init__()
        self.block_checker = DBBlockZone()
        self.upstream_dns = upstream_dns
        logger.info(f"Initializing DNS resolver with primary DNS: {upstream_dns}, fallback: {FALLBACK_DNS}")

    def resolve(self, request, handler):
        """Resolve DNS requests, blocking listed domains."""

        print('\n%%%%%%%%%%%%%%%%%%%%%REQUEST%%%%%%%%%%%%%%%%%%%%%\n')
        print(request)
        print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')

        hostname = str(request.q.qname).rstrip('.')
        
        # First check if hostname is blocked in database
        if self.block_checker.match(request.q.qname):
            #logger.info(f"Blocking access to {hostname}")
            reply = request.reply()
            if request.q.qtype == QTYPE.A:
                reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=dns.A("0.0.0.0"), ttl=300))
            return reply

        # Try primary and fallback DNS servers
        logger.info(f"Forwarding query for {hostname}")
        dns_servers = [(self.upstream_dns, 53), (FALLBACK_DNS, 53)]
        
        for server in dns_servers:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(3)
                data = request.pack()
                sock.sendto(data, server)
                response_data, _ = sock.recvfrom(4096)
                response = DNSRecord.parse(response_data)
                print('\n%%%%%%%%%%%%%%%%%%%%%RESPONSE%%%%%%%%%%%%%%%%%%%%%\n')
                print(response)
                print('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')

                return response
            except (socket.timeout, socket.error) as e:
                logger.error(f"Failed to reach DNS server {server[0]}:53 - Error: {str(e)}")
                continue
            finally:
                if sock:
                    sock.close()

        logger.error("All DNS servers failed")
        reply = request.reply()
        reply.header.rcode = RCODE.SERVFAIL
        return reply
  


def start_dns_server(port: int = DNS_PORT):
    """Start the DNS server on the specified port.
    
    If port 53 requires elevated privileges, will automatically try port 10053.
    """
    dns_server = None
    try:
        # Create resolver
        resolver = CustomDNSResolver(upstream_dns=DEFAULT_DNS)
        
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
