import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from logger import create_logger

logger = create_logger()

#__________________ Load environment variables from .env file __________________
backend_dir = Path(__file__).parent.parent.parent.parent
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded .env from: {env_path}")
else:
    logger.error(f"Warning: .env file not found at {env_path}")
    # Fallback: try loading from current working directory
    load_dotenv()

#__________________ Validate required environment variables __________________
DB_HOST = os.getenv("AWS_RDS_ENDPOINT")
DB_PORT = int(os.getenv("AWS_RDS_PORT", "3306"))  # Default MySQL port
DB_NAME = os.getenv("AWS_RDS_NAME")
DB_USER = os.getenv("AWS_RDS_USERNAME")
DB_PASSWORD = os.getenv("AWS_RDS_PASSWORD")
required_vars = [DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]
missing_vars = [var for var in ['AWS_RDS_ENDPOINT', 'AWS_RDS_NAME', 'AWS_RDS_USERNAME', 'AWS_RDS_PASSWORD'] 
                if not os.getenv(var)]

if missing_vars:
    logger.error(f"Missing required environment variables: {missing_vars}")
    raise ValueError(f"Missing required environment variables: {missing_vars}")

#__________________ MySQL connection __________________
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger.info(f"Initializing database connection to MySQL RDS: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Recycle connections every hour
        pool_pre_ping=True,  # Verify connections before use
        echo=False,  # Set to True for SQL query logging in development
        connect_args={
            "charset": "utf8mb4",
            "connect_timeout": 60,
            "read_timeout": 30,
            "write_timeout": 30,
            "autocommit": True,  # Enable autocommit for DDL operations
        }
    )
    logger.info("MySQL database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
logger.info("Session factory configured")

Base = declarative_base()
logger.info("Base declarative class initialized")

def get_db():
    """Database dependency generator with logging"""
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        logger.debug("Yielding database session")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close()

def test_connection():
    """Test the database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def get_database_info():
    """Get information about the current database and tables"""
    try:
        with engine.connect() as connection:
            # Get current database
            current_db = connection.execute(text("SELECT DATABASE()")).fetchone()[0]
            
            # Get all tables
            tables_result = connection.execute(text("SHOW TABLES"))
            tables = [table[0] for table in tables_result.fetchall()]
            
            # Get database size
            size_result = connection.execute(text(f"""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'DB Size in MB'
                FROM information_schema.tables 
                WHERE table_schema = '{DB_NAME}'
            """)).fetchone()
            
            db_size = size_result[0] if size_result and size_result[0] else 0
            
            logger.info(f"Connected to database: {current_db}, Tables: {tables}, Size: {db_size} MB")
            
            return {
                "database": current_db,
                "tables": tables,
                "size_mb": db_size,
                "connection_successful": True
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {
            "database": None,
            "tables": [],
            "size_mb": 0,
            "connection_successful": False,
            "error": str(e)
        }

def create_tables():
    """Create all tables defined in the models"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        return False

logger.info("Database configuration completed")

# Test connection on import
if test_connection():
    db_info = get_database_info()
    logger.info(f"Database info: {db_info}")
else:
    logger.warning("Initial database connection test failed")