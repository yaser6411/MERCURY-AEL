"""Process isolation and sandboxing for candidate execution."""
import subprocess
import tempfile
import shutil
import os
import time
from pathlib import Path
from typing import Optional

from core.data_structures import Candidate, ExecutionResult
from core.evolution_logger import EvolutionLogger


class Sandbox:
    """Executes candidate code in isolated environment."""

    def __init__(self, config: dict, logger: EvolutionLogger = None):
        self.config = config
        self.logger = logger or EvolutionLogger()
        self.sandbox_dir = Path(tempfile.gettempdir()) / 'mercury-sandbox'
        self.sandbox_dir.mkdir(exist_ok=True)

    def run_candidate(self, candidate: Candidate, test_harness: str = None, timeout_sec: int = None) -> ExecutionResult:
        """Execute candidate in isolated sandbox.
        
        Args:
            candidate: Candidate to execute
            test_harness: Test harness code to run against candidate
            timeout_sec: Execution timeout in seconds
            
        Returns:
            ExecutionResult with stdout, stderr, returncode
        """
        result = ExecutionResult()
        timeout_sec = timeout_sec or self.config.get('limits', {}).get('sandbox_timeout_sec', 60)
        
        # Create temporary execution directory
        exec_dir = self.sandbox_dir / f"exec_{int(time.time() * 1000)}"
        exec_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Write candidate to temp file
            candidate_path = exec_dir / 'candidate.py'
            with open(candidate_path, 'w') as f:
                f.write(candidate.source_code)
            
            # Write test harness if provided
            if test_harness:
                harness_path = exec_dir / 'test.py'
                with open(harness_path, 'w') as f:
                    f.write(test_harness)
                script_to_run = harness_path
            else:
                script_to_run = candidate_path
            
            # Execute with timeout
            start_time = time.time()
            
            try:
                process = subprocess.Popen(
                    ['python3', str(script_to_run)],
                    cwd=str(exec_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout_sec,
                    text=True
                )
                stdout, stderr = process.communicate(timeout=timeout_sec)
                
                result.returncode = process.returncode
                result.stdout = stdout[:10000]  # Truncate large outputs
                result.stderr = stderr[:10000]
                result.success = process.returncode == 0
                result.execution_time_ms = (time.time() - start_time) * 1000
                
            except subprocess.TimeoutExpired:
                process.kill()
                result.success = False
                result.stderr = f"Timeout after {timeout_sec}s"
                result.returncode = -1
                result.execution_time_ms = timeout_sec * 1000
                self.logger.warning(f"Candidate {candidate.hash[:8]} execution timed out")
            
        except Exception as e:
            result.success = False
            result.stderr = str(e)
            result.returncode = -1
            self.logger.error(f"Sandbox execution error: {e}")
        
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(exec_dir)
            except Exception as e:
                self.logger.debug(f"Cleanup error: {e}")
        
        return result

    def cleanup(self):
        """Clean up all sandbox directories."""
        try:
            if self.sandbox_dir.exists():
                shutil.rmtree(self.sandbox_dir)
        except Exception as e:
            self.logger.warning(f"Sandbox cleanup failed: {e}")
