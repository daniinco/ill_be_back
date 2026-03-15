from dataclasses import dataclass
from typing import Mapping, Any
from clients.postgres import get_pg_connection
from observability.metrics import DB_QUERY_DURATION_SECONDS
import time

@dataclass(frozen=True)
class UserPostgresStorage:
    async def create(self, name: str, is_verified: bool) -> Mapping[str, Any]:
        query = '''
            INSERT INTO users (name, is_verified)
            VALUES ($1, $2)
            RETURNING *
        '''

        start_time = time.time()
        try:
            async with get_pg_connection() as connection:
                return dict(await connection.fetchrow(query, name, is_verified))
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION_SECONDS.labels(query_type="insert").observe(duration)
    
    async def select(self, id: int) -> Mapping[str, Any]:
        query = '''
            SELECT *
            FROM users
            WHERE id = $1::INTEGER
            LIMIT 1
        '''

        start_time = time.time()
        try:
            async with get_pg_connection() as connection:
                row = await connection.fetchrow(query, id)

                if row:
                    return dict(row)
                
                return None
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION_SECONDS.labels(query_type="select").observe(duration)
    
    async def delete(self, id: int) -> bool:
        query = '''
            DELETE FROM users
            WHERE id = $1::INTEGER
            RETURNING *
        '''

        start_time = time.time()
        try:
            async with get_pg_connection() as connection:
                row = await connection.fetchrow(query, id)
                return row is not None
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION_SECONDS.labels(query_type="delete").observe(duration)

@dataclass(frozen=True)
class UserRepository:
    user_postgres_storage: UserPostgresStorage = UserPostgresStorage()

    async def create_user(self, name: str, is_verified: bool) -> int:
        raw_user = await self.user_postgres_storage.create(name, is_verified)
        return raw_user['id']

    async def get_user(self, user_id: int) -> Mapping[str, Any]:
        return await self.user_postgres_storage.select(user_id)

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_postgres_storage.delete(user_id)