from typing import List, Optional
from domain.entities import Branch
from domain.interfaces import IBranchRepository
from core.helpers.exceptions_helper import (
    ServiceException,
    ValidationServiceException,
    InfrastructureServiceException,
)


class BranchService:
    def __init__(self, branch_repo: IBranchRepository):
        try:
            self.branch_repo = branch_repo
        except Exception as e:
            raise InfrastructureServiceException("Failed to initialize branch service") from e

    async def create_branch(self, branch_data: dict) -> Branch:
        try:
            branch = Branch.model_validate(branch_data)
            return await self.branch_repo.create(branch)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to create branch") from e

    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        try:
            return await self.branch_repo.get_by_id(branch_id)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to fetch branch") from e

    async def list_branches(self) -> List[Branch]:
        try:
            return await self.branch_repo.list_all()
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to list branches") from e

    async def update_branch(
        self, branch_id: int, branch_data: dict
    ) -> Optional[Branch]:
        try:
            return await self.branch_repo.update(branch_id, branch_data)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to update branch") from e

    async def delete_branch(self, branch_id: int) -> bool:
        try:
            return await self.branch_repo.delete(branch_id)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to delete branch") from e
