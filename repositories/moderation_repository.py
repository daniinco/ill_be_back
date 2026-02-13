from dataclasses import dataclass
from typing import Mapping, Any, Optional
from clients.postgres import get_pg_connection
from datetime import datetime

@dataclass(frozen=True)
class ModerationPostgresStorage:
    async def create(self, item_id: int) -> Mapping[str, Any]:
        query = '''
            INSERT INTO moderation_results 
            (item_id, status, created_at) 
            VALUES ($1, 'pending', CURRENT_TIMESTAMP) 
            RETURNING *
        '''
        
        async with get_pg_connection() as connection:
            return dict(await connection.fetchrow(query, item_id))
    
    async def select(self, task_id: int) -> Optional[Mapping[str, Any]]:
        query = '''
            SELECT id, item_id, status, is_violation, probability, 
                   error_message, created_at, processed_at
            FROM moderation_results
            WHERE id = $1::INTEGER
            LIMIT 1
        '''
        
        async with get_pg_connection() as connection:
            row = await connection.fetchrow(query, task_id)
            
            if row:
                return dict(row)
            
            return None
    
    async def update_completed(
        self, 
        task_id: int, 
        is_violation: bool, 
        probability: float
    ) -> bool:
        query = '''
            UPDATE moderation_results
            SET status = 'completed',
                is_violation = $2,
                probability = $3,
                processed_at = CURRENT_TIMESTAMP
            WHERE id = $1::INTEGER
            returning *
        '''
        
        async with get_pg_connection() as connection:
            row = await connection.fetchrow(query, task_id, is_violation, probability)
            return row is not None
    
    async def update_failed(self, task_id: int, error_message: str) -> bool:
        query = '''
            UPDATE moderation_results
            SET status = 'failed',
                error_message = $2,
                processed_at = CURRENT_TIMESTAMP
            WHERE id = $1::INTEGER
            returning *
        '''
        
        async with get_pg_connection() as connection:
            row = await connection.fetchrow(query, task_id, error_message)
            return row is not None

@dataclass(frozen=True)
class ModerationRepository:
    moderation_postgres_storage: ModerationPostgresStorage = ModerationPostgresStorage()
    
    async def create_moderation_task(self, item_id: int) -> int:
        raw_task = await self.moderation_postgres_storage.create(item_id)
        return raw_task['id']
    
    async def get_moderation_task(self, task_id: int) -> Optional[Mapping[str, Any]]:
        return await self.moderation_postgres_storage.select(task_id)
    
    async def mark_completed(
        self, 
        task_id: int, 
        is_violation: bool, 
        probability: float
    ) -> bool:
        return await self.moderation_postgres_storage.update_completed(
            task_id, is_violation, probability
        )
    
    async def mark_failed(self, task_id: int, error_message: str) -> bool:
        return await self.moderation_postgres_storage.update_failed(task_id, error_message)