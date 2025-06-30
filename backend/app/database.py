"""Database configuration and initialization."""

import aiomysql
import os
from typing import Optional
from contextlib import asynccontextmanager


class Database:
    """MySQL database manager with connection pooling."""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        mysql_host = os.getenv("MYSQL_HOST", "localhost")
        mysql_port = os.getenv("MYSQL_PORT", "3306")
        mysql_database = os.getenv("MYSQL_DATABASE")
        
        if not mysql_user or not mysql_password or not mysql_database:
            raise ValueError("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables are required")
        
        self.database_url = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    
    async def connect(self):
        """Connect to the database and create connection pool."""
        if self.database_url.startswith("mysql://"):
            url_parts = self.database_url[8:].split("@")
            user_pass = url_parts[0].split(":")
            host_db = url_parts[1].split("/")
            host_port = host_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1]
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            database = host_db[1]
            
            self.pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=database,
                minsize=5,
                maxsize=20,
                autocommit=False
            )
            
            await self.create_tables()
    
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
                        id VARCHAR(255) PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL,
                        function_call_id VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at BIGINT NOT NULL,
                        updated_at BIGINT NOT NULL,
                        result TEXT,
                        INDEX idx_session_id (session_id),
                        INDEX idx_function_call_id (function_call_id),
                        INDEX idx_status (status)
                    )
                """)
                await conn.commit()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool.
        
        Returns an async context manager that yields a connection and automatically closes it.
        
        Usage:
            async with database.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(...)
                await conn.commit()
        """
        if not self.pool:
            await self.connect()
        
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            conn.close()


database = Database()
