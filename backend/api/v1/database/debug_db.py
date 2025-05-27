#!/usr/bin/env python3
"""
Debug script to test database connection independently
Run this to diagnose connection issues before starting FastAPI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

def test_env_loading():
    """Test environment variable loading"""
    print("=== Testing Environment Variable Loading ===")
    
    # Try to find .env file
    backend_dir = Path(__file__).parent.parent.parent.parent
    env_path = backend_dir / '.env'
    
    print(f"Looking for .env at: {env_path}")
    print(f".env exists: {env_path.exists()}")
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from: {env_path}")
    else:
        print("Trying to load .env from current directory...")
        load_dotenv()
    
    # Check environment variables
    required_vars = ['AWS_RDS_ENDPOINT', 'AWS_RDS_PORT', 'AWS_RDS_NAME', 'AWS_RDS_USERNAME', 'AWS_RDS_PASSWORD']
    
    print("\n=== Environment Variables ===")
    for var in required_vars:
        value = os.getenv(var)
        if var == 'AWS_RDS_PASSWORD':
            print(f"{var}: {'*' * len(value) if value else 'None'}")
        else:
            print(f"{var}: {value}")
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"\n❌ Missing variables: {missing}")
        return False
    else:
        print("\n✅ All environment variables loaded")
        return True

def test_raw_mysql_connection():
    """Test raw MySQL connection using mysql-connector-python"""
    print("\n=== Testing Raw MySQL Connection ===")
    
    DB_HOST = os.getenv("AWS_RDS_ENDPOINT")
    DB_PORT = int(os.getenv("AWS_RDS_PORT", "3306"))
    DB_NAME = os.getenv("AWS_RDS_NAME")
    DB_USER = os.getenv("AWS_RDS_USERNAME")
    DB_PASSWORD = os.getenv("AWS_RDS_PASSWORD")
    
    try:
        print(f"Connecting to: {DB_USER}@{DB_HOST}:{DB_PORT}")
        
        # Test connection without database first
        print("Step 1: Connecting to MySQL server...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connection_timeout=10
        )
        
        if conn.is_connected():
            print("✅ Connected to MySQL server successfully")
            cursor = conn.cursor()
            
            # Check if database exists
            print(f"Step 2: Checking if database '{DB_NAME}' exists...")
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            print(f"Available databases: {databases}")
            
            if DB_NAME in databases:
                print(f"✅ Database '{DB_NAME}' exists")
                
                # Try to connect to specific database
                cursor.close()
                conn.close()
                
                print(f"Step 3: Connecting to database '{DB_NAME}'...")
                conn = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    port=DB_PORT,
                    database=DB_NAME,
                    connection_timeout=10
                )
                
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"✅ Successfully connected to database '{DB_NAME}'")
                
                # Show tables
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                print(f"Tables in database: {tables}")
                
                cursor.close()
                conn.close()
                return True
                
            else:
                print(f"❌ Database '{DB_NAME}' does not exist")
                print("Available databases:", databases)
                cursor.close()
                conn.close()
                return False
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Access denied: Check username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ Database does not exist")
        else:
            print(f"❌ MySQL Error: {err}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\n=== Testing SQLAlchemy Connection ===")
    
    try:
        from sqlalchemy import create_engine, text
        
        DB_HOST = os.getenv("AWS_RDS_ENDPOINT")
        DB_PORT = os.getenv("AWS_RDS_PORT", "3306")
        DB_NAME = os.getenv("AWS_RDS_NAME")
        DB_USER = os.getenv("AWS_RDS_USERNAME")
        DB_PASSWORD = os.getenv("AWS_RDS_PASSWORD")
        
        SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"SQLAlchemy URL: mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,
            connect_args={
                "charset": "utf8mb4",
                "connect_timeout": 10,
            }
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ SQLAlchemy connection successful")
            return True
            
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def main():
    """Main debug function"""
    print("🔍 Database Connection Debug Tool")
    print("=" * 50)
    
    # Test 1: Environment variables
    if not test_env_loading():
        print("\n❌ Environment variable test failed. Fix .env file first.")
        sys.exit(1)
    
    # Test 2: Raw MySQL connection
    if not test_raw_mysql_connection():
        print("\n❌ Raw MySQL connection failed.")
        sys.exit(1)
    
    # Test 3: SQLAlchemy connection
    if not test_sqlalchemy_connection():
        print("\n❌ SQLAlchemy connection failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Database connection should work.")

if __name__ == "__main__":
    main()