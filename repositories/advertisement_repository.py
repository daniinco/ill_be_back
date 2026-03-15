from dataclasses import dataclass
from typing import Mapping, Any
from clients.postgres import get_pg_connection
from observability.metrics import DB_QUERY_DURATION_SECONDS
import time

@dataclass(frozen=True)
class AdvertisementPostgresStorage:
    async def create(
        self,
        user_id: int,
        item_id: int,
        name: str,
        description: str,
        category: int,
        images_qty: int
    ) -> Mapping[str, Any]:
        query = '''
            INSERT INTO advertisements 
            (user_id, item_id, name, description, category, images_qty) 
            VALUES ($1, $2, $3, $4, $5, $6) 
            RETURNING *
        '''

        start_time = time.time()
        try:
            async with get_pg_connection() as connection:
                return dict(await connection.fetchrow(
                    query, user_id, item_id, name, description, category, images_qty
                ))
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION_SECONDS.labels(query_type="insert").observe(duration)
    
    async def select(self, id: int) -> Mapping[str, Any]:
        query = '''
            SELECT a.id, a.user_id, a.item_id, a.name, a.description, 
            a.category, a.images_qty, u.is_verified
            FROM advertisements a
            JOIN users u 
            ON a.user_id = u.id
            WHERE a.id = $1::INTEGER
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
            DELETE FROM advertisements
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
class AdvertisementRepository:
    advertisement_postgres_storage: AdvertisementPostgresStorage = AdvertisementPostgresStorage()

    async def create_advertisement(
        self,
        user_id: int,
        item_id: int,
        name: str,
        description: str,
        category: int,
        images_qty: int
    ) -> int:
        raw_ad = await self.advertisement_postgres_storage.create(
            user_id, item_id, name, description, category, images_qty
        )
        return raw_ad['id']

    async def get_advertisement(self, ad_id: int) -> Mapping[str, Any]:
        return await self.advertisement_postgres_storage.select(ad_id)

    async def delete_advertisement(self, ad_id: int) -> bool:
        return await self.advertisement_postgres_storage.delete(ad_id)