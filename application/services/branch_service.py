from typing import List, Optional
from domain.entities import Branch
from domain.interfaces import IBranchRepository


class BranchService:
    def __init__(self, branch_repo: IBranchRepository):
        self.branch_repo = branch_repo

    async def create_branch(self, branch_data: dict) -> Branch:
        branch = Branch.model_validate(branch_data)
        return await self.branch_repo.create(branch)

    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        return await self.branch_repo.get_by_id(branch_id)

    async def list_branches(self) -> List[Branch]:
        return await self.branch_repo.list_all()

    async def update_branch(
        self, branch_id: int, branch_data: dict
    ) -> Optional[Branch]:
        return await self.branch_repo.update(branch_id, branch_data)

    async def delete_branch(self, branch_id: int) -> bool:
        return await self.branch_repo.delete(branch_id)
