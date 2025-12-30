from typing import Any
import httpx

from app.core.config import get_settings


class PhraseTmsClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.TMS_BASE_URL.rstrip("/")
        self.api_token = self.settings.TMS_API_TOKEN

    def create_job(
        self,
        project_id: str,
        source_locale: str,
        target_locales: list[str],
        content: dict[str, Any],
    ) -> str:
        """
        Create a job in Phrase.
        Returns the TMS job UID.
        """

        url = f"{self.base_url}/web/api2/v1/projects/{project_id}/jobs"

        headers = {
            "Authorization": f"ApiToken {self.api_token}",
            "Content-Type": "application/json",
        }

        #  Simplified payload for demo purposes
        payload = {
            "jobs": [
                {
                    "fileName": "content.json",
                    "targetLangs": target_locales,
                    "content": content,
                }
            ]
        }

        try:
            response = httpx.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.settings.HTTP_TIMEOUT,
            )
        except httpx.RequestError as exc:
            raise RuntimeError(f"TMS request failed: {exc}") from exc

        if response.status_code >= 400:
            raise RuntimeError(
                f"TMS error {response.status_code}: {response.text}"
            )

        data = response.json()

        # Phrase typically returns an array of jobs
        # We store the first job UID
        try:
            return data["jobs"][0]["uid"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected TMS response: {data}")
