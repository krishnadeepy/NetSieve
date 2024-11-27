from sqlalchemy import Column, Integer, String, Index, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv('.env.prod')

# Get database configuration from environment variables
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables if they don't exist
# Base.metadata.create_all(bind=engine)
