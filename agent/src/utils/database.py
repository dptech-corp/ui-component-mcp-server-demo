"""Database configuration and initialization."""

import aiomysql
import os
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

class Database:
    """MySQL database manager with connection pooling."""
    
    def __init__(self):
        load_dotenv()
        MYSQL_USER = os.getenv("MYSQL_USER")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
        # 本地开发环境下使用 localhost，容器环境下可改回 mysql
        self.database_url = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@mysql:3306/{MYSQL_DATABASE}"
        self.pool: Optional[aiomysql.Pool] = None
        # self.database_url = os.getenv("DATABASE_URL", "mysql://demo:ui_password@localhost:3306/ui_component_db")
    
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
async def get_approval(approval_id: str) ->dict:
    """Get an approval request by ID."""
    async with database.get_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, session_id, function_call_id, description, status, created_at, updated_at, result FROM approvals WHERE id = %s",
                (approval_id,)
            )
            row = await cursor.fetchone()
            return {
                'status': row[4],
            }
