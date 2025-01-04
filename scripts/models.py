import os
import socket
from dotenv import load_dotenv
from dns import resolver


from sqlalchemy import Column, Integer, String, Index, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

dns_resolver = resolver.Resolver(configure=False)
dns_resolver.nameservers = ['8.8.8.8']

# Custom hostname resolution function
def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host:
        answer = dns_resolver.resolve(host, 'A')  # Resolve A record
        ip = answer[0].to_text()  # Get resolved IP address
        return [(socket.AF_INET, socket.SOCK_STREAM, proto, '', (ip, port))]
    return original_getaddrinfo(host, port, family, type, proto, flags)

# Backup original resolver function
original_getaddrinfo = socket.getaddrinfo

# Override resolver
socket.getaddrinfo = custom_getaddrinfo

load_dotenv('.env.prod')




# Get database configuration from environment variables
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

try:
    resolved_ip = dns_resolver.resolve(DATABASE_HOST, 'A')[0].to_text()
    #print(f"Resolved {DATABASE_HOST} to {resolved_ip} using Google DNS 8.8.8.8")
    DATABASE_HOST = resolved_ip
except Exception as e:
    print(f"Error resolving {DATABASE_HOST}: {e}")

socket.getaddrinfo = original_getaddrinfo



Base = declarative_base()

class HostEntry(Base):
    __tablename__ = 'host_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String, nullable=False)
    hostname = Column(String, nullable=False)
    category = Column(String, nullable=False)

    # Add an index on the 'hostname' column for better performance
    __table_args__ = (
        Index('idx_hostname', 'hostname'),  # 'idx_hostname' is the name of the index
    )

# Construct the DATABASE_URL dynamically
DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
DATABASE_URL = (
    f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    f"?options=endpoint%3D{os.getenv('DATABASE_HOST').split('.')[0]}&sslmode=require"
)

engine = create_engine(DATABASE_URL,pool_size=100, max_overflow=100)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create the database tables if they don't exist
# Base.metadata.create_all(bind=engine)


try:
    with engine.connect() as connection:
        print("DB Connection successful!")
        # result = connection.execute(text("SELECT 1;"))
        # print(f"Query Result: {result.fetchall()}")
except Exception as e:
    print(f"Error connecting to the database: {e}")