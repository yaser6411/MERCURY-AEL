"""Benchmark suite for performance measurement."""
import time
import psutil
from typing import List, Dict, Optional

from core.data_structures import Candidate, BenchmarkResult
from core.sandbox import Sandbox
from core.evolution_logger import EvolutionLogger


class Benchmark:
    """Runs performance benchmarks on candidates."""

    def __init__(self, config: Dict, sandbox: Optional[Sandbox] = None, logger: EvolutionLogger = None):
        self.config = config
        self.sandbox = sandbox or Sandbox(config, logger)
        self.logger = logger or EvolutionLogger()

    def run_benchmark(self, candidate: Candidate, test_harness: str = None, 
                     num_iterations: int = 3) -> BenchmarkResult:
        """Run candidate through benchmark suite.
        
        Args:
            candidate: Candidate to benchmark
            test_harness: Test code to execute
            num_iterations: Number of iterations to run
            
        Returns:
            BenchmarkResult with metrics
        """
        result = BenchmarkResult()
        execution_times = []
        memory_peaks = []
        
        for i in range(num_iterations):
            try:
                # Measure memory before execution
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                
                # Execute
                start = time.time()
                exec_result = self.sandbox.run_candidate(candidate, test_harness)
                elapsed_ms = (time.time() - start) * 1000
                
                # Measure memory after execution
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                mem_used = max(0, mem_after - mem_before)
                
                if exec_result.success:
                    execution_times.append(elapsed_ms)
                    memory_peaks.append(mem_used)
                    result.passed = True
                else:
                    result.passed = False
                    self.logger.debug(f"Benchmark iteration {i+1} failed: {exec_result.stderr}")
            
            except Exception as e:
                result.passed = False
                self.logger.error(f"Benchmark error: {e}")
        
        # Calculate statistics
        if execution_times:
            result.execution_times = execution_times
            result.memory_peak_mb = max(memory_peaks) if memory_peaks else 0.0
            result.memory_avg_mb = sum(memory_peaks) / len(memory_peaks) if memory_peaks else 0.0
            
            # Calculate throughput (operations per second)
            avg_time = sum(execution_times) / len(execution_times)
            if avg_time > 0:
                result.throughput = 1000.0 / avg_time  # ops/sec
        
        return result
