"""
Automotive Listener for Robot Framework.

Custom listener that captures test metrics for automotive testing:
- Signal injection counts
- API call statistics
- Performance metrics
- Test execution details

Usage:
    robot --listener libraries.automotive_listener tests/
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class AutomotiveListener:
    """
    Robot Framework listener for automotive test metrics.
    
    Captures:
    - Test execution timing
    - Signal injection counts
    - API call statistics
    - Performance metrics
    - Pass/fail rates
    """
    
    # Listener API v2 (name + attrs) — stable with Robot Framework 7
    ROBOT_LISTENER_API_VERSION = 2
    
    def __init__(self, output_dir: str = "logs"):
        """Initialize listener."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Metrics storage
        self.test_metrics: List[Dict[str, Any]] = []
        self.suite_metrics: Dict[str, Any] = {}
        self.signal_count = 0
        self.api_call_count = 0
        self.alert_count = 0
        
        # Timing
        self.suite_start_time: Optional[float] = None
        self.test_start_time: Optional[float] = None
        
        # Current test info
        self.current_test_name = ""
        self.current_test_tags = []
        self.current_test_keywords = 0
        
        logger.info("AutomotiveListener initialized")
    
    def start_suite(self, name: str, attrs: Dict[str, Any]) -> None:
        """Called at suite start."""
        self.suite_start_time = time.time()
        
        self.suite_metrics = {
            "name": name,
            "start_time": datetime.now().isoformat(),
            "tests": 0,
            "passed": 0,
            "failed": 0,
        }
        
        logger.info(f"Suite started: {name}")
    
    def end_suite(self, name: str, attrs: Dict[str, Any]) -> None:
        """Called at suite end."""
        if self.suite_start_time:
            duration = time.time() - self.suite_start_time
        else:
            duration = 0
        
        # Update metrics
        stats = attrs.get("statistics", {})
        self.suite_metrics.update({
            "end_time": datetime.now().isoformat(),
            "duration_seconds": duration,
            "passed": stats.get("passed", 0),
            "failed": stats.get("failed", 0),
            "total": stats.get("total", 0),
            "status": attrs.get("status", "UNKNOWN"),
        })
        
        # Save metrics
        self._save_metrics()
        
        logger.info(
            f"Suite ended: {name} | "
            f"Duration: {duration:.2f}s | "
            f"Status: {self.suite_metrics['status']}"
        )
    
    def start_test(self, name: str, attrs: Dict[str, Any]) -> None:
        """Called at test start."""
        self.test_start_time = time.time()
        self.current_test_name = name
        self.current_test_tags = attrs.get("tags", [])
        self.current_test_keywords = 0
        
        logger.info(f"Test started: {name} | Tags: {self.current_test_tags}")
    
    def end_test(self, name: str, attrs: Dict[str, Any]) -> None:
        """Called at test end."""
        if self.test_start_time:
            duration = time.time() - self.test_start_time
        else:
            duration = 0
        
        status = attrs.get("status", "UNKNOWN")
        
        # Record test metric
        test_metric = {
            "name": name,
            "status": status,
            "duration_seconds": duration,
            "tags": self.current_test_tags,
            "timestamp": datetime.now().isoformat(),
            "keywords_executed": self.current_test_keywords,
        }
        
        self.test_metrics.append(test_metric)
        
        # Update counters
        if status == "PASS":
            self.suite_metrics["passed"] = self.suite_metrics.get("passed", 0) + 1
        else:
            self.suite_metrics["failed"] = self.suite_metrics.get("failed", 0) + 1
        
        logger.info(
            f"Test ended: {name} | "
            f"Status: {status} | "
            f"Duration: {duration:.2f}s"
        )
    
    def start_keyword(self, name: str, attrs: Dict[str, Any]) -> None:
        """Called at keyword start."""
        self.current_test_keywords += 1
        
        # Count automotive-specific keywords
        if "signal" in name.lower() or "inject" in name.lower():
            self.signal_count += 1
        elif "api" in name.lower() or "ecu" in name.lower():
            self.api_call_count += 1
        elif "alert" in name.lower():
            self.alert_count += 1
    
    def end_keyword(self, name: str, attrs: Dict[str, Any]) -> None:
        """Called at keyword end."""
        status = attrs.get("status", "UNKNOWN")
        if status != "PASS":
            logger.warning(f"Keyword failed: {name}")
    
    def log_message(self, message: Dict[str, Any]) -> None:
        """Called when a log message is written."""
        # Can be used to capture specific log patterns
        level = message.get("level", "")
        text = message.get("message", "")
        
        if "SIGNAL" in text.upper():
            pass  # Already counted in start_keyword
    
    def _save_metrics(self) -> None:
        """Save metrics to JSON file."""
        try:
            output_file = self.output_dir / "automotive_metrics.json"
            
            metrics_data = {
                "suite": self.suite_metrics,
                "tests": self.test_metrics,
                "aggregated": {
                    "total_signal_injections": self.signal_count,
                    "total_api_calls": self.api_call_count,
                    "total_alerts": self.alert_count,
                    "total_tests": len(self.test_metrics),
                    "total_passed": sum(1 for t in self.test_metrics if t["status"] == "PASS"),
                    "total_failed": sum(1 for t in self.test_metrics if t["status"] == "FAIL"),
                    "timestamp": datetime.now().isoformat(),
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info(f"Metrics saved to {output_file}")
            
            # Also save CSV for easy viewing
            self._save_metrics_csv(output_file)
        
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _save_metrics_csv(self, json_file: Path) -> None:
        """Save metrics to CSV format."""
        try:
            import csv
            
            csv_file = self.output_dir / "automotive_metrics.csv"
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "test_name",
                        "status",
                        "duration_seconds",
                        "tags",
                        "timestamp",
                        "keywords_executed",
                    ]
                )
                writer.writeheader()
                
                for test_metric in self.test_metrics:
                    writer.writerow({
                        "test_name": test_metric["name"],
                        "status": test_metric["status"],
                        "duration_seconds": f"{test_metric['duration_seconds']:.2f}",
                        "tags": ",".join(test_metric["tags"]),
                        "timestamp": test_metric["timestamp"],
                        "keywords_executed": test_metric["keywords_executed"],
                    })
            
            logger.info(f"CSV metrics saved to {csv_file}")
        
        except Exception as e:
            logger.warning(f"Failed to save CSV metrics: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "suite": self.suite_metrics,
            "tests_executed": len(self.test_metrics),
            "tests_passed": sum(1 for t in self.test_metrics if t["status"] == "PASS"),
            "tests_failed": sum(1 for t in self.test_metrics if t["status"] == "FAIL"),
            "signal_injections": self.signal_count,
            "api_calls": self.api_call_count,
            "alerts": self.alert_count,
        }
