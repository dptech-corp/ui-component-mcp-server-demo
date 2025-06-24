"""Database configuration and initialization."""

import aiomysql
import os
from typing import Optional


class Database:
    """MySQL database manager with connection pooling."""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self):
        """Connect to the database and create connection pool."""
        mysql_host = os.getenv("MYSQL_HOST", "mysql")
        mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        mysql_database = os.getenv("MYSQL_DATABASE")
        
        print(f"DEBUG: Connecting to database with host={mysql_host}, port={mysql_port}, user={mysql_user}, db={mysql_database}")
        print(f"DEBUG: Password is {'set' if mysql_password else 'NOT SET'}")
        
        try:
            self.pool = await aiomysql.create_pool(
                host=mysql_host,
                port=mysql_port,
                user=mysql_user,
                password=mysql_password,
                db=mysql_database,
                minsize=5,
                maxsize=20,
                autocommit=False
            )
            print(f"DEBUG: Database pool created successfully, pool is None: {self.pool is None}")
            
            await self.create_tables()
            print("DEBUG: Database tables created successfully")
        except Exception as e:
            print(f"DEBUG: Database connection failed: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from the database."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
    
    async def create_tables(self):
        """Create the todos, backlog, and approvals tables if they don't exist."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS todos (
                        id VARCHAR(36) PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at BIGINT NOT NULL,
                        updated_at BIGINT NOT NULL
                    )
                """)
                
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backlog (
                        id VARCHAR(36) PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        created_at BIGINT NOT NULL,
                        updated_at BIGINT NOT NULL
                    )
                """)
                
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS approvals (
                        id VARCHAR(36) PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL,
                        function_call_id VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at BIGINT NOT NULL,
                        updated_at BIGINT NOT NULL
                    )
                """)
                await conn.commit()
    
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self.pool:
            await self.connect()
        return self.pool.acquire()


database = Database()
