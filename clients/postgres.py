import asyncpg
from typing import AsyncGenerator
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_pg_connection(
    user: str = 'postgres',
    password: str = 'postgres'
) -> AsyncGenerator[asyncpg.Connection, None]:
    connection: asyncpg.Connection = await asyncpg.connect(
        database='postgres',
        host='localhost',
        port=5432,
        user=user,
        password=password
    )

    yield connection

    await connection.close()