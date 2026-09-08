"""Resource monitoring and enforcement for MERCURY-AEL."""
import psutil
import os
import time
from typing import Dict
from pathlib import Path

from core.evolution_logger import EvolutionLogger


class ResourceMonitor:
    """Tracks and enforces resource limits during campaign execution."""

    def __init__(self, config: Dict, logger: EvolutionLogger = None):
        self.config = config
        self.logger = logger or EvolutionLogger()
        self.limits = config.get('limits', {})
        self.process = psutil.Process()
        self.start_time = time.time()
        self.initial_disk_usage = self._get_disk_usage()

    def exceeded_limits(self) -> bool:
        """Check if any resource limit has been exceeded.
        
        Returns:
            True if any limit exceeded, False otherwise
        """
        # Check RAM
        ram_usage_mb = self.process.memory_info().rss / 1024 / 1024
        max_ram_mb = self.limits.get('max_ram_mb', 2048)
        if ram_usage_mb > max_ram_mb:
            self.logger.warning(f"RAM limit exceeded: {ram_usage_mb:.1f}MB > {max_ram_mb}MB")
            return True

        # Check CPU percent
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            max_cpu_percent = self.limits.get('max_cpu_percent', 50)
            if cpu_percent > max_cpu_percent:
                self.logger.warning(f"CPU limit exceeded: {cpu_percent:.1f}% > {max_cpu_percent}%")
                return True
        except Exception as e:
            self.logger.debug(f"CPU check failed: {e}")

        # Check execution time
        elapsed_sec = time.time() - self.start_time
        max_execution_sec = self.limits.get('max_execution_time_sec', 3600)
        if elapsed_sec > max_execution_sec:
            self.logger.warning(f"Campaign timeout: {elapsed_sec:.1f}s > {max_execution_sec}s")
            return True

        # Check disk usage
        current_disk_usage = self._get_disk_usage()
        disk_used_mb = (current_disk_usage - self.initial_disk_usage) / 1024 / 1024
        max_disk_mb = self.limits.get('max_disk_mb', 5120)
        if disk_used_mb > max_disk_mb:
            self.logger.warning(f"Disk limit exceeded: {disk_used_mb:.1f}MB > {max_disk_mb}MB")
            return True

        return False

    def within_limits(self, candidate_size_kb: float) -> bool:
        """Check if candidate itself exceeds size constraints.
        
        Args:
            candidate_size_kb: Size of candidate in KB
            
        Returns:
            True if within limits, False otherwise
        """
        max_size_kb = self.limits.get('max_candidate_size_kb', 512)
        return candidate_size_kb <= max_size_kb

    def get_resource_status(self) -> Dict:
        """Get current resource usage status.
        
        Returns:
            Dictionary with resource metrics
        """
        ram_usage_mb = self.process.memory_info().rss / 1024 / 1024
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
        except:
            cpu_percent = 0.0
        
        elapsed_sec = time.time() - self.start_time
        disk_used_mb = (self._get_disk_usage() - self.initial_disk_usage) / 1024 / 1024
        
        return {
            'ram_mb': ram_usage_mb,
            'ram_limit_mb': self.limits.get('max_ram_mb', 2048),
            'cpu_percent': cpu_percent,
            'cpu_limit_percent': self.limits.get('max_cpu_percent', 50),
            'elapsed_sec': elapsed_sec,
            'timeout_sec': self.limits.get('max_execution_time_sec', 3600),
            'disk_used_mb': disk_used_mb,
            'disk_limit_mb': self.limits.get('max_disk_mb', 5120)
        }

    def _get_disk_usage(self) -> float:
        """Get total disk usage of project directory in bytes.
        
        Returns:
            Total disk usage in bytes
        """
        total = 0
        project_root = Path.cwd()
        
        try:
            for dirpath, dirnames, filenames in os.walk(project_root):
                # Skip certain directories
                dirnames[:] = [d for d in dirnames if not d.startswith('.')]
                
                for filename in filenames:
                    try:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except Exception as e:
            self.logger.debug(f"Disk usage calculation failed: {e}")
        
        return total

    def log_resource_usage(self):
        """Log current resource usage."""
        status = self.get_resource_status()
        self.logger.info(
            f"Resources: RAM {status['ram_mb']:.0f}/{status['ram_limit_mb']}MB | "
            f"CPU {status['cpu_percent']:.1f}%/{status['cpu_limit_percent']}% | "
            f"Time {status['elapsed_sec']:.0f}s/{status['timeout_sec']}s | "
            f"Disk {status['disk_used_mb']:.0f}/{status['disk_limit_mb']}MB"
        )
