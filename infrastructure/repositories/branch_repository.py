import asyncpg
from typing import List, Optional
from domain.entities import Branch
from domain.interfaces import IBranchRepository

BRANCH_COLUMNS = "id, name, location, contact_info"


class SQLBranchRepository(IBranchRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def get_by_id(self, branch_id: int) -> Optional[Branch]:
        query = f"SELECT {BRANCH_COLUMNS} FROM branches WHERE id = $1"
        row = await self.connection.fetchrow(query, branch_id)
        if row:
            return Branch.model_validate(dict(row))
        return None

    async def list_all(self) -> List[Branch]:
        query = f"SELECT {BRANCH_COLUMNS} FROM branches ORDER BY name"
        rows = await self.connection.fetch(query)
        return [Branch.model_validate(dict(row)) for row in rows]

    async def create(self, branch: Branch) -> Branch:
        branch_dict = branch.model_dump(exclude={"id"})
        columns = ", ".join(branch_dict.keys())
        placeholders = ",埋".join([f"${i+1}" for i in range(len(branch_dict))])
        values = list(branch_dict.values())

        sql = f"INSERT INTO branches ({columns}) VALUES ({placeholders}) RETURNING {BRANCH_COLUMNS}"
        row = await self.connection.fetchrow(sql, *values)
        if not row:
            raise Exception("Failed to create branch")
        return Branch.model_validate(dict(row))

    async def update(self, branch_id: int, branch_data: dict) -> Optional[Branch]:
        if not branch_data:
            return await self.get_by_id(branch_id)

        branch_data.pop("id", None)
        set_clauses = [f"{k} = ${i+1}" for i, k in enumerate(branch_data.keys())]
        values = list(branch_data.values())
        
        idx = len(values) + 1
        sql = f"UPDATE branches SET {', '.join(set_clauses)} WHERE id = ${idx} RETURNING {BRANCH_COLUMNS}"
        values.append(branch_id)

        row = await self.connection.fetchrow(sql, *values)
        if row:
            return Branch.model_validate(dict(row))
        return None

    async def delete(self, branch_id: int) -> bool:
        query = "DELETE FROM branches WHERE id = $1"
        result = await self.connection.execute(query, branch_id)
        return result == "DELETE 1"
