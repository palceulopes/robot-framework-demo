"""
REST ECU API Library for Robot Framework.

Provides keywords for testing ECU communication via REST/HTTP API.
Simulates ECU endpoints for diagnostics, configuration, and status queries.

Example:
    *** Settings ***
    Library    libraries.rest_ecu_api    base_url=http://localhost:5000
    
    *** Test Cases ***
    Query ECU Speed
        ${speed}=    Get ECU Signal    speed
        Should Be Equal As Numbers    ${speed}    120
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from robot.api.deco import library

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


@library(scope="SUITE", version="1.0.0", auto_keywords=True)
class RestEcuApi:
    """
    REST API client for ECU communication testing.
    
    Provides:
    - ECU signal queries via REST
    - Configuration commands
    - Diagnostics data retrieval
    - Error handling and retries
    - Request/response logging
    """
    
    # Standard ECU endpoints
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
        """
        Initialize REST ECU API client.
        
        Args:
            base_url: Base URL of ECU API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if requests is None:
            raise RuntimeError(
                "requests not installed. Install with: pip install requests"
            )
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create session with retry strategy
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
        self.request_history: List[Dict[str, Any]] = []
        
        self.logger.info(f"REST ECU API initialized: {self.base_url}")
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        return f"{self.base_url}{endpoint}"
    
    def _log_request(self, method: str, url: str, **kwargs) -> None:
        """Log HTTP request."""
        self.request_history.append({
            "timestamp": time.time(),
            "method": method,
            "url": url,
            "kwargs": kwargs,
        })
        self.logger.debug(f"{method} {url}")
    
    def get_ecu_signal(self, signal_name: str) -> Any:
        """
        Get a signal value from ECU.
        
        Args:
            signal_name: Signal name (speed, rpm, temperature, etc.)
            
        Returns:
            Signal value
            
        Raises:
            RuntimeError: If request fails
        """
        try:
            endpoint = self.ENDPOINTS.get(signal_name, f"/api/signals/{signal_name}")
            url = self._build_url(endpoint)
            
            self._log_request("GET", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_response = response
            data = response.json()
            
            value = data.get("value")
            self.logger.info(f"Got {signal_name}: {value}")
            return value
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to get signal {signal_name}: {e}")
            raise RuntimeError(f"ECU API error: {e}")
    
    def get_ecu_status(self) -> Dict[str, Any]:
        """
        Get ECU system status.
        
        Returns:
            Status dictionary
        """
        try:
            url = self._build_url(self.ENDPOINTS["status"])
            self._log_request("GET", url)
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_response = response
            return response.json()
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to get ECU status: {e}")
            raise RuntimeError(f"ECU API error: {e}")
    
    def get_ecu_version(self) -> str:
        """Get ECU software version."""
        try:
            url = self._build_url(self.ENDPOINTS["version"])
            self._log_request("GET", url)
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_response = response
            data = response.json()
            version = data.get("version", "unknown")
            
            self.logger.info(f"ECU version: {version}")
            return version
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to get ECU version: {e}")
            raise RuntimeError(f"ECU API error: {e}")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get ECU diagnostic data."""
        try:
            url = self._build_url(self.ENDPOINTS["errors"])
            self._log_request("GET", url)
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_response = response
            return response.json()
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to get diagnostics: {e}")
            raise RuntimeError(f"ECU API error: {e}")
    
    def set_ecu_parameter(self, parameter: str, value: Any) -> bool:
        """
        Set an ECU parameter.
        
        Args:
            parameter: Parameter name
            value: Parameter value
            
        Returns:
            True if successful
        """
        try:
            url = self._build_url(f"/api/config/{parameter}")
            payload = {"value": value}
            
            self._log_request("POST", url, json=payload)
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_response = response
            self.logger.info(f"Set {parameter} = {value}")
            return True
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to set parameter: {e}")
            return False
    
    def send_ecu_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Send a command to ECU.
        
        Args:
            command: Command name
            **kwargs: Command parameters
            
        Returns:
            Response from ECU
        """
        try:
            url = self._build_url(f"/api/commands/{command}")
            
            self._log_request("POST", url, json=kwargs)
            response = self.session.post(url, json=kwargs, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_response = response
            return response.json()
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to send command: {e}")
            raise RuntimeError(f"ECU API error: {e}")
    
    def check_ecu_connectivity(self) -> bool:
        """Check if ECU is reachable."""
        try:
            url = self._build_url("/api/health")
            self._log_request("GET", url)
            
            response = self.session.get(url, timeout=self.timeout)
            self.last_response = response
            
            is_healthy = response.status_code == 200
            self.logger.info(f"ECU health check: {'OK' if is_healthy else 'FAILED'}")
            return is_healthy
        
        except requests.RequestException:
            self.logger.warning("ECU not reachable")
            return False
    
    def get_response_status(self) -> int:
        """Get last response HTTP status code."""
        return self.last_response.status_code if self.last_response else None
    
    def get_response_body(self) -> str:
        """Get last response body."""
        return self.last_response.text if self.last_response else None
    
    def get_request_count(self) -> int:
        """Get total requests made."""
        return len(self.request_history)
    
    def clear_history(self) -> None:
        """Clear request history."""
        self.request_history = []
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get overall API client status."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "request_count": self.get_request_count(),
            "last_response_status": self.get_response_status(),
            "connected": self.check_ecu_connectivity(),
        }
