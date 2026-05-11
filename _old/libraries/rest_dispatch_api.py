"""
REST Dispatch API Library for Robot Framework.

Client for the mock Dispatch Service (fleet / job orchestration).
"""

import logging
from typing import Any, Dict, List, Optional

from robot.api.deco import library

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    requests = None


@library(scope="SUITE", version="1.0.0", auto_keywords=True)
class RestDispatchApi:
    """HTTP client for Dispatch Service mock endpoints."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8766",
        timeout: int = 10,
        max_retries: int = 3,
    ):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        if requests is None:
            raise RuntimeError(
                "requests not installed. Install with: uv sync --extra automotive"
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.last_response: Optional[requests.Response] = None
        self.logger.info("REST Dispatch API initialized: %s", self.base_url)

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def check_dispatch_connectivity(self) -> bool:
        """GET /api/health — Dispatch Service reachable."""
        try:
            r = self.session.get(self._url("/api/health"), timeout=self.timeout)
            self.last_response = r
            ok = r.status_code == 200
            self.logger.info("Dispatch health: %s", "OK" if ok else "FAILED")
            return ok
        except requests.RequestException:
            self.logger.warning("Dispatch Service not reachable")
            return False

    def list_dispatch_jobs(self) -> List[Dict[str, Any]]:
        """GET /api/v1/dispatch/jobs — current job queue."""
        r = self.session.get(self._url("/api/v1/dispatch/jobs"), timeout=self.timeout)
        r.raise_for_status()
        self.last_response = r
        data = r.json()
        return list(data.get("jobs") or [])

    def create_dispatch_job(self, vehicle_id: str, command: str) -> Dict[str, Any]:
        """
        POST /api/v1/dispatch/jobs — assign command to vehicle (publishes to MQTT).

        Returns:
            Parsed JSON body (includes job and optional mqtt_topic).
        """
        payload = {"vehicle_id": vehicle_id, "command": command}
        r = self.session.post(
            self._url("/api/v1/dispatch/jobs"),
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        self.last_response = r
        return r.json()

    def get_fleet_status(self) -> Dict[str, Any]:
        """GET /api/v1/fleet/status — lightweight fleet counters."""
        r = self.session.get(self._url("/api/v1/fleet/status"), timeout=self.timeout)
        r.raise_for_status()
        self.last_response = r
        return r.json()
