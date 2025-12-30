from abc import ABC, abstractmethod
from typing import Any


class TmsClient(ABC):
    @abstractmethod
    def create_job(
        self,
        project_id: str,
        source_locale: str,
        target_locales: list[str],
        content: dict[str, Any],
    ) -> str:
        """
        Creates a job in the TMS.
        Returns TMS job ID.
        """
        pass
