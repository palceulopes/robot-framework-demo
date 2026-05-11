"""
REST client for the Vehicle Service (mock ECU-style HTTP API).

Keywords keep ECU-oriented names (Get Ecu Signal, etc.) for stable Robot resources.

Example:
    *** Settings ***
    Library    libraries.rest_vehicle_service_api    base_url=http://localhost:8765

    *** Test Cases ***
    Query Vehicle Speed
        ${speed}=    Get Ecu Signal    speed
        Should Be Equal As Numbers    ${speed}    120
"""

import logging
from typing import Any, Dict, Optional

from robot.api.deco import library

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    requests = None


@library(scope="SUITE", version="1.0.0", auto_keywords=True)
class RestVehicleServiceApi:
    """HTTP client for Vehicle Service REST endpoints (signals, diagnostics, health)."""

    ENDPOINTS = {
        "speed": "/api/signals/speed",
        "rpm": "/api/signals/rpm",
        "temperature": "/api/signals/temperature",
        "fuel": "/api/signals/fuel_level",
        "voltage": "/api/diagnostics/voltage",
        "errors": "/api/diagnostics/errors",
        "version": "/api/system/version",
        "status": "/api/system/status",
    }

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8765",
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
        self.max_retries = max_retries

        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.last_response: Optional[requests.Response] = None

        self.logger.info("REST Vehicle Service client initialized: %s", self.base_url)

    def _build_url(self, endpoint: str) -> str:
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return f"{self.base_url}{endpoint}"

    def _log_request(self, method: str, url: str, **kwargs) -> None:
        self.logger.debug("%s %s", method, url)

    def get_ecu_signal(self, signal_name: str) -> Any:
        try:
            endpoint = self.ENDPOINTS.get(signal_name, f"/api/signals/{signal_name}")
            url = self._build_url(endpoint)

            self._log_request("GET", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            self.last_response = response
            data = response.json()

            value = data.get("value")
            self.logger.info("Got %s: %s", signal_name, value)
            return value

        except requests.RequestException as e:
            self.logger.error("Failed to get signal %s: %s", signal_name, e)
            raise RuntimeError(f"Vehicle Service API error: {e}") from e

    def get_ecu_status(self) -> Dict[str, Any]:
        try:
            url = self._build_url(self.ENDPOINTS["status"])
            self._log_request("GET", url)

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            self.last_response = response
            return response.json()

        except requests.RequestException as e:
            self.logger.error("Failed to get status: %s", e)
            raise RuntimeError(f"Vehicle Service API error: {e}") from e

    def get_ecu_version(self) -> str:
        try:
            url = self._build_url(self.ENDPOINTS["version"])
            self._log_request("GET", url)

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            self.last_response = response
            data = response.json()
            version = data.get("version", "unknown")

            self.logger.info("Vehicle Service version: %s", version)
            return version

        except requests.RequestException as e:
            self.logger.error("Failed to get version: %s", e)
            raise RuntimeError(f"Vehicle Service API error: {e}") from e

    def get_diagnostics(self) -> Dict[str, Any]:
        try:
            url = self._build_url(self.ENDPOINTS["errors"])
            self._log_request("GET", url)

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            self.last_response = response
            return response.json()

        except requests.RequestException as e:
            self.logger.error("Failed to get diagnostics: %s", e)
            raise RuntimeError(f"Vehicle Service API error: {e}") from e

    def set_ecu_parameter(self, parameter: str, value: Any) -> bool:
        try:
            url = self._build_url(f"/api/config/{parameter}")
            payload = {"value": value}

            self._log_request("POST", url, json=payload)
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            self.last_response = response
            self.logger.info("Set %s = %s", parameter, value)
            return True

        except requests.RequestException as e:
            self.logger.error("Failed to set parameter: %s", e)
            return False

    def send_ecu_command(self, command: str, **kwargs) -> Dict[str, Any]:
        try:
            url = self._build_url(f"/api/commands/{command}")

            self._log_request("POST", url, json=kwargs)
            response = self.session.post(url, json=kwargs, timeout=self.timeout)
            response.raise_for_status()

            self.last_response = response
            return response.json()

        except requests.RequestException as e:
            self.logger.error("Failed to send command: %s", e)
            raise RuntimeError(f"Vehicle Service API error: {e}") from e

    def check_ecu_connectivity(self) -> bool:
        try:
            url = self._build_url("/api/health")
            self._log_request("GET", url)

            response = self.session.get(url, timeout=self.timeout)
            self.last_response = response

            is_healthy = response.status_code == 200
            self.logger.info("Vehicle Service health: %s", "OK" if is_healthy else "FAILED")
            return is_healthy

        except requests.RequestException:
            self.logger.warning("Vehicle Service not reachable")
            return False
