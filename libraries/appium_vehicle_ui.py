"""
Optional Appium-based UI helpers for Android automotive HMI tests.

Install: uv sync --extra ui  (requires Appium server + emulator/device outside this package)

This module stays minimal so core framework installs stay lightweight.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AppiumVehicleUi:
    """Thin Robot library around Appium WebDriver (optional dependency)."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = "1.0.0"

    def __init__(self, command_executor: str = "http://127.0.0.1:4723"):
        try:
            from appium import webdriver  # type: ignore
            from appium.options.android import UiAutomator2Options  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "Appium client not installed. Install optional UI extras: uv sync --extra ui"
            ) from e

        self._options_cls = UiAutomator2Options
        self.command_executor = command_executor
        self.driver: Optional[Any] = None

    def open_android_session(self, app_package: str, app_activity: str, **caps: Any) -> None:
        """Start UiAutomator2 session (provide platformVersion/deviceName via caps if needed)."""
        opts = self._options_cls()
        opts.platform_name = caps.get("platform_name", "Android")
        opts.app_package = app_package
        opts.app_activity = app_activity
        if "device_name" in caps:
            opts.device_name = caps["device_name"]
        if "platform_version" in caps:
            opts.platform_version = caps["platform_version"]

        self.driver = webdriver.Remote(self.command_executor, options=opts)
        logger.info("Appium session started for %s/%s", app_package, app_activity)

    def quit_session(self) -> None:
        """Close Appium session."""
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def tap_text(self, text: str, timeout_s: int = 10) -> None:
        """Tap first visible element containing text (UiAutomator2)."""
        from selenium.webdriver.common.by import By

        if self.driver is None:
            raise RuntimeError("No active session")
        el = self.driver.find_element(
            By.XPATH,
            f'//*[contains(@text, "{text}")]',
        )
        el.click()

    def get_ui_dump_summary(self) -> Dict[str, Any]:
        """Return lightweight session info for logging."""
        if self.driver is None:
            return {"session": None}
        caps = getattr(self.driver, "capabilities", {}) or {}
        return {"session_id": caps.get("sessionId"), "platform": caps.get("platformName")}
