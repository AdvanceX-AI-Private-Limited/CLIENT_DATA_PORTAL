import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from logger import create_logger

logger = create_logger(__name__)

#__________________ Load environment variables from .env file __________________
env = load_dotenv('.env')

#__________________ Validate required environment variables __________________
DB_HOST = os.getenv("AWS_RDS_ENDPOINT")
DB_PORT = int(os.getenv("AWS_RDS_PORT", "3306"))
DB_NAME = os.getenv("AWS_RDS_NAME")
DB_USER = os.getenv("AWS_RDS_USERNAME")
DB_PASSWORD = os.getenv("AWS_RDS_PASSWORD")

required_vars = {
    'AWS_RDS_ENDPOINT': DB_HOST,
    'AWS_RDS_NAME': DB_NAME,
    'AWS_RDS_USERNAME': DB_USER,
    'AWS_RDS_PASSWORD': DB_PASSWORD
}
missing_vars = [key for key, val in required_vars.items() if not val]
if missing_vars:
    logger.error(f"Missing required environment variables: {missing_vars}")
    raise ValueError(f"Missing required environment variables: {missing_vars}")

#__________________ SQLAlchemy Engine and Session __________________
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger.info(f"Preparing SQLAlchemy engine for {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False,
        connect_args={
            "charset": "utf8mb4",
            "connect_timeout": 60,
            "read_timeout": 30,
            "write_timeout": 30,
            "autocommit": True
        }
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create engine: {str(e)}")
    raise

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
logger.info("Session factory initialized")

Base = declarative_base()
logger.info("Declarative base class set")

#__________________ Utility Functions __________________
def get_db():
    """Yields a new DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection() -> bool:
    """Ping database to confirm connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB ping failed: {e}")
        return False

def get_database_info() -> dict:
    """Collect metadata about current DB"""
    try:
        with engine.connect() as conn:
            db_name = conn.execute(text("SELECT DATABASE()")).scalar()
            tables = [row[0] for row in conn.execute(text("SHOW TABLES")).fetchall()]
            size = conn.execute(text(f"""
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
                FROM information_schema.tables 
                WHERE table_schema = '{DB_NAME}'
            """)).scalar()
            return {
                "database": db_name,
                "tables": tables,
                "size_mb": size or 0,
                "connection_successful": True
            }
    except Exception as e:
        logger.error(f"get_database_info failed: {e}")
        return {
            "database": None,
            "tables": [],
            "size_mb": 0,
            "connection_successful": False
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