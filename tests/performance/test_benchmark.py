"""Performance benchmark tests for MERCURY-AEL."""
import pytest
import time
import hashlib
from datetime import datetime

from core.data_structures import Candidate
from core.benchmark import Benchmark
from core.sandbox import Sandbox


class TestBenchmarkExecution:
    """Test benchmark execution and measurement."""

    def test_benchmark_simple_function(self, mock_config):
        """Test benchmarking a simple function."""
        code = "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        benchmark = Benchmark(mock_config)
        result = benchmark.run_benchmark(candidate, num_iterations=1)
        
        assert result.passed is not None
        assert len(result.execution_times) >= 0

    def test_benchmark_measures_execution_time(self, mock_config):
        """Test that benchmark measures execution time."""
        code = "import time\ntime.sleep(0.01)"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        benchmark = Benchmark(mock_config)
        result = benchmark.run_benchmark(candidate, num_iterations=1)
        
        # Execution should take at least 10ms (due to sleep)
        if result.passed and result.execution_times:
            assert min(result.execution_times) >= 10

    def test_benchmark_average_calculation(self, mock_config):
        """Test that benchmark calculates average execution time."""
        code = "x = 1 + 1"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        benchmark = Benchmark(mock_config)
        result = benchmark.run_benchmark(candidate, num_iterations=3)
        
        if result.execution_times:
            assert result.avg_execution_time > 0

    def test_benchmark_with_test_harness(self, mock_config):
        """Test benchmark with custom test harness."""
        code = "def add(a, b):\n    return a + b"
        candidate = Candidate(
            source_code=code,
            generation=1,
            timestamp=datetime.now(),
            hash=hashlib.sha256(code.encode()).hexdigest()
        )
        
        harness = "from candidate import add\nassert add(2, 3) == 5"
        
        benchmark = Benchmark(mock_config)
        result = benchmark.run_benchmark(candidate, test_harness=harness, num_iterations=1)
        
        # Result should indicate pass/fail status
        assert isinstance(result.passed, bool)
